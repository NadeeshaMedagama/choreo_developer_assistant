"""
Service to detect diagram-related queries and enhance them with diagram knowledge.
"""
import re
from typing import List, Dict, Optional, Tuple


class DiagramDetectionService:
    """Detects when users ask about diagrams and enhances the query with diagram-specific context."""
    
    # Keywords that indicate diagram-related queries - ONLY explicit diagram requests
    DIAGRAM_KEYWORDS = [
        'diagram', 'diagrams', 'flowchart', 'sequence diagram',
        'visualization', 'visualize', 'illustrate', 'draw',
        'show me a diagram', 'create a diagram', 'generate a diagram',
        'show me a flowchart', 'architecture diagram',
        'er diagram', 'class diagram', 'uml',
        'draw me', 'draw a', 'visual representation'
    ]
    
    # Diagram type mappings (using only reliable Mermaid types)
    DIAGRAM_TYPE_MAPPINGS = {
        'flowchart': ['flow', 'workflow', 'process', 'pipeline', 'decision', 'step', 'data flow', 'build', 'deploy'],
        'sequence': ['sequence', 'interaction', 'api call', 'request', 'response', 'authentication', 'communication', 'message'],
        'graph': ['architecture', 'component', 'system', 'service', 'high level', 'overview', 'structure'],
        'state': ['state', 'lifecycle', 'transition', 'status', 'stage'],
    }
    
    def __init__(self):
        self.diagram_request_count = 0
    
    def is_diagram_query(self, query: str) -> bool:
        """
        Detect if the query is EXPLICITLY asking for a diagram or visualization.
        Only returns True when the user clearly wants a diagram, not for general questions.

        Args:
            query: User's question
            
        Returns:
            True if query explicitly requests a diagram
        """
        query_lower = query.lower()
        
        # Check for explicit diagram keywords
        for keyword in self.DIAGRAM_KEYWORDS:
            if keyword in query_lower:
                return True
        
        # Check for explicit "show me" + diagram-related patterns ONLY
        explicit_diagram_patterns = [
            r'show\s+(?:me\s+)?(?:a\s+|the\s+)?(?:diagram|flowchart|chart|graph|visualization|visual)',
            r'(?:create|generate|make|draw)\s+(?:a\s+|the\s+)?(?:diagram|flowchart|chart|graph|visualization|visual)',
            r'(?:can you|could you|please)\s+(?:draw|create|generate|make|visualize|illustrate)',
        ]
        
        for pattern in explicit_diagram_patterns:
            if re.search(pattern, query_lower):
                return True

        return False
    
    def detect_diagram_type(self, query: str) -> Optional[str]:
        """
        Detect what type of diagram would be most appropriate.
        
        Args:
            query: User's question
            
        Returns:
            Diagram type (flowchart, sequence, architecture, etc.) or None
        """
        query_lower = query.lower()
        
        # Score each diagram type
        type_scores = {}
        for diagram_type, keywords in self.DIAGRAM_TYPE_MAPPINGS.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                type_scores[diagram_type] = score
        
        if not type_scores:
            return None
        
        # Return the type with highest score
        return max(type_scores, key=type_scores.get)
    
    def enhance_query_for_diagrams(self, query: str, context: str = "") -> Tuple[str, Dict]:
        """
        Enhance the query to better retrieve diagram-related context.
        
        Args:
            query: Original user query
            context: Retrieved context from vector DB
            
        Returns:
            Tuple of (enhanced_query, metadata)
        """
        is_diagram_query = self.is_diagram_query(query)
        
        if not is_diagram_query:
            return query, {"is_diagram_query": False}
        
        self.diagram_request_count += 1
        diagram_type = self.detect_diagram_type(query)
        
        # Add diagram-specific search terms
        diagram_terms = [
            "architecture", "flow", "component", "interaction",
            "sequence", "diagram", "visualization", "process"
        ]
        
        # Build enhanced query
        enhanced_parts = [query]
        
        # Add diagram type if detected
        if diagram_type:
            enhanced_parts.append(f"{diagram_type} diagram")
        
        # Add general diagram terms
        enhanced_parts.extend(diagram_terms[:3])
        
        enhanced_query = " ".join(enhanced_parts)
        
        metadata = {
            "is_diagram_query": True,
            "diagram_type": diagram_type,
            "request_count": self.diagram_request_count,
            "original_query": query
        }
        
        return enhanced_query, metadata
    
    def generate_diagram_prompt_enhancement(self, query: str, diagram_type: Optional[str] = None) -> str:
        """
        Generate an enhancement to add to the system prompt for diagram generation.
        
        Args:
            query: User's question
            diagram_type: Detected diagram type
            
        Returns:
            Additional prompt text to emphasize diagram generation
        """
        if not diagram_type:
            diagram_type = self.detect_diagram_type(query) or "flowchart"

        # Map to correct Mermaid syntax
        mermaid_type_map = {
            'flowchart': 'flowchart TD',
            'sequence': 'sequenceDiagram',
            'graph': 'graph LR',
            'state': 'stateDiagram-v2'
        }

        mermaid_syntax = mermaid_type_map.get(diagram_type, 'flowchart TD')

        # Get comprehensive examples based on diagram type
        examples = {
            'flowchart TD': '''```mermaid
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
```''',
            'sequenceDiagram': '''```mermaid
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
```''',
            'graph LR': '''```mermaid
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
```''',
            'stateDiagram-v2': '''```mermaid
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
```'''
        }

        example = examples.get(mermaid_syntax, examples['flowchart TD'])

        return f"""
📊 DIAGRAM GENERATION REQUESTED - Generate a relevant, accurate diagram.

🎯 USER REQUEST TYPE: {mermaid_syntax} diagram
The user is explicitly asking for a visual explanation. Generate a PROFESSIONAL-GRADE diagram that is:
- RELEVANT and SPECIFIC to the user's question (not generic)
- ACCURATE based on actual Choreo architecture from the retrieved context
- Well-organized with subgraphs and meaningful labels

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 DIAGRAM QUALITY REQUIREMENTS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 📊 COMPLEXITY: Generate diagrams with 8-20 nodes as needed
2. 📦 ORGANIZATION: Use SUBGRAPHS to group related components
3. 🏷️ NAMING: Use ACTUAL component names from context (never "Start", "Process", "End")
4. 🔗 CONNECTIONS: Add meaningful LABELS on arrows explaining data/action flow
5. 🎨 SHAPES: Use appropriate shapes: [rectangles], (rounded), {"{"}diamonds{"}"}, [(databases)]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ CRITICAL MERMAID SYNTAX RULES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FIRST LINE must be ONLY: {mermaid_syntax}
2. NO text inside mermaid code block except valid Mermaid syntax
3. Node IDs: alphanumeric + underscores only
4. Labels WITHOUT quotes: A[User Service] not A["User Service"]
5. NEVER use parentheses inside square brackets: ❌ A[Console (UI)] ✅ A[Console - UI]
6. Arrow syntax: --> (solid), -.-> (dotted), ==> (thick), -->|label|
7. Subgraph syntax: subgraph GroupName ... end

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 EXAMPLE (for reference - create one specific to the question):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{example}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ DO NOT generate generic/placeholder diagrams like:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```
Such generic diagrams are unhelpful and should not be generated.

Generate the diagram based on ACTUAL information from the retrieved context. Make it specific, accurate, and relevant to the user's question.
"""
    
    def extract_diagram_keywords_from_context(self, context: str) -> List[str]:
        """
        Extract diagram-relevant keywords from the retrieved context.
        
        Args:
            context: Retrieved context from vector DB
            
        Returns:
            List of relevant keywords
        """
        # Common technical terms that are useful for diagrams
        technical_terms = [
            'service', 'component', 'api', 'gateway', 'database', 'cache',
            'frontend', 'backend', 'microservice', 'authentication', 'authorization',
            'deployment', 'pipeline', 'workflow', 'observability', 'monitoring',
            'runtime', 'console', 'cli', 'sdk', 'endpoint', 'handler'
        ]
        
        context_lower = context.lower()
        found_keywords = []
        
        for term in technical_terms:
            if term in context_lower:
                found_keywords.append(term)
        
        return found_keywords[:10]  # Return top 10
    
    def suggest_diagram_improvements(self, response: str) -> Dict:
        """
        Analyze the response and suggest if diagrams could enhance it.
        
        Args:
            response: LLM's response
            
        Returns:
            Dictionary with suggestions
        """
        has_diagram = '```mermaid' in response
        
        # Count technical components mentioned
        technical_terms = [
            'service', 'component', 'api', 'flow', 'process',
            'step', 'interaction', 'system', 'architecture'
        ]
        
        term_count = sum(1 for term in technical_terms if term in response.lower())
        
        return {
            "has_diagram": has_diagram,
            "technical_complexity": term_count,
            "should_have_diagram": term_count >= 3 and not has_diagram,
            "suggestion": "Consider adding a diagram to visualize this" if term_count >= 3 and not has_diagram else None
        }

    def enhance_user_question_for_diagram(self, question: str, diagram_type: Optional[str] = None) -> str:
        """
        Enhance the user's question to explicitly request a professional diagram.
        This reinforces the diagram quality requirements at the user message level.

        Args:
            question: Original user question
            diagram_type: Detected diagram type

        Returns:
            Enhanced question with explicit diagram requirements
        """
        if not diagram_type:
            diagram_type = self.detect_diagram_type(question) or "flowchart"

        # Map to human-readable diagram type
        type_descriptions = {
            'flowchart': 'flowchart diagram',
            'sequence': 'sequence diagram',
            'graph': 'architecture diagram',
            'state': 'state diagram'
        }

        diagram_desc = type_descriptions.get(diagram_type, 'diagram')

        # Add explicit requirements to the question
        enhanced_question = f"""{question}

[Please generate a relevant, accurate {diagram_desc} specific to this question, using real component names from the context. Use subgraphs to organize related components. Do not create a generic placeholder diagram.]"""

        return enhanced_question


# Singleton instance
_diagram_detection_service = None


def get_diagram_detection_service() -> DiagramDetectionService:
    """Get or create the diagram detection service singleton."""
    global _diagram_detection_service
    if _diagram_detection_service is None:
        _diagram_detection_service = DiagramDetectionService()
    return _diagram_detection_service
