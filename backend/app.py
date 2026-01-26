import os
import time
import json
import asyncio
from typing import List, Dict, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel

from services.llm_service import LLMService
from services.context_manager import ContextManager
from services.github_service import GitHubService
from services.image_service import ImageProcessingService
from services.conversation_memory_manager import ConversationMemoryManager
from services.url_validator import get_url_validator
from services.choreo_repo_registry import get_choreo_registry
from services.llm_repo_matcher import get_llm_repo_matcher
from services.diagram_detection_service import get_diagram_detection_service
from db.vector_client import VectorClient
from utils.config import load_config
from services.ingestion import IngestionService
from services.rag_graph import build_graph

# Import new SOLID monitoring architecture
from monitoring import get_monitoring_service
from monitoring.middleware.metrics_middleware import MetricsMiddleware
from monitoring.config.logging_setup import setup_logging
from monitoring.health.health_checker import MilvusHealthChecker, ApplicationHealthChecker

# Initialize logging
setup_logging(log_level="INFO", enable_json=False)

# Pydantic models for request validation
class AskRequest(BaseModel):
    question: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    summary: Optional[Dict] = None  # Conversation summary from previous interactions
    max_history_tokens: Optional[int] = 4000  # Configurable token limit
    enable_summarization: Optional[bool] = True  # Enable/disable auto-summarization

# Get monitoring service (Singleton)
monitoring = get_monitoring_service()

# Global service instances (lazy-initialized)
config = None
vector_client = None
llm_service = None
github_service = None
image_service = None
context_manager = None
ingestion_service = None
rag = None
conversation_memory_manager = None
url_validator = None
services_initialized = False

def initialize_services():
    """Initialize all services lazily to speed up startup time."""
    global config, vector_client, llm_service, github_service, image_service
    global context_manager, ingestion_service, rag, conversation_memory_manager
    global url_validator, services_initialized

    if services_initialized:
        return

    monitoring.log_info("Starting Choreo AI Assistant service initialization...", logger_type='app')

    # Load configuration
    config = load_config()

    # Initialize services with timeout handling
    try:
        # Initialize vector client with connection retry
        monitoring.log_info("Initializing Milvus vector client...", logger_type='app')
        vector_client = VectorClient(
            uri=config["MILVUS_URI"],
            token=config["MILVUS_TOKEN"],
            collection_name=config["MILVUS_COLLECTION_NAME"],
            dimension=config.get("MILVUS_DIMENSION", 1536),
            metric=config.get("MILVUS_METRIC", "COSINE")
        )
        monitoring.log_info("Milvus vector client initialized successfully", logger_type='app')
    except Exception as e:
        monitoring.log_error(f"CRITICAL: Failed to initialize Milvus: {e}", logger_type='app')
        monitoring.log_error("Application will start but RAG features will be unavailable", logger_type='app')
        vector_client = None  # Explicitly set to None to signal failure

    try:
        monitoring.log_info("Initializing Azure OpenAI LLM service...", logger_type='app')
        llm_service = LLMService(
            endpoint=config["AZURE_OPENAI_ENDPOINT"],
            api_key=config["AZURE_OPENAI_KEY"],
            deployment=config["AZURE_OPENAI_DEPLOYMENT"],
            api_version=config.get("AZURE_OPENAI_API_VERSION") or "2024-02-15-preview",
        )

        # Allow separate embeddings deployment if provided
        if config.get("AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"):
            llm_service.set_embeddings_deployment(config["AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT"])

        monitoring.log_info("LLM service initialized", logger_type='app')
    except Exception as e:
        monitoring.log_error(f"Failed to initialize LLM service: {e}", logger_type='app')

    try:
        github_service = GitHubService(token=config.get("GITHUB_TOKEN"))

        # Initialize image processing service (optional)
        if config.get("GOOGLE_VISION_API_KEY"):
            image_service = ImageProcessingService(api_key=config["GOOGLE_VISION_API_KEY"])

        if vector_client and llm_service:
            context_manager = ContextManager(vector_client, llm_service)
            ingestion_service = IngestionService(github_service, llm_service, vector_client, image_service)
            rag = build_graph(llm_service, vector_client)

        # Initialize conversation memory manager
        enable_llm_summarization = os.getenv("ENABLE_LLM_SUMMARIZATION", "true").lower() == "true"
        max_summarization_retries = int(os.getenv("MAX_SUMMARIZATION_RETRIES", "2"))

        if llm_service:
            conversation_memory_manager = ConversationMemoryManager(
                llm_service=llm_service,
                max_total_tokens=8000,
                max_history_tokens=4000,
                recent_window_size=6,
                summarization_trigger_ratio=0.75,
                enable_llm_summarization=enable_llm_summarization,
                max_summarization_retries=max_summarization_retries
            )

            if not enable_llm_summarization:
                monitoring.log_info("LLM summarization disabled - using simple fallback summaries", logger_type='ai')

        # Initialize URL validator
        enable_url_validation = os.getenv("ENABLE_URL_VALIDATION", "true").lower() == "true"
        url_validation_timeout = int(os.getenv("URL_VALIDATION_TIMEOUT", "5"))

        trusted_domains_env = os.getenv("URL_VALIDATION_TRUSTED_DOMAINS", "")
        trusted_domains = [d.strip() for d in trusted_domains_env.split(",") if d.strip()] if trusted_domains_env else None

        url_validator = get_url_validator(
            timeout=url_validation_timeout,
            max_concurrent=10,
            enable_validation=enable_url_validation,
            trusted_domains=trusted_domains
        )

        if enable_url_validation:
            monitoring.log_info(f"URL validation enabled (timeout: {url_validation_timeout}s)", logger_type='app')
        else:
            monitoring.log_info("URL validation disabled", logger_type='app')

        # Register health checkers
        if vector_client:
            monitoring.register_health_checker(MilvusHealthChecker(vector_client))
        monitoring.register_health_checker(ApplicationHealthChecker())
        monitoring.log_info("Health checkers registered", logger_type='app')

        services_initialized = True
        monitoring.log_info("All services initialized successfully", logger_type='app')

    except Exception as e:
        monitoring.log_error(f"Error during service initialization: {e}", logger_type='app', exc_info=True)
        # Mark as initialized anyway to allow basic operations
        services_initialized = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    monitoring.log_info("FastAPI application starting up...", logger_type='app')
    # Don't initialize services here - let them initialize lazily on first request
    yield
    # Shutdown
    monitoring.log_info("FastAPI application shutting down...", logger_type='app')

