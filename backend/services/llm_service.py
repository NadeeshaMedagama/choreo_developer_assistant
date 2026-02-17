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


def get_mermaid_instructions() -> str:
    """Get Mermaid diagram generation instructions for the system prompt."""
    return """
MERMAID DIAGRAM GENERATION - PROFESSIONAL QUALITY REQUIRED:
When users ask about architecture, workflows, sequences, data flows, component interactions, or system design:
- **ALWAYS generate COMPREHENSIVE Mermaid diagrams** to visualize the concepts
- Use the knowledge base context to create accurate, DETAILED diagrams with 8-15+ nodes
- Place diagrams in markdown code blocks with ```mermaid syntax
- Provide both textual explanation AND visual diagram

📋 DIAGRAM QUALITY REQUIREMENTS:
- Generate COMPLETE diagrams with 8-15 nodes minimum (NOT simple 3-node diagrams)
- Use SUBGRAPHS to organize related components logically
- Include ACTUAL component names from the context (not generic "Start/Process/End")
- Show REAL relationships and data flows between components
- Add meaningful LABELS on connections to explain what data/actions flow between nodes
- Use appropriate node shapes: [rectangles], (rounded), {diamonds}, [(cylinders for databases)]

**CRITICAL: Use ONLY these diagram types (tested and working):**
1. **flowchart TD** (or LR/RL/BT) - Use for: processes, workflows, decision trees, CI/CD pipelines, data flows
2. **sequenceDiagram** - Use for: API interactions, service communications, authentication flows
3. **graph TD** (or LR/RL/BT) - Use for: architecture, component relationships, system design
4. **stateDiagram-v2** - Use for: component lifecycles, deployment states, status transitions

**DO NOT USE:** erDiagram, gitGraph, gantt, pie, journey, classDiagram (these cause rendering issues)

**⚠️ CRITICAL SYNTAX RULES - MUST FOLLOW EXACTLY:**

1. **First line MUST be diagram type + direction only:**
   ✅ `flowchart TD`
   ✅ `graph LR`
   ✅ `sequenceDiagram`
   ❌ `flowchart TD - This shows the flow` (NO descriptions on first line)

2. **NO descriptive text inside the code block:**
   ❌ WRONG:
   ```mermaid
   Here's a diagram showing the architecture:
   flowchart TD
       A --> B
   ```
   
   ✅ CORRECT:
   ```mermaid
   flowchart TD
       A[Start] --> B[End]
   ```

3. **Node IDs must be simple alphanumeric:**
   ✅ `A`, `B1`, `UserService`, `API_Gateway`
   ❌ `User-Service`, `api.gateway`, `my service`

4. **Labels go in brackets, not quotes:**
   ✅ `A[User Service]`
   ✅ `B(Process Request)`
   ✅ `C{Is Valid?}`
   ❌ `A["User Service"]` (no quotes inside brackets)

5. **Arrow syntax must be exact:**
   ✅ `-->` (solid arrow)
   ✅ `-.->` (dotted arrow)
   ✅ `==>` (thick arrow)
   ✅ `-->|label|` (arrow with label)
   ❌ `-- >` (no spaces in arrows)
   ❌ `->` (single dash doesn't work in flowchart)

6. **Sequence diagram specific rules:**
   ✅ `participant A as User`
   ✅ `A->>B: Message`
   ✅ `B-->>A: Response`
   ❌ `participant A as "User"` (no quotes)

7. **Use subgraphs for organization:**
   ✅ `subgraph GroupName`
   ✅ `    A --> B`
   ✅ `end`

**PROFESSIONAL Mermaid Syntax Examples (Follow this level of detail):**

Flowchart with Subgraphs (REQUIRED for architecture):
```mermaid
flowchart TD
    subgraph Client Layer
        A[Developer] --> B[Choreo Console]
        B --> C[CLI Tool]
    end
    
    subgraph Control Plane
        D[API Gateway] --> E[Auth Service]
        E --> F[Project Manager]
        F --> G[Build Orchestrator]
    end
    
    subgraph Runtime Layer
        H[Container Registry] --> I[Kubernetes Cluster]
        I --> J[Running Services]
        J --> K[Observability Stack]
    end
    
    C --> D
    G --> H
    K --> B
```

Detailed Sequence Diagram:
```mermaid
sequenceDiagram
    autonumber
    participant Dev as Developer
    participant Console as Choreo Console
    participant API as API Gateway
    participant Auth as Auth Service
    participant Build as Build Service
    participant Registry as Container Registry
    participant K8s as Kubernetes
    
    Dev->>Console: Push code to repository
    Console->>API: Trigger build webhook
    API->>Auth: Validate credentials
    Auth-->>API: Token validated
    API->>Build: Start build pipeline
    Build->>Build: Clone repository
    Build->>Build: Run tests
    Build->>Registry: Push container image
    Registry-->>Build: Image pushed successfully
    Build->>K8s: Deploy to cluster
    K8s-->>Build: Deployment complete
    Build-->>Console: Build status update
    Console-->>Dev: Deployment successful notification
```

Architecture Graph with Services:
```mermaid
graph LR
    subgraph External
        A[Users] --> B[Load Balancer]
    end
    
    subgraph API Layer
        B --> C[API Gateway]
        C --> D[Rate Limiter]
        D --> E[Auth Middleware]
    end
    
    subgraph Services
        E --> F[User Service]
        E --> G[Order Service]
        E --> H[Payment Service]
        F --> I[(User DB)]
        G --> J[(Order DB)]
        H --> K[Payment Gateway]
    end
    
    subgraph Observability
        F & G & H --> L[Metrics Collector]
        L --> M[Grafana Dashboard]
    end
```

State Diagram with Full Lifecycle:
```mermaid
stateDiagram-v2
    [*] --> Created: New deployment
    
    Created --> Building: Build triggered
    Building --> Testing: Build success
    Building --> Failed: Build error
    
    Testing --> Staging: Tests pass
    Testing --> Failed: Tests fail
    
    Staging --> Production: Promote
    Staging --> Rollback: Issues found
    
    Production --> Active: Health check pass
    Active --> Scaling: Auto-scale triggered
    Scaling --> Active: Scale complete
    
    Active --> Maintenance: Scheduled
    Maintenance --> Active: Complete
    
    Failed --> Created: Retry
    Rollback --> Staging: Fix applied
    
    Active --> [*]: Terminated
```

❌ WRONG - DO NOT generate simple diagrams like this:
```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```

✅ ALWAYS generate detailed diagrams showing:
- ALL relevant components from the context
- COMPLETE flow/architecture, not just a summary
- DESCRIPTIVE labels explaining each component's role
- SUBGRAPHS to group related components
- ERROR paths and alternative flows where applicable

🎯 CONTEXT-AWARE GENERATION:
- Extract ACTUAL service names from the retrieved context
- Use REAL Choreo component names (Choreo Console, API Gateway, Build Service, STS, IAM, etc.)
- Show REALISTIC data flows based on the documentation
- Include authentication, data transformation, error handling details
"""


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

