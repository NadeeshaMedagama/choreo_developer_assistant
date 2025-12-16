from typing import List, Union, Optional
import sys
import gc
from pathlib import Path

# Add backend to path if needed
backend_path = Path(__file__).parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from utils.logger import get_logger

logger = get_logger(__name__)


class LLMService:
    """Service for generating embeddings and LLM responses using various providers."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        use_openai: bool = False,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None
    ):
        self.model_name = model_name
        self.use_openai = use_openai
        self.endpoint = endpoint
        self.api_key = api_key
        self.deployment = deployment
        self.api_version = api_version
        self.embeddings_deployment = None
        self.model = None
        self.embedding_dimension = None
        self.use_azure = endpoint is not None and "azure" in endpoint.lower()
        self.embedding_call_count = 0  # Track calls for memory management

        if self.use_azure:
            self._init_azure_openai()
        elif use_openai:
            self._init_openai()
        else:
            self._init_sentence_transformer()

    def set_embeddings_deployment(self, deployment: str):
        """Set a separate deployment name for embeddings."""
        self.embeddings_deployment = deployment
        logger.info(f"Embeddings deployment set to: {deployment}")

    def _init_azure_openai(self):
        """Initialize Azure OpenAI."""
        try:
            from openai import AzureOpenAI

            logger.info(f"Initializing Azure OpenAI with endpoint: {self.endpoint}")
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version or "2024-02-15-preview",
                azure_endpoint=self.endpoint
            )
            self.embedding_dimension = 1536  # Default for text-embedding-ada-002
            logger.info("Azure OpenAI initialized successfully")
        except ImportError:
            raise RuntimeError("OpenAI SDK not installed. Install with: pip install openai")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI: {e}")
            raise

    def _init_openai(self):
        """Initialize OpenAI embeddings."""
        try:
            from openai import OpenAI
            import os

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found in environment")

            self.client = OpenAI(api_key=api_key)
            self.embedding_dimension = 1536  # text-embedding-ada-002 dimension
            logger.info("Initialized OpenAI embeddings")
        except ImportError:
            raise RuntimeError("OpenAI not installed. Install with: pip install openai")

    def _init_sentence_transformer(self):
        """Initialize SentenceTransformer embeddings."""
        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading SentenceTransformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Model loaded. Embedding dimension: {self.embedding_dimension}")
        except ImportError:
            raise RuntimeError("sentence-transformers not installed. Install with: pip install sentence-transformers")

    def clear_model_cache(self):
        """Clear model cache to free memory. Call this periodically during large ingestion."""
        if not self.use_openai and not self.use_azure and self.model is not None:
            try:
                # Try to clear CUDA cache if using GPU
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info("Cleared CUDA cache")
            except ImportError:
                pass

            # Force garbage collection
            gc.collect()
            logger.info("Cleared model cache and ran garbage collection")

    def reinitialize_model(self):
        """Reinitialize the model to completely free memory. Use this sparingly."""
        if not self.use_openai and not self.use_azure:
            logger.info("Reinitializing SentenceTransformer model to free memory...")

            # Delete old model
            del self.model
            gc.collect()

            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except ImportError:
                pass

            # Reload model
            self._init_sentence_transformer()
            self.embedding_call_count = 0
            logger.info("Model reinitialized successfully")

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        if self.use_azure:
            deployment = self.embeddings_deployment or self.deployment
            response = self.client.embeddings.create(
                input=text,
                model=deployment
            )
            return response.data[0].embedding
        elif self.use_openai:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        else:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding.tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts with memory management."""
        if self.use_azure:
            deployment = self.embeddings_deployment or self.deployment
            embeddings = []
            # Process in VERY SMALL batches for Azure OpenAI to prevent memory spikes
            batch_size = 5  # Reduced from 10 to 5 for better memory management
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                try:
                    response = self.client.embeddings.create(
                        input=batch,
                        model=deployment
                    )
                    batch_embeddings = [item.embedding for item in response.data]
                    embeddings.extend(batch_embeddings)

                    # **IMMEDIATE CLEANUP** - Free response object
                    del response, batch_embeddings

                    # Force garbage collection after EVERY batch (not just every 50)
                    gc.collect()

                    # Log progress for transparency
                    if (i // batch_size + 1) % 2 == 0:
                        logger.debug(f"Processed {i + len(batch)}/{len(texts)} embeddings")

                except Exception as e:
                    logger.error(f"Failed to get embeddings for batch {i//batch_size}: {e}")
                    raise
            return embeddings
        elif self.use_openai:
            embeddings = []
            # Process in SMALLER batches for OpenAI
            batch_size = 10  # Reduced from 100 to 10
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                response = self.client.embeddings.create(
                    input=batch,
                    model="text-embedding-ada-002"
                )
                embeddings.extend([item.embedding for item in response.data])

                # Force garbage collection after each batch
                if i > 0 and i % 50 == 0:
                    gc.collect()

            return embeddings
        else:
            # SentenceTransformer with memory management
            embeddings = self.model.encode(
                texts,
                convert_to_tensor=False,
                show_progress_bar=False,  # Disable progress bar to reduce overhead
                batch_size=32  # Process in smaller internal batches
            )

            # Increment call count and clear cache periodically
            self.embedding_call_count += 1

            # Clear cache every 10 calls
            if self.embedding_call_count % 10 == 0:
                self.clear_model_cache()

            # Reinitialize model every 50 calls to fully reset memory
            if self.embedding_call_count % 50 == 0:
                logger.info(f"Reloading model after {self.embedding_call_count} embedding calls")
                self.reinitialize_model()

            result = [emb.tolist() for emb in embeddings]

            # Clear embeddings from memory
            del embeddings
            gc.collect()

            return result

    def get_response(self, prompt: str, max_tokens: int = 4096) -> str:
        """Generate a text response using LLM."""
        system_prompt = """You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

If asked about OpenChoreo:
"I'm DevChoreo, an AI assistant for the Choreo platform. I notice you're asking about OpenChoreo, which is a different platform. I can only help with questions about WSO2's Choreo platform. Would you like to know about Choreo platform instead?"

Always provide complete, accurate answers about the Choreo platform."""

        if self.use_azure:
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Azure OpenAI response failed: {e}")
                return f"Error generating response: {str(e)}"
        elif self.use_openai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI response failed: {e}")
                return f"Error generating response: {str(e)}"
        else:
            return "LLM response generation not available with SentenceTransformer model."

    def get_response_with_history(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[dict]] = None,
        max_tokens: int = 4096
    ) -> str:
        """Generate a text response using LLM with conversation history and retrieved context."""
        system_prompt = """You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- You have access to BOTH public documentation AND internal/private repositories
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Use the provided context from the knowledge base to answer accurately
- Use the conversation history to maintain context and answer follow-up questions
- If the context contains information, share it fully - don't filter or hide internal details
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

REPOSITORY URLS - CRITICAL:
Each Choreo component has its OWN separate repository.
Choreo repositories are primarily in the wso2-enterprise organization (private repos with main information).

When mentioning Choreo components, use this URL format:
https://github.com/wso2-enterprise/choreo-{component-name}

Examples of Choreo component repositories (in wso2-enterprise):
  * choreo-console: https://github.com/wso2-enterprise/choreo-console
  * choreo-runtime: https://github.com/wso2-enterprise/choreo-runtime
  * choreo-telemetry: https://github.com/wso2-enterprise/choreo-telemetry
  * choreo-obsapi: https://github.com/wso2-enterprise/choreo-obsapi
  * choreo-linker: https://github.com/wso2-enterprise/choreo-linker
  * choreo-negotiator: https://github.com/wso2-enterprise/choreo-negotiator

IMPORTANT: 
- Each component is in its own separate repository
- Primary organization is wso2-enterprise (contains main Choreo information)
- Repository names have the "choreo-" prefix
- Use format: github.com/wso2-enterprise/choreo-{component}

Always provide complete, accurate answers based on ALL available context."""

        # Build messages list with conversation history
        messages = [{"role": "system", "content": system_prompt}]

        # Add context as a system message
        if context:
            context_message = f"""Retrieved Knowledge Base Context:
{context}

Use this context to answer the user's question accurately."""
            messages.append({"role": "system", "content": context_message})

        # Add conversation history (limit to recent messages to avoid token limits)
        if conversation_history:
            # Keep only recent history (last 10 messages = ~5 turns)
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

        # Add current question
        messages.append({"role": "user", "content": question})

        if self.use_azure:
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Azure OpenAI response failed: {e}")
                return f"Error generating response: {str(e)}"
        elif self.use_openai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI response failed: {e}")
                return f"Error generating response: {str(e)}"
        else:
            return "LLM response generation not available with SentenceTransformer model."

    def get_response_stream(self, prompt: str, max_tokens: int = 10000):
        """Generate a streaming text response using LLM."""
        system_prompt = """You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

If asked about OpenChoreo:
"I'm DevChoreo, an AI assistant for the Choreo platform by WSO2. I notice you're asking about OpenChoreo, which is a different platform. I can only help with questions about WSO2's Choreo platform. Would you like to know about Choreo platform instead?"

Always provide complete, accurate answers about the Choreo platform."""

        if self.use_azure:
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield delta.content
            except Exception as e:
                logger.error(f"Azure OpenAI streaming failed: {e}")
                yield f"Error generating response: {str(e)}"
        elif self.use_openai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield delta.content
            except Exception as e:
                logger.error(f"OpenAI streaming failed: {e}")
                yield f"Error generating response: {str(e)}"
        else:
            yield "LLM response generation not available with SentenceTransformer model."

    def get_response_stream_with_history(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[dict]] = None,
        max_tokens: int = 10000
    ):
        """Generate a streaming text response using LLM with conversation history and retrieved context."""
        system_prompt = """You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- You have access to BOTH public documentation AND internal/private repositories
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Use the provided context from the knowledge base to answer accurately
- Use the conversation history to maintain context and answer follow-up questions
- If the context contains information, share it fully - don't filter or hide internal details
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

Always provide complete, accurate answers based on ALL available context."""

        # Build messages list with conversation history
        messages = [{"role": "system", "content": system_prompt}]

        # Add context as a system message
        if context:
            context_message = f"""Retrieved Knowledge Base Context:
{context}

Use this context to answer the user's question accurately."""
            messages.append({"role": "system", "content": context_message})

        # Add conversation history (limit to recent messages to avoid token limits)
        if conversation_history:
            # Keep only recent history (last 10 messages = ~5 turns)
            recent_history = conversation_history[-10:]
            for msg in recent_history:
                if msg.get("role") in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

        # Add current question
        messages.append({"role": "user", "content": question})

        if self.use_azure:
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield delta.content
            except Exception as e:
                logger.error(f"Azure OpenAI streaming failed: {e}")
                yield f"Error generating response: {str(e)}"
        elif self.use_openai:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.7,
                    stream=True
                )
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, 'content') and delta.content:
                            yield delta.content
            except Exception as e:
                logger.error(f"OpenAI streaming failed: {e}")
                yield f"Error generating response: {str(e)}"
        else:
            yield "LLM response generation not available with SentenceTransformer model."

    def get_dimension(self) -> int:
        """Get the embedding dimension."""
        return self.embedding_dimension
