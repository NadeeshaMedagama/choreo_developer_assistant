"""
Demo script showing example queries that will generate Mermaid diagrams.
This demonstrates the diagram feature without needing to run the full backend.
"""

EXAMPLE_QUERIES = {
    "Architecture Diagrams": [
        "Show me the architecture of Choreo",
        "What's the overall system design?",
        "Diagram the Choreo platform components",
        "Show me how the observability system is structured",
        "What are the main components and how do they connect?",
    ],

    "Flow Diagrams": [
        "Explain how the deployment process works",
        "Show me the CI/CD pipeline flow",
        "What happens when I push code to GitHub?",
        "Walk me through the build process",
        "How does the data flow through the system?",
    ],

    "Sequence Diagrams": [
        "How do services communicate for authentication?",
        "Show me the API call sequence for deployment",
        "What's the interaction flow between Console and Runtime?",
        "Explain the OAuth authentication sequence",
        "How does the STS token flow work?",
    ],

    "State Diagrams": [
        "What's the lifecycle of a deployment?",
        "Show me the different states of a component",
        "Explain the deployment state transitions",
    ],

    "Database Diagrams": [
        "Show me the database schema",
        "What's the data model for deployments?",
        "Diagram the entity relationships",
    ],
}

EXPECTED_RESPONSES = {
    "deployment_flow": """
Here's how the deployment process works in Choreo:

```mermaid
flowchart TD
    A[Developer Commits Code] --> B[GitHub Webhook Triggered]
    B --> C[Choreo Workflow Manager]
    C --> D[Build Container Image]
    D --> E{Tests Pass?}
    E -->|Yes| F[Push to Registry]
    E -->|No| G[Notify Developer]
    F --> H[Deploy to Runtime]
    H --> I[Health Check]
    I --> J{Healthy?}
    J -->|Yes| K[Route Traffic]
    J -->|No| L[Rollback]
    K --> M[Monitor with Observability]
```

The deployment process in Choreo follows these steps:

1. **Code Commit**: Developer pushes code to GitHub
2. **Webhook**: GitHub triggers a webhook to Choreo
3. **Build**: Workflow Manager initiates the build process
4. **Test**: Automated tests run on the built image
5. **Registry**: If tests pass, image is pushed to container registry
6. **Deploy**: Runtime Manager deploys to the target environment
7. **Health Check**: System verifies the deployment is healthy
8. **Traffic**: If healthy, traffic is routed to the new deployment
9. **Monitor**: Observability services track metrics and logs

Each step is monitored by the Observability platform for real-time insights.
""",

    "authentication_sequence": """
Here's the authentication flow in Choreo:

```mermaid
sequenceDiagram
    participant User
    participant Console
    participant IAM
    participant STS
    participant API Gateway
    participant Service
    
    User->>Console: Login Request
    Console->>IAM: Authenticate User
    IAM->>IAM: Verify Credentials
    IAM->>STS: Request Access Token
    STS->>STS: Generate JWT Token
    STS-->>IAM: Access Token
    IAM-->>Console: Auth Success + Token
    Console-->>User: Display Dashboard
    
    Note over User,Service: Making API Calls
    
    User->>Console: Trigger API Action
    Console->>API Gateway: API Request + Token
    API Gateway->>API Gateway: Validate Token
    API Gateway->>Service: Forward Request
    Service->>Service: Process Request
    Service-->>API Gateway: Response
    API Gateway-->>Console: Response
    Console-->>User: Display Result
```

The authentication flow involves several components:

1. **IAM (Identity & Access Management)**: Verifies user credentials
2. **STS (Security Token Service)**: Generates JWT tokens
3. **API Gateway**: Validates tokens and routes requests
4. **Services**: Process authenticated requests

This ensures secure, token-based authentication across the platform.
""",

    "choreo_architecture": """
Here's the high-level architecture of the Choreo platform:

```mermaid
graph TB
    subgraph "User Interface Layer"
        A[Console Web UI]
        B[CLI Tool]
        C[VS Code Extension]
        D[IDE Plugins]
    end
    
    subgraph "API Gateway Layer"
        E[API Gateway]
        F[Authentication Service]
    end
    
    subgraph "Core Platform Services"
        G[Workflow Manager]
        H[Runtime Manager]
        I[Build Service]
        J[Deployment Controller]
    end
    
    subgraph "Observability Stack"
        K[Metrics Service]
        L[Logging Service]
        M[Tracing Service]
        N[Alerting Service]
    end
    
    subgraph "AI Services"
        O[AI Copilot]
        P[AI Test Assistant]
        Q[AI Doc Bot]
    end
    
    subgraph "Data & Storage"
        R[Vector Database - Milvus]
        S[PostgreSQL]
        T[Object Storage]
    end
    
    subgraph "Infrastructure"
        U[Kubernetes Runtime]
        V[Container Registry]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    E --> G
    E --> H
    E --> O
    
    G --> I
    G --> J
    H --> U
    I --> V
    
    G --> K
    H --> L
    J --> M
    
    O --> R
    P --> R
    Q --> R
    
    G --> S
    H --> S
    I --> T
    
    K --> S
    L --> T
```

**Key Components:**

1. **User Interfaces**: Multiple ways to interact (Console, CLI, IDE extensions)
2. **API Gateway**: Central entry point with authentication
3. **Core Services**: Manage workflows, runtimes, builds, and deployments
4. **Observability**: Comprehensive monitoring, logging, and tracing
5. **AI Services**: Intelligent assistance for development tasks
6. **Data Layer**: Vector DB for AI, PostgreSQL for metadata, Object storage for artifacts
7. **Infrastructure**: Kubernetes-based runtime with container registry

This architecture enables scalable, observable, and AI-powered application development.
"""
}


def print_examples():
    """Print example queries by category."""
    print("\n" + "="*70)
    print("🎨 CHOREO AI ASSISTANT - DIAGRAM FEATURE EXAMPLES")
    print("="*70 + "\n")

    for category, queries in EXAMPLE_QUERIES.items():
        print(f"\n📊 {category}")
        print("-" * 60)
        for i, query in enumerate(queries, 1):
            print(f"   {i}. {query}")

    print("\n" + "="*70)
    print("\n💡 TIP: The AI will automatically detect these queries and generate")
    print("   appropriate Mermaid diagrams based on the knowledge base!\n")


def show_sample_responses():
    """Show what the responses would look like."""
    print("\n" + "="*70)
    print("📝 SAMPLE RESPONSES WITH DIAGRAMS")
    print("="*70 + "\n")

    examples = [
        ("Query: Explain how the deployment process works", "deployment_flow"),
        ("Query: How does authentication work?", "authentication_sequence"),
        ("Query: Show me the Choreo architecture", "choreo_architecture"),
    ]

    for title, key in examples:
        print(f"\n{title}")
        print("-" * 70)
        print(EXPECTED_RESPONSES[key])
        print("\n")


if __name__ == "__main__":
    print_examples()

    print("\n" + "="*70)
    print("Would you like to see sample responses? (y/n): ", end="")
    try:
        choice = input().lower()
        if choice == 'y':
            show_sample_responses()
    except:
        pass

    print("\n✅ The diagram feature is ready!")
    print("   Just ask questions naturally and diagrams will be generated automatically.\n")