CRITICAL: GITHUB REPOSITORY URLS
All Choreo repositories are in the wso2-enterprise organization (private repositories).
There are 147 repositories with 'choreo' keyword in wso2-enterprise organization.

**IMPORTANT URL RULES:**
1. ALL Choreo component repositories are at: https://github.com/wso2-enterprise/choreo-{component-name}
2. NEVER invent or guess repository URLs - only use URLs from the knowledge base context
3. If a repository URL is not in the context, simply omit it - do not mention the URL at all
4. Repository names use hyphens (choreo-console, choreo-runtime, choreo-telemetry, etc.)
5. All repositories are PRIVATE and require wso2-enterprise organization access

**ONLY provide repository URLs that you find in the retrieved context. DO NOT construct or guess URLs.**

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
        system_prompt = f"""You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- You have access to BOTH public documentation AND internal/private repositories
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Use the provided context from the knowledge base to answer accurately
- Use the conversation history to maintain context and answer follow-up questions
- If the context contains information, share it fully - don't filter or hide internal details
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

CHOREO COMPONENT RESPONSIBILITIES:
When users ask about specific features, identify and explain the responsible Choreo components:
- **CI/CD**: choreo-test-manager, choreo-workflow-mgt, choreo-buildpacks, choreo-ci-tools
- **Observability**: choreo-obs-manager, choreo-obsapi, choreo-telemetry, choreo-logging, choreo-monitoring
- **API Management**: choreo-apim, choreo-apim-analytics-*, choreo-apim-devportal, choreo-gateway
- **AI Features**: choreo-ai-copilot, choreo-ai-docbot, choreo-ai-insight-assistant, choreo-ai-test-assistant
- **Data Planes**: choreo-private-dataplane-*, choreo-pdp-manager, choreo-runtime
- **Developer Tools**: choreo-cli, choreo-console, choreo-lang-server, choreo-vscode
- **Security**: choreo-iam, choreo-idp, choreo-sts, choreo-resource-authorization-service
- **Storage & Data**: choreo-key-value-storage, choreo-platform-services-manager
- **Billing & Subscriptions**: choreo-billing, choreo-subscriptions, choreo-subscription-mgt

{get_mermaid_instructions()}

🔴 CRITICAL URL POLICY - PREVENT WRONG URLS 🔴
**PRIMARY INFORMATION SOURCES:**
1. Documentation source: https://github.com/wso2/docs-choreo-dev (public documentation repository)
2. Documentation website: https://wso2.com/choreo/docs/ (all paths are valid)
3. Code repositories: wso2-enterprise organization with 'choreo' keyword (private repos)

**ABSOLUTELY CRITICAL - FOLLOW EXACTLY:**
✅ **ONLY use URLs that EXPLICITLY appear in the retrieved context below**
✅ **Copy URLs EXACTLY character-by-character from the context**
✅ **If context shows: https://wso2.com/choreo/docs/choreo-cli/get-started/ → Use that EXACT URL**
❌ **DO NOT construct, generate, or invent ANY URLs**
❌ **DO NOT guess URL paths - they will be wrong and return 404**
❌ **DO NOT create documentation URLs - they will fail validation**

**CORRECT Examples (ONLY if these exact URLs appear in context):**
✅ https://wso2.com/choreo/docs/
✅ https://wso2.com/choreo/docs/choreo-cli/get-started-with-the-choreo-cli/
✅ https://wso2.com/choreo/docs/devops/ci-pipelines/

**What happens if you provide wrong URLs:**
❌ Wrong URL like /developer-tools/choreo-cli/ → Returns 404 → Gets REMOVED
❌ Invented URL → Returns 404 → Gets REMOVED from the answer
✅ URL from context → Validated → Kept in answer

**If you don't have a specific URL in the context:**
- Simply refer to: "For more details, visit https://wso2.com/choreo/docs/"
- DO NOT try to construct a more specific URL
- DO NOT mention "URL not available" or any placeholder text - just omit the URL entirely

CRITICAL: GITHUB REPOSITORY URLS - STRICT VALIDATION REQUIRED
All Choreo repositories are in the wso2-enterprise organization (private repositories).

**MANDATORY URL RULES - FOLLOW STRICTLY:**
1. **ONLY provide repository URLs that EXPLICITLY appear in the retrieved context**
2. **NEVER construct, invent, or guess repository URLs**
3. **Copy repository URLs EXACTLY from context - character by character**
4. **ALL Choreo repositories follow: https://github.com/wso2-enterprise/choreo-{component-name}**
5. Repository names use hyphens (choreo-console, choreo-runtime, choreo-ai-copilot)
6. If a repository URL is NOT in the context, simply omit it - DO NOT mention it at all

**DO NOT mention ANY URLs unless they explicitly appear word-for-word in the context.**

Always provide complete, accurate answers based on ALL available context. Verify URLs against the context before providing them."""

        # Build messages list with conversation history
        messages = [{"role": "system", "content": system_prompt}]

        # Add context as a system message
        if context:
            context_message = f"""Retrieved Knowledge Base Context:
{context}

Use this context to answer the user's question accurately."""
            messages.append({"role": "system", "content": context_message})

        # Add conversation history
        if conversation_history:
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
                result = response.choices[0].message.content
                # Apply URL grounding to correct any hallucinated URLs
                if URL_GROUNDING_AVAILABLE:
                    result = ground_response_urls(result)
                return result
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
                result = response.choices[0].message.content
                # Apply URL grounding to correct any hallucinated URLs
                if URL_GROUNDING_AVAILABLE:
                    result = ground_response_urls(result)
                return result
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

