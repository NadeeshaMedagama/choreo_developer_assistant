#!/usr/bin/env python3
"""
Main entry point for GitHub Issues Ingestion.

Usage:
    python main.py <owner>/<repo> [options]
    
    python main.py wso2/choreo --max-issues 50
    python main.py wso2/choreo --state open --labels bug,enhancement
    python main.py wso2/choreo --since 2024-01-01

Options:
    --state: Issue state (open, closed, all) [default: all]
    --labels: Comma-separated list of labels to filter by
    --since: ISO 8601 timestamp (only issues updated after this date)
    --max-issues: Maximum number of issues to fetch
    --batch-size: Batch size for processing [default: 10]
    --query: Query the vector database instead of ingesting
    --delete: Delete all data for the repository
"""

import argparse
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from github_issues_ingestion import create_ingestion_pipeline
from github_issues_ingestion.utils.helpers import validate_repo_format


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest GitHub issues into vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        "repository",
        help="Repository in format 'owner/repo'"
    )
    
    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="all",
        help="Filter issues by state (default: all)"
    )
    
    parser.add_argument(
        "--labels",
        help="Comma-separated list of labels to filter by"
    )
    
    parser.add_argument(
        "--since",
        help="Only issues updated after this timestamp (ISO 8601 format)"
    )
    
    parser.add_argument(
        "--max-issues",
        type=int,
        help="Maximum number of issues to fetch"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for processing (default: 10)"
    )
    
    parser.add_argument(
        "--query",
        help="Query the vector database instead of ingesting"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return for queries (default: 5)"
    )
    
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete all data for the repository"
    )
    
    args = parser.parse_args()
    
    # Validate repository format
    try:
        owner, repo = validate_repo_format(args.repository)
    except ValueError as e:
        print(f"Error: {e}")
        print("Repository must be in format 'owner/repo'")
        sys.exit(1)
    
    # Create pipeline
    try:
        print("Initializing ingestion pipeline...")
        orchestrator = create_ingestion_pipeline(batch_size=args.batch_size)
        print("✓ Pipeline initialized\n")
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        sys.exit(1)
    
    # Handle delete operation
    if args.delete:
        confirm = input(f"Are you sure you want to delete all data for {owner}/{repo}? (yes/no): ")
        if confirm.lower() == "yes":
            try:
                orchestrator.delete_repository_data(owner, repo)
                print("✓ Data deleted successfully")
            except Exception as e:
                print(f"Error deleting data: {e}")
                sys.exit(1)
        else:
            print("Delete cancelled")
        return
    
    # Handle query operation
    if args.query:
        try:
            # Add repository filter
            filter_dict = {"repository": f"{owner}/{repo}"}
            
            results = orchestrator.query_issues(
                query=args.query,
                top_k=args.top_k,
                filter_dict=filter_dict
            )
            
            # Print results
            print(f"\nTop {len(results)} results:\n")
            for i, result in enumerate(results, 1):
                print(f"{i}. Score: {result['score']:.4f}")
                print(f"   Issue: #{result['metadata'].get('issue_number')} - {result['metadata'].get('issue_title', 'N/A')}")
                print(f"   Chunk: {result['metadata'].get('chunk_index', 0) + 1}/{result['metadata'].get('total_chunks', 1)}")
                print(f"   Content preview: {result['content'][:200]}...")
                print()
            
        except Exception as e:
            print(f"Error querying: {e}")
            sys.exit(1)
        
        return
    
    # Handle ingestion
    try:
        # Parse labels
        labels = None
        if args.labels:
            labels = [label.strip() for label in args.labels.split(",")]
        
        # Ingest repository
        stats = orchestrator.ingest_repository(
            owner=owner,
            repo=repo,
            state=args.state,
            labels=labels,
            since=args.since,
            max_issues=args.max_issues
        )
        
        # Exit with success
        if stats["errors"]:
            print(f"\n⚠ Completed with {len(stats['errors'])} error(s)")
            sys.exit(1)
        else:
            print("\n✓ Ingestion completed successfully!")
            sys.exit(0)
    
    except KeyboardInterrupt:
        print("\n\n⚠ Ingestion interrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