# Create FastAPI app with lifespan
app = FastAPI(
    title="Choreo AI Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:9090",
        "http://localhost:8000",
        "https://*.ngrok-free.app",  # Allow all ngrok URLs
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add metrics middleware (SOLID architecture)
app.add_middleware(MetricsMiddleware, monitoring_service=monitoring)
monitoring.log_info("Metrics middleware added", logger_type='app')

@app.get("/")
def read_root():
    return {"message": "Choreo AI Assistant (Azure LLM + Milvus) is running.", "status": "ok"}

@app.post("/")
async def root_post(request: Request):
    """Handle POST requests to root - often from webhooks or health checks."""
    try:
        body = await request.json()
        return {
            "message": "POST received at root endpoint",
            "hint": "Use /api/webhook/github for GitHub webhooks or /api/ask for AI queries",
            "received": body
        }
    except:
        return {
            "message": "POST received at root endpoint",
            "hint": "Use /api/webhook/github for GitHub webhooks or /api/ask for AI queries"
        }


@app.get("/api/health")
def health_check():
    """Health check endpoint that tests all components. Initializes services on first call."""
    try:
        # Initialize services on first health check if not already initialized
        if not services_initialized:
            monitoring.log_info("Health check triggered, initializing services...", logger_type='app')
            initialize_services()

        health_status = monitoring.check_health()
        monitoring.log_info(
            f"Health check completed: {health_status['status']}",
            logger_type='app'
        )
        return health_status
    except Exception as e:
        monitoring.log_error(
            f"Health check failed: {str(e)}",
            logger_type='app',
            exc_info=True
        )
        return {
            "status": "unhealthy",
            "error": str(e),
            "services_initialized": services_initialized
        }

# Keep old endpoint for backward compatibility
@app.get("/health")
def health_check_legacy():
    """Simplified health check endpoint for Choreo - returns basic Milvus status."""
    try:
        # Check if services are initialized and Milvus is available
        if services_initialized and vector_client:
            try:
                is_connected = vector_client.test_connection()
                return {
                    "status": "healthy" if is_connected else "unhealthy",
                    "milvus": "connected" if is_connected else "disconnected"
                }
            except Exception as e:
                monitoring.log_error(f"Milvus health check failed: {str(e)}", logger_type='app')
                return {
                    "status": "unhealthy",
                    "milvus": "disconnected"
                }
        else:
            # Services not initialized yet - return healthy but indicate not ready
            return {
                "status": "healthy",
                "milvus": "initializing"
            }
    except Exception as e:
        monitoring.log_error(f"Health check failed: {str(e)}", logger_type='app')
        return {
            "status": "unhealthy",
            "milvus": "error"
        }

@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint."""
    metrics_data = monitoring.get_metrics()
    return Response(content=metrics_data, media_type="text/plain; version=0.0.4")

@app.post("/api/ask")
async def ask_ai(request: AskRequest):
    # Ensure services are initialized before processing requests
    if not services_initialized:
        monitoring.log_info("Request received, initializing services...", logger_type='app')
        initialize_services()

    # Fail fast if critical services are not available
    if vector_client is None or conversation_memory_manager is None or llm_service is None:
        monitoring.log_error("Critical services not initialized - cannot process request", logger_type='app')
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={
                "error": "Service Unavailable",
                "message": "Database or AI services are not available",
                "detail": "Vector database initialization failed. Please check server logs and verify Milvus connection."
            }
        )

    start_time = time.time()
    try:
        question = request.question
        conversation_history = request.conversation_history or []
        existing_summary = request.summary
        enable_summarization = request.enable_summarization if request.enable_summarization is not None else True

        monitoring.log_info(
            f"AI request received",
            logger_type='ai',
            question_length=len(question),
            history_length=len(conversation_history),
            has_summary=bool(existing_summary)
        )

        # 1. Manage conversation memory with smart summarization
        summary = None
        recent_messages = conversation_history
        memory_stats = {}

        if enable_summarization and conversation_history:
            # Estimate context tokens (rough estimate before retrieval)
            estimated_context_tokens = 500  # Reserve for DB context

            summary, recent_messages, memory_stats = conversation_memory_manager.manage_conversation_memory(
                conversation_history=conversation_history,
                existing_summary=existing_summary,
                current_context_tokens=estimated_context_tokens
            )

            monitoring.log_info(
                f"Conversation memory managed",
                logger_type='ai',
                **memory_stats
            )

        # 2. Detect if query is asking for diagrams
        diagram_service = get_diagram_detection_service()
        is_diagram_query = diagram_service.is_diagram_query(question)
        diagram_type = None
        diagram_metadata = {}

        if is_diagram_query:
            diagram_type = diagram_service.detect_diagram_type(question)
            monitoring.log_info(
                f"Diagram query detected",
                logger_type='ai',
                diagram_type=diagram_type or "general",
                query=question[:100]
            )

        # 3. Enrich query with conversation context for better retrieval
        enriched_query = question
        if summary or recent_messages:
            context_parts = []

            # Add summary if exists
            if summary:
                context_parts.append(f"Summary: {summary.content[:300]}")  # Limit summary for retrieval

            # Add recent messages
            if recent_messages:
                recent_history_preview = recent_messages[-4:]  # Last 2 turns
                history_text = "\n".join(
                    f"{msg['role']}: {msg['content'][:200]}"
                    for msg in recent_history_preview
                )
                context_parts.append(history_text)

            enriched_query = f"{chr(10).join(context_parts)}\nCurrent question: {question}"

        # Enhance query for diagram searches
        if is_diagram_query:
            enriched_query, diagram_metadata = diagram_service.enhance_query_for_diagrams(enriched_query)

        # 4. Retrieve context from vector DB
        search_start = time.time()
        try:
            similar_rows = context_manager.retrieve_by_text(enriched_query, top_k=10)
            search_duration = time.time() - search_start
            monitoring.record_vector_search(search_duration, len(similar_rows))
        except Exception as e:
            # Handle Milvus errors gracefully (including index creation errors)
            monitoring.log_error(
                f"Vector search failed - {type(e).__name__}: {str(e)}",
                logger_type='ai',
                exc_info=True,
                error_type=type(e).__name__
            )
            # Continue with empty results if vector search fails
            similar_rows = []
            search_duration = time.time() - search_start
            monitoring.record_vector_search(search_duration, 0)

        # Filter out OpenChoreo content
        filtered_rows = [
            row for row in similar_rows
            if "openchoreo" not in row.get("metadata", {}).get("repository", "").lower()
        ]

        # Quality filtering
        high_quality_rows = [
            row for row in filtered_rows
            if row.get("score", 0.0) > 0.7
        ]

        if len(high_quality_rows) < 3:
            high_quality_rows = [
                row for row in filtered_rows
                if row.get("score", 0.0) > 0.6
            ]

        context_rows = high_quality_rows[:10]
        context_text = "\n".join(row.get("content", "") for row in context_rows if row.get("content"))

        # 3.5 Enhance context with STS Runtime Flow knowledge if query is related
        choreo_registry = get_choreo_registry()
        if choreo_registry and choreo_registry.is_sts_runtime_query(question):
            sts_runtime_info = choreo_registry.get_sts_runtime_flow_info(question)
            context_text = f"{sts_runtime_info}\n\n{context_text}"
            monitoring.log_info(
                "STS Runtime Flow context injected",
                logger_type='ai',
                query_topic="sts_runtime"
            )

        # 4. Use LLM-powered repo matcher to extract available repo URLs from context
        repo_matcher = get_llm_repo_matcher()

        # Extract repo URLs from both context text and source metadata
        context_urls = repo_matcher.extract_repo_urls_from_context(context_text)
        source_urls = repo_matcher.extract_repo_urls_from_sources(context_rows)

        # Combine URLs
        all_extracted_urls = list(set(context_urls + source_urls))

        # Check if user is asking for ALL repositories or all Choreo repositories
        query_lower = question.lower()
        is_requesting_all_repos = any(pattern in query_lower for pattern in [
            'all repos', 'all repositories', 'give me all',
            'list all repo', 'show all repo', 'provide all repo',
            'all wso2-enterprise', 'all 154', 'how many repo'
        ])

        is_requesting_choreo_repos = any(pattern in query_lower for pattern in [
            'all choreo repo', 'choreo keyword repo', 'choreo related repo',
            'repos with choreo', 'repositories with choreo'
        ])

        # Check if user is asking for a SPECIFIC repository
        is_requesting_specific_repo = any(pattern in query_lower for pattern in [
            'repo url', 'repository url', 'repo of', 'repository of',
            'repo contains', 'repository contains', 'repo for',
            'which repo has', 'what repo', 'find repo', 'locate repo',
            'give me repo'
        ]) and not (is_requesting_all_repos or is_requesting_choreo_repos)

        # Special handling: If asking for a specific repo, search dynamically
        if is_requesting_specific_repo:
            monitoring.log_info(
                f"Specific repository search requested: {question[:100]}",
                logger_type='ai'
            )

            try:
                # Extract the key part of query (after "repo of/for/contains")
                search_term = question.lower()
                for prefix in ['repo url of the', 'repo url of', 'repository url of the', 'repository url of',
                             'repo of the', 'repo of', 'repository of the', 'repository of',
                             'repo contains the', 'repo contains', 'repository contains the', 'repository contains',
                             'repo for the', 'repo for', 'repository for the', 'repository for',
                             'which repo has', 'what repo has', 'give me repo url of the', 'give me repo url of',
                             'find repo for', 'locate repo for']:
                    if prefix in search_term:
                        search_term = search_term.split(prefix, 1)[1].strip()
                        break

                # Clean up search term
                search_term = search_term.replace('?', '').replace('the ', '').strip()

                if search_term:  # Only search if we have a term
                    # Search for the repository
                    repo = repo_matcher.find_repository_by_name(search_term)

                    if repo:
                        formatted_response = repo_matcher.format_single_repo_response(repo, search_term)

                        monitoring.log_info(
                            f"Found specific repository: {repo.get('name')}",
                            logger_type='ai'
                        )

                        # Return directly without LLM processing
                        return {
                            "answer": formatted_response,
                            "sources": [],
                            "summary": summary.to_dict() if summary else None,
                            "memory_stats": memory_stats
                        }

            except Exception as e:
                monitoring.log_error(
                    f"Failed to search for specific repository: {e}",
                    logger_type='ai',
                    exc_info=True
                )
                # Fall through to normal LLM response

        # Special handling: If user is asking for ALL repos, fetch and return directly
        if is_requesting_all_repos or is_requesting_choreo_repos:
            monitoring.log_info(
                f"Direct repository list requested: all_repos={is_requesting_all_repos}, choreo_repos={is_requesting_choreo_repos}",
                logger_type='ai'
            )

            try:
                # Fetch repos dynamically from GitHub
                if is_requesting_choreo_repos:
                    repos = repo_matcher.get_all_wso2_enterprise_repos(keyword="choreo")
                    formatted_response = repo_matcher.format_repos_for_response(
                        repos,
                        query_context="with 'choreo' keyword"
                    )
                else:
                    repos = repo_matcher.get_all_wso2_enterprise_repos(keyword=None)
                    formatted_response = repo_matcher.format_repos_for_response(
                        repos,
                        query_context="from wso2-enterprise organization"
                    )

                monitoring.log_info(
                    f"Successfully fetched {len(repos)} repositories",
                    logger_type='ai'
                )

                # Return directly without LLM processing
                return {
                    "answer": formatted_response,
                    "sources": [],
                    "summary": summary.to_dict() if summary else None,
                    "memory_stats": memory_stats
                }

            except Exception as e:
                monitoring.log_error(
                    f"Failed to fetch repositories dynamically: {e}",
                    logger_type='ai',
                    exc_info=True
                )
                # Fall through to normal LLM response

        # If asking about repositories in general (not specific component), get more repos
        is_general_repo_query = any(keyword in query_lower for keyword in [
            'which repo', 'what repo', 'list repo',
            'show repo', 'available repo'
        ])

        if is_general_repo_query or len(all_extracted_urls) < 5:
            # Query database for more Choreo repos
            db_repos = repo_matcher.get_all_choreo_repos_from_db(vector_client, top_k=50)
            all_extracted_urls = list(set(all_extracted_urls + db_repos))

            # Use registry as fallback if still not enough
            all_extracted_urls = repo_matcher.enhance_with_registry_fallback(all_extracted_urls)

        # Generate enhanced system prompt with available repo URLs
        system_prompt = repo_matcher.generate_enhanced_system_prompt(
            base_context=context_text,
            context_urls=all_extracted_urls,
            source_urls=[]  # Already combined above
        )

        # Add diagram generation enhancement if this is a diagram query
        if is_diagram_query:
            diagram_enhancement = diagram_service.generate_diagram_prompt_enhancement(
                question, diagram_type
            )
            system_prompt += f"\n\n{diagram_enhancement}"
            monitoring.log_info(
                "Added diagram generation instructions to system prompt",
                logger_type='ai',
                diagram_type=diagram_type or "general"
            )

        messages = conversation_memory_manager.build_llm_messages(
            question=question,
            context=context_text,
            recent_messages=recent_messages,
            summary=summary,
            system_prompt=system_prompt
        )

        # 5. Get LLM response
        # Use the messages directly with client
        response = llm_service.client.chat.completions.create(
            model=llm_service.deployment,
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )
        answer = response.choices[0].message.content

        # 6. Validate URLs in the answer using LLM intelligence + HTTP checks
        validation_start = time.time()
        filtered_answer, url_validation_map = await url_validator.validate_answer_urls(
            answer=answer,
            llm_service=llm_service,
            context=context_text
        )
        validation_duration = time.time() - validation_start

        if url_validation_map:
            valid_count = sum(1 for v in url_validation_map.values() if v)
            invalid_count = len(url_validation_map) - valid_count
            monitoring.log_info(
                f"URL validation completed",
                logger_type='ai',
                validation_duration=f"{validation_duration:.2f}s",
                valid_urls=valid_count,
                invalid_urls=invalid_count
            )

        # 7. Extract source documents
        RELEVANCE_THRESHOLD = 0.70
        sources = []
        for row in filtered_rows:
            metadata = row.get("metadata", {})
            repository = metadata.get("repository", "")
            score = row.get("score", 0.0)

            if "openchoreo" in repository.lower():
                continue

            if score < RELEVANCE_THRESHOLD:
                continue

            source_info = {
                "content": row.get("content", "")[:200] + "...",
                "score": score,
            }

            if metadata.get("file_path"):
                source_info["file_path"] = metadata["file_path"]
            if metadata.get("repository"):
                source_info["repository"] = metadata["repository"]
            if metadata.get("url"):
                source_info["url"] = metadata["url"]
            if metadata.get("source_type"):
                source_info["source_type"] = metadata["source_type"]
            if metadata.get("title"):
                source_info["title"] = metadata["title"]

            sources.append(source_info)

        # Fallback if no sources meet threshold
        if len(sources) == 0 and len(filtered_rows) > 0:
            for row in filtered_rows[:3]:
                metadata = row.get("metadata", {})
                if "openchoreo" in metadata.get("repository", "").lower():
                    continue

                source_info = {
                    "content": row.get("content", "")[:200] + "...",
                    "score": row.get("score", 0.0),
                }

                if metadata.get("file_path"):
                    source_info["file_path"] = metadata["file_path"]
                if metadata.get("repository"):
                    source_info["repository"] = metadata["repository"]
                if metadata.get("url"):
                    source_info["url"] = metadata["url"]
                if metadata.get("source_type"):
                    source_info["source_type"] = metadata["source_type"]
                if metadata.get("title"):
                    source_info["title"] = metadata["title"]

                sources.append(source_info)
        else:
            sources = sources[:3]

        # 8. Validate URLs in sources
        sources = await url_validator.validate_and_filter_sources(sources)

        # Record metrics
        inference_duration = time.time() - start_time
        monitoring.record_ai_inference(
            duration=inference_duration,
            success=True,
            input_tokens=len(question.split()),
            output_tokens=len(filtered_answer.split())
        )

        monitoring.log_info(
            f"AI request completed",
            logger_type='ai',
            duration=f"{inference_duration:.2f}s",
            context_count=len(similar_rows)
        )

        # Return response with summary for next request
        response_data = {
            "answer": filtered_answer,
            "sources": sources,
            "context_count": len(similar_rows),
        }

        # Add URL validation info if validation was performed
        if url_validation_map:
            enable_url_validation = os.getenv("ENABLE_URL_VALIDATION", "true").lower() == "true"
            response_data["url_validation"] = {
                "total_urls": len(url_validation_map),
                "valid_urls": sum(1 for v in url_validation_map.values() if v),
                "invalid_urls": sum(1 for v in url_validation_map.values() if not v),
                "validation_enabled": enable_url_validation
            }

        # Add memory management info
        if enable_summarization:
            response_data["memory_stats"] = memory_stats
            if summary:
                response_data["summary"] = summary.to_dict()
                response_data["summary_metadata"] = {
                    "topics_covered": summary.topics_covered,
                    "key_questions": summary.key_questions,
                    "important_decisions": summary.important_decisions
                }

        return response_data

    except Exception as e:
        monitoring.log_error(
            f"AI request failed: {str(e)}",
            logger_type='ai',
            exc_info=True
        )
        monitoring.record_error()
        monitoring.record_ai_inference(
            duration=time.time() - start_time,
            success=False
        )
        raise

# Keep old endpoint for backward compatibility
@app.post("/ask")
def ask_ai_legacy(question: str):
    # Convert to AskRequest for backward compatibility
    request = AskRequest(question=question, conversation_history=None)
    return ask_ai(request)

@app.post("/api/ask/stream")
async def ask_ai_stream(request: AskRequest):
    """Stream AI response progressively like ChatGPT with conversation history and smart summarization"""
    try:
        # Ensure services are initialized
        if not services_initialized:
            monitoring.log_error(
                "Services not initialized when streaming endpoint called",
                logger_type='ai'
            )
            raise RuntimeError("Services not initialized. Please check application startup.")

        # Fail fast if critical services are not available
        if vector_client is None or conversation_memory_manager is None or llm_service is None:
            monitoring.log_error("Critical services not initialized - cannot process streaming request", logger_type='app')
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={
                    "error": "Service Unavailable",
                    "message": "Database or AI services are not available",
                    "detail": "Vector database initialization failed. Please check server logs and verify Milvus connection."
                }
            )

        question = request.question
        conversation_history = request.conversation_history or []
        existing_summary = request.summary
        enable_summarization = request.enable_summarization if request.enable_summarization is not None else True

        monitoring.log_info(
            f"Streaming AI request received",
            logger_type='ai',
            question_length=len(question),
            history_length=len(conversation_history),
            has_summary=bool(existing_summary)
        )

        # 1. Manage conversation memory with smart summarization
        summary = None
        recent_messages = conversation_history
        memory_stats = {}

        if enable_summarization and conversation_history:
            estimated_context_tokens = 500

            summary, recent_messages, memory_stats = conversation_memory_manager.manage_conversation_memory(
                conversation_history=conversation_history,
                existing_summary=existing_summary,
                current_context_tokens=estimated_context_tokens
            )

            monitoring.log_info(
                f"Streaming conversation memory managed",
                logger_type='ai',
                **memory_stats
            )

        # 2. Detect if query is asking for diagrams
        diagram_service = get_diagram_detection_service()
        is_diagram_query = diagram_service.is_diagram_query(question)
        diagram_type = None
        diagram_metadata = {}

        if is_diagram_query:
            diagram_type = diagram_service.detect_diagram_type(question)
            monitoring.log_info(
                f"Diagram query detected (streaming)",
                logger_type='ai',
                diagram_type=diagram_type or "general",
                query=question[:100]
            )

        # 3. Enrich query with conversation context
        enriched_query = question
        if summary or recent_messages:
            context_parts = []

            if summary:
                context_parts.append(f"Summary: {summary.content[:300]}")

            if recent_messages:
                recent_history_preview = recent_messages[-4:]
                history_text = "\n".join(
                    f"{msg['role']}: {msg['content'][:200]}"
                    for msg in recent_history_preview
                )
                context_parts.append(history_text)

            enriched_query = f"{chr(10).join(context_parts)}\nCurrent question: {question}"

        # Enhance query for diagram searches
        if is_diagram_query:
            enriched_query, diagram_metadata = diagram_service.enhance_query_for_diagrams(enriched_query)

        # 4. Retrieve context from vector DB
        search_start = time.time()
        try:
            similar_rows = context_manager.retrieve_by_text(enriched_query, top_k=10)
            search_duration = time.time() - search_start
            monitoring.record_vector_search(search_duration, len(similar_rows))
        except Exception as e:
            # Handle Milvus errors gracefully (including index creation errors)
            monitoring.log_error(
                f"Vector search failed - {type(e).__name__}: {str(e)}",
                logger_type='ai',
                exc_info=True,
                error_type=type(e).__name__
            )
            # Continue with empty results if vector search fails
            similar_rows = []
            search_duration = time.time() - search_start
            monitoring.record_vector_search(search_duration, 0)

        # Filter out OpenChoreo content
        filtered_rows = [
            row for row in similar_rows
            if "openchoreo" not in row.get("metadata", {}).get("repository", "").lower()
        ]

        # Quality filtering
        high_quality_rows = [
            row for row in filtered_rows
            if row.get("score", 0.0) > 0.7
        ]

        if len(high_quality_rows) < 3:
            high_quality_rows = [
                row for row in filtered_rows
                if row.get("score", 0.0) > 0.6
            ]

        context_rows = high_quality_rows[:5]
        context_text = "\n".join(row.get("content", "") for row in context_rows if row.get("content"))

        # 3.5 Enhance context with STS Runtime Flow knowledge if query is related
        choreo_registry = get_choreo_registry()
        if choreo_registry and choreo_registry.is_sts_runtime_query(question):
            sts_runtime_info = choreo_registry.get_sts_runtime_flow_info(question)
            context_text = f"{sts_runtime_info}\n\n{context_text}"
            monitoring.log_info(
                "STS Runtime Flow context injected (streaming)",
                logger_type='ai',
                query_topic="sts_runtime"
            )

        # 4. Extract source documents
        RELEVANCE_THRESHOLD = 0.70
        sources = []
        for row in filtered_rows:
            metadata = row.get("metadata", {})
            repository = metadata.get("repository", "")
            score = row.get("score", 0.0)

            if "openchoreo" in repository.lower():
                continue

            if score < RELEVANCE_THRESHOLD:
                continue

            source_info = {
                "content": row.get("content", "")[:200] + "...",
                "score": score,
            }

            if metadata.get("file_path"):
                source_info["file_path"] = metadata["file_path"]
            if metadata.get("repository"):
                source_info["repository"] = metadata["repository"]
            if metadata.get("url"):
                source_info["url"] = metadata["url"]
            if metadata.get("source_type"):
                source_info["source_type"] = metadata["source_type"]
            if metadata.get("title"):
                source_info["title"] = metadata["title"]

            sources.append(source_info)

        if len(sources) == 0 and len(filtered_rows) > 0:
            for row in filtered_rows[:3]:
                metadata = row.get("metadata", {})
                if "openchoreo" in metadata.get("repository", "").lower():
                    continue

                source_info = {
                    "content": row.get("content", "")[:200] + "...",
                    "score": row.get("score", 0.0),
                }

                if metadata.get("file_path"):
                    source_info["file_path"] = metadata["file_path"]
                if metadata.get("repository"):
                    source_info["repository"] = metadata["repository"]
                if metadata.get("url"):
                    source_info["url"] = metadata["url"]
                if metadata.get("source_type"):
                    source_info["source_type"] = metadata["source_type"]
                if metadata.get("title"):
                    source_info["title"] = metadata["title"]

                sources.append(source_info)
        else:
            sources = sources[:3]

        # 5. Use LLM-powered repo matcher to extract available repo URLs from context
        repo_matcher = get_llm_repo_matcher()

        # Extract repo URLs from both context text and source metadata
        context_urls = repo_matcher.extract_repo_urls_from_context(context_text)
        source_urls = repo_matcher.extract_repo_urls_from_sources(context_rows)

        # Combine URLs
        all_extracted_urls = list(set(context_urls + source_urls))

        # Check if user is asking for ALL repositories or all Choreo repositories
        query_lower = question.lower()
        is_requesting_all_repos = any(pattern in query_lower for pattern in [
            'all repos', 'all repositories', 'give me all',
            'list all repo', 'show all repo', 'provide all repo',
            'all wso2-enterprise', 'all 154', 'how many repo'
        ])

        is_requesting_choreo_repos = any(pattern in query_lower for pattern in [
            'all choreo repo', 'choreo keyword repo', 'choreo related repo',
            'repos with choreo', 'repositories with choreo'
        ])

        # Check if user is asking for a SPECIFIC repository
        is_requesting_specific_repo = any(pattern in query_lower for pattern in [
            'repo url', 'repository url', 'repo of', 'repository of',
            'repo contains', 'repository contains', 'repo for',
            'which repo has', 'what repo', 'find repo', 'locate repo',
            'give me repo'
        ]) and not (is_requesting_all_repos or is_requesting_choreo_repos)

        # If asking about repositories in general (not specific component), get more repos
        is_general_repo_query = any(keyword in query_lower for keyword in [
            'list repo', 'available repo'
        ])

        if is_general_repo_query or len(all_extracted_urls) < 5:
            # Query database for more Choreo repos
            db_repos = repo_matcher.get_all_choreo_repos_from_db(vector_client, top_k=50)
            all_extracted_urls = list(set(all_extracted_urls + db_repos))

            # Use registry as fallback if still not enough
            all_extracted_urls = repo_matcher.enhance_with_registry_fallback(all_extracted_urls)

        # Generate enhanced system prompt with available repo URLs
        system_prompt = repo_matcher.generate_enhanced_system_prompt(
            base_context=context_text,
            context_urls=all_extracted_urls,
            source_urls=[]  # Already combined above
        )

        # Add diagram generation enhancement if this is a diagram query
        if is_diagram_query:
            diagram_enhancement = diagram_service.generate_diagram_prompt_enhancement(
                question, diagram_type
            )
            system_prompt += f"\n\n{diagram_enhancement}"
            monitoring.log_info(
                "Added diagram generation instructions to system prompt (streaming)",
                logger_type='ai',
                diagram_type=diagram_type or "general"
            )


        messages = conversation_memory_manager.build_llm_messages(
            question=question,
            context=context_text,
            recent_messages=recent_messages,
            summary=summary,
            system_prompt=system_prompt
        )

        # 6. Stream response from LLM
        async def generate():
            try:
                # Special handling: If user is asking for a specific repo, search and return
                if is_requesting_specific_repo:
                    monitoring.log_info(
                        f"Specific repository search requested in stream: {question[:100]}",
                        logger_type='ai'
                    )

                    try:
                        # Extract search term
                        search_term = question.lower()
                        for prefix in ['repo url of the', 'repo url of', 'repository url of the', 'repository url of',
                                     'repo of the', 'repo of', 'repository of the', 'repository of',
                                     'repo contains the', 'repo contains', 'repository contains the', 'repository contains',
                                     'repo for the', 'repo for', 'repository for the', 'repository for',
                                     'which repo has', 'what repo has', 'give me repo url of the', 'give me repo url of',
                                     'find repo for', 'locate repo for']:
                            if prefix in search_term:
                                search_term = search_term.split(prefix, 1)[1].strip()
                                break

                        search_term = search_term.replace('?', '').replace('the ', '').strip()

                        if search_term:
                            repo = repo_matcher.find_repository_by_name(search_term)

                            if repo:
                                formatted_response = repo_matcher.format_single_repo_response(repo, search_term)

                                # Send empty sources first
                                yield f"data: {json.dumps({'sources': []})}\n\n"

                                # Stream the formatted response
                                for char in formatted_response:
                                    yield f"data: {json.dumps({'content': char})}\n\n"
                                    await asyncio.sleep(0.001)

                                # Send done signal
                                yield f"data: {json.dumps({'done': True})}\n\n"

                                monitoring.log_info(
                                    f"Successfully returned specific repository: {repo.get('name')}",
                                    logger_type='ai'
                                )
                                return

                    except Exception as e:
                        monitoring.log_error(
                            f"Failed to search for specific repository: {e}",
                            logger_type='ai',
                            exc_info=True
                        )
                        # Fall through to normal processing

                # Special handling: If user is asking for ALL repos, fetch and return directly
                if is_requesting_all_repos or is_requesting_choreo_repos:
                    monitoring.log_info(
                        f"Direct repository list requested: all_repos={is_requesting_all_repos}, choreo_repos={is_requesting_choreo_repos}",
                        logger_type='ai'
                    )

                    try:
                        # Fetch repos dynamically from GitHub
                        if is_requesting_choreo_repos:
                            repos = repo_matcher.get_all_wso2_enterprise_repos(keyword="choreo")
                            formatted_response = repo_matcher.format_repos_for_response(
                                repos,
                                query_context="with 'choreo' keyword"
                            )
                        else:
                            repos = repo_matcher.get_all_wso2_enterprise_repos(keyword=None)
                            formatted_response = repo_matcher.format_repos_for_response(
                                repos,
                                query_context="from wso2-enterprise organization"
                            )

                        # Send empty sources first
                        yield f"data: {json.dumps({'sources': []})}\n\n"

                        # Stream the formatted response
                        for char in formatted_response:
                            yield f"data: {json.dumps({'content': char})}\n\n"
                            await asyncio.sleep(0.001)  # Small delay for smooth streaming

                        # Send done signal
                        yield f"data: {json.dumps({'done': True})}\n\n"

                        monitoring.log_info(
                            f"Successfully returned {len(repos)} repositories",
                            logger_type='ai'
                        )
                        return

                    except Exception as e:
                        monitoring.log_error(
                            f"Failed to fetch repositories dynamically: {e}",
                            logger_type='ai',
                            exc_info=True
                        )
                        # Fall through to normal LLM response

                # Normal flow: Validate URLs in sources FIRST and send them early
                validated_sources = await url_validator.validate_and_filter_sources(sources)

                # Send sources IMMEDIATELY at the start of stream (before content)
                monitoring.log_info(
                    f"Sending {len(validated_sources)} sources at stream start",
                    logger_type='ai'
                )
                yield f"data: {json.dumps({'sources': validated_sources})}\n\n"

                # Collect the full answer first for URL validation
                full_answer = ""

                # Stream from Azure OpenAI
                monitoring.log_info(
                    "Starting Azure OpenAI streaming request",
                    logger_type='ai'
                )

                response = llm_service.client.chat.completions.create(
                    model=llm_service.deployment,
                    messages=messages,
                    max_tokens=10000,
                    temperature=0.7,
                    stream=True
                )

                # Collect full response
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            full_answer += delta.content

                monitoring.log_info(
                    f"Azure OpenAI response collected, length: {len(full_answer)}",
                    logger_type='ai'
                )

                # Validate URLs in the complete answer using LLM intelligence + HTTP checks
                filtered_answer, url_validation_map = await url_validator.validate_answer_urls(
                    answer=full_answer,
                    llm_service=llm_service,
                    context=context_text
                )

                # Log URL validation results
                if url_validation_map:
                    valid_count = sum(1 for v in url_validation_map.values() if v)
                    invalid_count = len(url_validation_map) - valid_count
                    monitoring.log_info(
                        f"Streaming URL validation completed",
                        logger_type='ai',
                        valid_urls=valid_count,
                        invalid_urls=invalid_count
                    )

                # Stream the filtered answer word by word to maintain progressive feel
                words = filtered_answer.split(' ')
                for word in words:
                    yield f"data: {json.dumps({'content': word + ' '})}\n\n"
                    # Small delay to simulate progressive streaming
                    await asyncio.sleep(0.01)

                # Send memory stats and summary separately
                if enable_summarization:
                    memory_metadata = {"memory_stats": memory_stats}
                    if summary:
                        memory_metadata["summary"] = summary.to_dict()
                        memory_metadata["summary_metadata"] = {
                            "topics_covered": summary.topics_covered,
                            "key_questions": summary.key_questions,
                            "important_decisions": summary.important_decisions
                        }
                    yield f"data: {json.dumps(memory_metadata)}\n\n"

                # Add URL validation info if validation was performed
                if url_validation_map:
                    enable_url_validation = os.getenv("ENABLE_URL_VALIDATION", "true").lower() == "true"
                    url_metadata = {
                        "url_validation": {
                            "total_urls": len(url_validation_map),
                            "valid_urls": sum(1 for v in url_validation_map.values() if v),
                            "invalid_urls": sum(1 for v in url_validation_map.values() if not v),
                            "validation_enabled": enable_url_validation
                        }
                    }
                    yield f"data: {json.dumps(url_metadata)}\n\n"

                # Send done signal
                yield "data: [DONE]\n\n"

                monitoring.log_info(
                    f"Streaming AI request completed",
                    logger_type='ai',
                    context_count=len(similar_rows)
                )
            except Exception as e:
                monitoring.log_error(
                    f"Streaming generator failed - {type(e).__name__}: {str(e)}",
                    logger_type='ai',
                    exc_info=True,
                    error_type=type(e).__name__,
                    error_details=str(e)
                )
                error_msg = {"error": f"{type(e).__name__}: {str(e)}"}
                yield f"data: {json.dumps(error_msg)}\n\n"

        # Add headers to prevent buffering in proxies/gateways
        headers = {
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
            "Connection": "keep-alive"
        }

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers=headers
        )

    except Exception as e:
        monitoring.log_error(
            f"Streaming AI request setup failed - {type(e).__name__}: {str(e)}",
            logger_type='ai',
            exc_info=True,
            error_type=type(e).__name__
        )
        monitoring.record_error()

        # Return error as JSON instead of raising to provide better client feedback
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "error": type(e).__name__,
                "message": str(e),
                "detail": "Failed to process streaming request. Check server logs for details."
            }
        )

@app.post("/api/ask_graph")
def ask_ai_graph(question: str):
    # Ensure services are initialized
    if not services_initialized:
        initialize_services()

    start_time = time.time()
    try:
        monitoring.log_info(
            f"Graph AI request received",
            logger_type='ai',
            question_length=len(question)
        )

        state = rag.invoke({"question": question})
        answer = state.get("answer")
        docs = state.get("docs") or []

        # Record AI inference metrics
        inference_duration = time.time() - start_time
        monitoring.record_ai_inference(
            duration=inference_duration,
            success=True,
            input_tokens=len(question.split()),
            output_tokens=len(str(answer).split())
        )

        monitoring.log_info(
            f"Graph AI request completed",
            logger_type='ai',
            duration=f"{inference_duration:.2f}s",
            context_count=len(docs)
        )
        return {"answer": answer, "context_count": len(docs)}

    except Exception as e:
        monitoring.log_error(
            f"Graph AI request failed: {str(e)}",
            logger_type='ai',
            exc_info=True
        )
        monitoring.record_error()
        monitoring.record_ai_inference(
            duration=time.time() - start_time,
            success=False
        )
        raise

# Keep old endpoint for backward compatibility
@app.post("/ask_graph")
def ask_ai_graph_legacy(question: str):
    return ask_ai_graph(question)

@app.post("/api/ingest/github")
def ingest_github(repo_url: str = "https://github.com/wso2/docs-choreo-dev.git", branch: str = "main"):
    # Ensure services are initialized
    if not services_initialized:
        initialize_services()

    start_time = time.time()
    try:
        monitoring.log_info(
            f"Starting GitHub ingestion",
            logger_type='ingestion',
            repo=repo_url,
            branch=branch
        )

        result = ingestion_service.ingest_github_repo(repo_url, branch)

        # Record ingestion metrics
        duration = time.time() - start_time
        monitoring.log_info(
            f"GitHub ingestion completed",
            logger_type='ingestion',
            repo=repo_url,
            duration=f"{duration:.2f}s",
            status=result.get("status"),
            files_processed=result.get("files_processed", {})
        )
        return {"repo_url": repo_url, "branch": branch, **result}

    except Exception as e:
        duration = time.time() - start_time
        monitoring.log_error(
            f"GitHub ingestion failed: {str(e)}",
            logger_type='ingestion',
            exc_info=True,
            repo=repo_url,
            duration=f"{duration:.2f}s"
        )
        monitoring.record_error()
        raise

@app.post("/api/ingest/github/with-images")
def ingest_github_with_images(repo_url: str = "https://github.com/wso2/docs-choreo-dev.git", branch: str = "main"):
    """Ingest both markdown files and images from a GitHub repository."""
    # Ensure services are initialized
    if not services_initialized:
        initialize_services()

    if not image_service:
        return {
            "status": "error",
            "message": "Google Vision API is not configured. Please add GOOGLE_VISION_API_KEY to your .env file."
        }
    result = ingestion_service.ingest_github_repo_with_images(repo_url, branch)
    return {"repo_url": repo_url, "branch": branch, **result}

@app.post("/api/ingest/org")
def ingest_organization_repos(org: str, keyword: str = "", max_repos: int = None):
    """
    Ingest all markdown files from repositories in an organization, optionally filtered by keyword.

    Args:
        org: Organization name (e.g., 'wso2-enterprise')
        keyword: Optional keyword to filter repositories (e.g., 'choreo')
        max_repos: Optional maximum number of repositories to process

    Returns:
        Summary statistics of the bulk ingestion process
    """
    # Ensure services are initialized
    if not services_initialized:
        initialize_services()

    result = ingestion_service.ingest_org_repositories(org, keyword, max_repos)
    return result

# Keep old endpoint for backward compatibility
@app.post("/ingest/github")
def ingest_github_legacy(repo_url: str = "https://github.com/wso2/docs-choreo-dev.git", branch: str = "main"):
    return ingest_github(repo_url, branch)

@app.post("/api/webhook/github")
async def github_webhook(request: Request):
    # Minimal webhook: on push, reingest the repo URL from payload if present
    payload = await request.json()
    repo = (payload.get("repository") or {}).get("html_url")
    ref = payload.get("ref", "refs/heads/main")
    branch = ref.split("/")[-1] if ref else "main"
    if repo:
        try:
            result = ingestion_service.ingest_github_repo(repo, branch)
            return {"status": "ok", "ingested": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "ignored"}

# Keep old endpoint for backward compatibility
@app.post("/webhook/github")
async def github_webhook_legacy(request: Request):
    return await github_webhook(request)