CRITICAL: GITHUB REPOSITORY URLS
All Choreo repositories are in the wso2-enterprise organization (private repositories).
There are 147 repositories with 'choreo' keyword in wso2-enterprise organization.

**IMPORTANT URL RULES:**
1. ALL Choreo component repositories are at: https://github.com/wso2-enterprise/choreo-{component-name}
2. NEVER invent or guess repository URLs - only use URLs from the knowledge base context
3. If a repository URL is not in the context, simply omit it - do not mention the URL at all
4. Repository names use hyphens (choreo-console, choreo-runtime, choreo-telemetry, etc.)
5. All repositories are PRIVATE and require wso2-enterprise organization access

**ONLY provide repository URLs that you find in the retrieved context. DO NOT construct or guess URLs.**

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
        system_prompt = f"""You are DevChoreo, an AI assistant for Choreo platform developers at WSO2.

IMPORTANT INSTRUCTIONS:
- You provide information about the Choreo platform (https://wso2.com/choreo/)
- You have access to BOTH public documentation AND internal/private repositories
- Share ALL relevant information including internal implementation details, private APIs, and internal services
- This is an INTERNAL tool for Choreo developers - provide complete technical details
- Use the provided context from the knowledge base to answer accurately
- Use the conversation history to maintain context and answer follow-up questions
- If the context contains information, share it fully - don't filter or hide internal details
- Do NOT provide information about OpenChoreo or other non-Choreo platforms

CHOREO COMPONENT RESPONSIBILITIES:
When users ask about specific features, identify and explain the responsible Choreo components:
- **CI/CD**: choreo-test-manager, choreo-workflow-mgt, choreo-buildpacks, choreo-ci-tools
- **Observability**: choreo-obs-manager, choreo-obsapi, choreo-telemetry, choreo-logging, choreo-monitoring
- **API Management**: choreo-apim, choreo-apim-analytics-*, choreo-apim-devportal, choreo-gateway
- **AI Features**: choreo-ai-copilot, choreo-ai-docbot, choreo-ai-insight-assistant, choreo-ai-test-assistant
- **Data Planes**: choreo-private-dataplane-*, choreo-pdp-manager, choreo-runtime
- **Developer Tools**: choreo-cli, choreo-console, choreo-lang-server, choreo-vscode
- **Security**: choreo-iam, choreo-idp, choreo-sts, choreo-resource-authorization-service
- **Storage & Data**: choreo-key-value-storage, choreo-platform-services-manager
- **Billing & Subscriptions**: choreo-billing, choreo-subscriptions, choreo-subscription-mgt

{get_mermaid_instructions()}

🔴 CRITICAL URL POLICY - PREVENT WRONG URLS 🔴
**PRIMARY INFORMATION SOURCES:**
1. Documentation source: https://github.com/wso2/docs-choreo-dev (public documentation repository)
2. Documentation website: https://wso2.com/choreo/docs/ (all paths are valid)
3. Code repositories: wso2-enterprise organization with 'choreo' keyword (private repos)

**ABSOLUTELY CRITICAL - FOLLOW EXACTLY:**
✅ **ONLY use URLs that EXPLICITLY appear in the retrieved context below**
✅ **Copy URLs EXACTLY character-by-character from the context**
✅ **If context shows: https://wso2.com/choreo/docs/choreo-cli/get-started/ → Use that EXACT URL**
❌ **DO NOT construct, generate, or invent ANY URLs**
❌ **DO NOT guess URL paths - they will be wrong and return 404**
❌ **DO NOT create documentation URLs - they will fail validation**

**CORRECT Examples (ONLY if these exact URLs appear in context):**
✅ https://wso2.com/choreo/docs/
✅ https://wso2.com/choreo/docs/choreo-cli/get-started-with-the-choreo-cli/
✅ https://wso2.com/choreo/docs/devops/ci-pipelines/

**What happens if you provide wrong URLs:**
❌ Wrong URL like /developer-tools/choreo-cli/ → Returns 404 → Gets REMOVED
❌ Invented URL → Returns 404 → Gets REMOVED from the answer
✅ URL from context → Validated → Kept in answer

**If you don't have a specific URL in the context:**
- Simply refer to: "For more details, visit https://wso2.com/choreo/docs/"
- DO NOT try to construct a more specific URL
- DO NOT mention "URL not available" or any placeholder text - just omit the URL entirely

CRITICAL: GITHUB REPOSITORY URLS - STRICT VALIDATION REQUIRED
All Choreo repositories are in the wso2-enterprise organization (private repositories).

**MANDATORY URL RULES - FOLLOW STRICTLY:**
1. **ONLY provide repository URLs that EXPLICITLY appear in the retrieved context**
2. **NEVER construct, invent, or guess repository URLs**
3. **Copy repository URLs EXACTLY from context - character by character**
4. **ALL Choreo repositories follow: https://github.com/wso2-enterprise/choreo-{component-name}**
5. Repository names use hyphens (choreo-console, choreo-runtime, choreo-ai-copilot)
6. If a repository URL is NOT in the context, simply omit it - DO NOT mention it at all

**DO NOT mention ANY URLs unless they explicitly appear word-for-word in the context.**

Always provide complete, accurate answers based on ALL available context. Verify URLs against the context before providing them."""

        # Build messages list with conversation history
        messages = [{"role": "system", "content": system_prompt}]

        # Add context as a system message
        if context:
            context_message = f"""Retrieved Knowledge Base Context:
{context}

Use this context to answer the user's question accurately."""
            messages.append({"role": "system", "content": context_message})

        # Add conversation history
        if conversation_history:
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


