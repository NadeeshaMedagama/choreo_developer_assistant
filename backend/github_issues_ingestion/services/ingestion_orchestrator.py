"""
Ingestion Orchestrator Service.
Coordinates the entire ingestion workflow following SOLID principles.
"""

from typing import List, Dict, Any, Optional
import time
from datetime import datetime

from ..interfaces.issue_fetcher import IIssueFetcher
from ..interfaces.text_processor import ITextProcessor
from ..interfaces.chunker import IChunker
from ..interfaces.embedding_service import IEmbeddingService
from ..interfaces.vector_store import IVectorStore
from ..models.github_issue import GitHubIssue
from ..models.chunk import TextChunk


class IngestionOrchestrator:
    """
    Orchestrator for the entire GitHub issues ingestion workflow.
    Follows Dependency Inversion Principle - depends on abstractions, not concretions.
    """

    def __init__(
        self,
        issue_fetcher: IIssueFetcher,
        text_processor: ITextProcessor,
        chunker: IChunker,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStore,
        batch_size: int = 10
    ):
        """
        Initialize Ingestion Orchestrator.

        Args:
            issue_fetcher: Service for fetching GitHub issues
            text_processor: Service for processing text
            chunker: Service for chunking text
            embedding_service: Service for creating embeddings
            vector_store: Service for storing vectors
            batch_size: Number of chunks to process in each batch
        """
        self.issue_fetcher = issue_fetcher
        self.text_processor = text_processor
        self.chunker = chunker
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.batch_size = batch_size

        # Statistics
        self.stats = {
            "total_issues": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "new_issues": 0,
            "updated_issues": 0,
            "skipped_issues": 0,
            "start_time": None,
            "end_time": None,
            "errors": [],
        }

    def ingest_repository(
        self,
        owner: str,
        repo: str,
        state: str = "all",
        labels: Optional[List[str]] = None,
        since: Optional[str] = None,
        max_issues: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ingest all issues from a GitHub repository.

        Args:
            owner: Repository owner/organization
            repo: Repository name
            state: Issue state ('open', 'closed', 'all')
            labels: Filter by labels
            since: Only issues updated after this timestamp
            max_issues: Maximum number of issues to fetch

        Returns:
            Dictionary with ingestion statistics
        """
        print(f"\n{'='*80}")
        print(f"Starting ingestion for {owner}/{repo}")
        print(f"{'='*80}\n")

        self.stats["start_time"] = datetime.utcnow()

        try:
            # Step 1: Fetch issues
            print("Step 1: Fetching issues from GitHub...")
            issues = self.issue_fetcher.fetch_issues(
                owner=owner,
                repo=repo,
                state=state,
                labels=labels,
                since=since,
                max_issues=max_issues
            )
            self.stats["total_issues"] = len(issues)
            print(f"✓ Fetched {len(issues)} issues\n")

            if not issues:
                print("No issues found. Exiting.")
                return self.stats

            # Step 2-5: Process each issue immediately (one at a time for better performance)
            print("Step 2-5: Processing issues (chunking, embedding, storing)...")
            all_chunk_ids = []
            
            for i, issue in enumerate(issues, 1):
                print(f"\n[{i}/{len(issues)}] Processing issue #{issue.number} - {issue.title[:50]}...")

                try:
                    # Check if issue already exists in vector store
                    existing_data = self._check_issue_exists(owner, repo, issue.number)

                    if existing_data:
                        # Check if the issue has been updated since last ingestion
                        last_ingested = existing_data.get("updated_at")
                        current_updated = issue.updated_at.isoformat()

                        if last_ingested == current_updated:
                            print(f"  ⊘ Skipping - already up to date")
                            self.stats["skipped_issues"] += 1
                            continue
                        else:
                            print(f"  ↻ Updating - has been modified since last ingestion")
                            # Delete old chunks before re-processing
                            self._delete_issue_chunks(owner, repo, issue.number)
                            self.stats["updated_issues"] += 1
                    else:
                        self.stats["new_issues"] += 1

                    # Process this single issue (chunk, embed, store)
                    chunk_ids = self._process_issue(issue)
                    all_chunk_ids.extend(chunk_ids)
                    print(f"  ✓ Stored {len(chunk_ids)} chunks")

                except Exception as e:
                    error_msg = f"Error processing issue #{issue.number}: {e}"
                    print(f"  ✗ {error_msg}")
                    self.stats["errors"].append(error_msg)
                    continue

            self.stats["end_time"] = datetime.utcnow()
            
            # Print summary
            self._print_summary(owner, repo)
            
            return self.stats

        except Exception as e:
            error_msg = f"Fatal error during ingestion: {e}"
            print(f"\n✗ {error_msg}")
            self.stats["errors"].append(error_msg)
            self.stats["end_time"] = datetime.utcnow()
            raise

    def _process_issue(self, issue: GitHubIssue) -> List[str]:
        """
        Process a single issue through the entire pipeline.

        Args:
            issue: GitHubIssue object

        Returns:
            List of chunk IDs that were stored
        """
        # Step 2: Process text
        processed_text = self.text_processor.process_issue(issue)
        
        # Step 3: Chunk text
        metadata = {
            "issue_number": issue.number,
            "issue_title": issue.title,
            "repository": f"{issue.owner}/{issue.repo}",
            "state": issue.state,
            "labels": issue.labels,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "url": issue.url,
        }
        
        chunks = self.chunker.chunk_text(processed_text, metadata=metadata)
        self.stats["total_chunks"] += len(chunks)
        
        if not chunks:
            return []

        # Step 4 & 5: Create embeddings and store in batches
        chunk_ids = []
        
        for i in range(0, len(chunks), self.batch_size):
            batch_chunks = chunks[i:i + self.batch_size]
            
            # Extract text from chunks
            texts = [chunk.content for chunk in batch_chunks]
            
            # Create embeddings
            embeddings = self.embedding_service.create_embeddings_batch(texts)
            self.stats["total_embeddings"] += len(embeddings)
            
            # Store in vector database
            batch_ids = self.vector_store.store_chunks_batch(batch_chunks, embeddings)
            chunk_ids.extend(batch_ids)
        
        return chunk_ids

    def query_issues(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query the vector database for similar issue content.

        Args:
            query: Query text
            top_k: Number of results to return
            filter_dict: Optional metadata filters

        Returns:
            List of matching chunks with metadata
        """
        print(f"\nQuerying for: '{query}'")
        
        # Create embedding for query
        query_embedding = self.embedding_service.create_embedding(query)
        
        # Query vector store
        results = self.vector_store.query_similar(
            query_vector=query_embedding,
            top_k=top_k,
            filter_dict=filter_dict
        )
        
        print(f"Found {len(results)} results\n")
        
        return results

    def delete_repository_data(self, owner: str, repo: str) -> None:
        """
        Delete all data for a specific repository.

        Args:
            owner: Repository owner
            repo: Repository name
        """
        print(f"Deleting all data for {owner}/{repo}...")
        
        filter_dict = {"repository": f"{owner}/{repo}"}
        self.vector_store.delete_by_metadata(filter_dict)
        
        print(f"✓ Deleted all data for {owner}/{repo}")

    def _check_issue_exists(self, owner: str, repo: str, issue_number: int) -> Optional[Dict[str, Any]]:
        """
        Check if an issue already exists in the vector store.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number

        Returns:
            Metadata of existing issue if found, None otherwise
        """
        try:
            # Query for any chunk from this issue
            filter_dict = {
                "repository": f"{owner}/{repo}",
                "issue_number": issue_number
            }

            results = self.vector_store.query(
                query_vector=[0.0] * 1536,  # Dummy vector
                top_k=1,
                filter_dict=filter_dict
            )

            if results and len(results) > 0:
                return results[0].get("metadata", {})

            return None
        except Exception:
            # If query fails, assume issue doesn't exist
            return None

    def _delete_issue_chunks(self, owner: str, repo: str, issue_number: int) -> None:
        """
        Delete all chunks for a specific issue.

        Args:
            owner: Repository owner
            repo: Repository name
            issue_number: Issue number
        """
        filter_dict = {
            "repository": f"{owner}/{repo}",
            "issue_number": issue_number
        }
        self.vector_store.delete_by_metadata(filter_dict)

    def _print_summary(self, owner: str, repo: str):
        """Print ingestion summary."""
        duration = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        print(f"\n{'='*80}")
        print(f"Ingestion Summary for {owner}/{repo}")
        print(f"{'='*80}")
        print(f"Total Issues Fetched: {self.stats['total_issues']}")
        print(f"New Issues: {self.stats['new_issues']}")
        print(f"Updated Issues: {self.stats['updated_issues']}")
        print(f"Skipped Issues (unchanged): {self.stats['skipped_issues']}")
        print(f"Total Chunks Created: {self.stats['total_chunks']}")
        print(f"Total Embeddings Created: {self.stats['total_embeddings']}")
        print(f"Duration: {duration:.2f} seconds")

        processed = self.stats['new_issues'] + self.stats['updated_issues']
        if processed > 0:
            print(f"Average Time per Processed Issue: {duration / processed:.2f} seconds")

        if self.stats["errors"]:
            print(f"\nErrors ({len(self.stats['errors'])}):")
            for error in self.stats["errors"]:
                print(f"  - {error}")
        else:
            print("\n✓ No errors")
        
        print(f"{'='*80}\n")

    def get_stats(self) -> Dict[str, Any]:
        """Get ingestion statistics."""
        return self.stats.copy()

    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_issues": 0,
            "total_chunks": 0,
            "total_embeddings": 0,
            "new_issues": 0,
            "updated_issues": 0,
            "skipped_issues": 0,
            "start_time": None,
            "end_time": None,
            "errors": [],
        }

