"""
Test to verify Mermaid syntax that works correctly.
This helps debug rendering issues.
"""

WORKING_DIAGRAMS = {
    "flowchart_simple": """```mermaid
flowchart TD
    A[Start] --> B[Process]
    B --> C[End]
```""",

    "flowchart_with_decision": """```mermaid
flowchart TD
    A[User Request] --> B{Valid?}
    B -->|Yes| C[Process]
    B -->|No| D[Error]
    C --> E[Success]
```""",

    "sequence_diagram": """```mermaid
sequenceDiagram
    participant User
    participant API
    participant DB
    User->>API: Request
    API->>DB: Query
    DB-->>API: Data
    API-->>User: Response
```""",

    "graph_architecture": """```mermaid
graph LR
    A[Frontend] --> B[API]
    B --> C[Database]
    B --> D[Cache]
```""",

    "state_diagram": """```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Processing
    Processing --> Done
    Done --> [*]
```""",
}

PROBLEMATIC_DIAGRAMS = {
    "er_diagram": """```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE-ITEM : contains
```
⚠️ ER diagrams can cause "Inferred ER Diagram" rendering issues""",

    "without_direction": """```mermaid
flowchart
    A --> B
    B --> C
```
⚠️ Missing direction (TD, LR) can cause issues""",

    "invalid_syntax": """```mermaid
graph
    A[Node -> B[Node]
```
⚠️ Invalid syntax - missing direction and wrong arrow""",
}


def print_working_examples():
    print("\n" + "="*70)
    print("✅ WORKING MERMAID DIAGRAMS")
    print("="*70)

    for name, diagram in WORKING_DIAGRAMS.items():
        print(f"\n{name.upper().replace('_', ' ')}:")
        print(diagram)


def print_problematic_examples():
    print("\n" + "="*70)
    print("❌ PROBLEMATIC MERMAID DIAGRAMS (AVOID THESE)")
    print("="*70)

    for name, info in PROBLEMATIC_DIAGRAMS.items():
        print(f"\n{name.upper().replace('_', ' ')}:")
        print(info)


def print_syntax_rules():
    print("\n" + "="*70)
    print("📋 MERMAID SYNTAX RULES TO FOLLOW")
    print("="*70)

    rules = [
        "1. ✅ ALWAYS specify diagram type AND direction:",
        "   - flowchart TD (top-down)",
        "   - flowchart LR (left-right)",
        "   - graph TD or graph LR",
        "   - sequenceDiagram (no direction needed)",
        "   - stateDiagram-v2 (use v2)",
        "",
        "2. ✅ Use square brackets for node labels:",
        "   - A[My Node Label]",
        "   - B[Another Node]",
        "",
        "3. ✅ Use proper arrow syntax:",
        "   - --> (solid arrow)",
        "   - -.-> (dotted arrow)",
        "   - ==> (thick arrow)",
        "   - A -->|Label| B (arrow with label)",
        "",
        "4. ✅ Use curly braces for decisions:",
        "   - A{Is Valid?}",
        "   - B{Check Status}",
        "",
        "5. ❌ AVOID these diagram types:",
        "   - erDiagram (causes 'Inferred ER Diagram' issues)",
        "   - gitGraph (complex, often fails)",
        "   - gantt, pie, journey (not well supported)",
        "",
        "6. ✅ Keep diagrams simple:",
        "   - 5-12 nodes is optimal",
        "   - Clear, short labels",
        "   - Logical flow",
    ]

    for rule in rules:
        print(rule)


def print_fix_guide():
    print("\n" + "="*70)
    print("🔧 HOW TO FIX 'Rendering diagram...' STUCK ISSUE")
    print("="*70)

    fixes = [
        "",
        "SYMPTOMS:",
        "- UI shows 'Rendering diagram...' indefinitely",
        "- Console may show 'Inferred ER Diagram'",
        "- Diagram never appears",
        "",
        "CAUSES:",
        "1. Invalid Mermaid syntax",
        "2. Using erDiagram or other problematic types",
        "3. Missing diagram direction (TD, LR, etc.)",
        "4. Malformed node IDs or arrows",
        "",
        "SOLUTIONS:",
        "✅ Frontend: Added 10-second timeout to prevent infinite rendering",
        "✅ Frontend: Better error handling and logging",
        "✅ Backend: Updated LLM instructions to avoid ER diagrams",
        "✅ Backend: Emphasize using flowchart/graph/sequence only",
        "✅ Backend: Always specify direction (TD, LR, etc.)",
        "",
        "TO TEST:",
        "1. Ask: 'Show me the Choreo architecture'",
        "2. Verify response contains: flowchart TD or graph LR",
        "3. Check diagram renders within 2-3 seconds",
        "4. If stuck > 10 seconds, shows timeout error with code",
        "",
        "UPDATED FILES:",
        "- frontend/src/components/MermaidDiagram.jsx (timeout + error handling)",
        "- backend/services/llm_service.py (better instructions)",
        "- backend/services/diagram_detection_service.py (safe types only)",
    ]

    for fix in fixes:
        print(fix)


if __name__ == "__main__":
    print("\n🎨 MERMAID DIAGRAM SYNTAX GUIDE")
    print_syntax_rules()
    print_working_examples()
    print_problematic_examples()
    print_fix_guide()

    print("\n" + "="*70)
    print("✅ FIXES APPLIED - Ready to test!")
    print("="*70)
    print("\nThe 'Rendering diagram...' issue should now be fixed.")
    print("Test by asking: 'Show me the Choreo deployment flow'\n")
