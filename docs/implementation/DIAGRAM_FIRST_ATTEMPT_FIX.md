# Diagram First Attempt Quality Fix

## Problem Statement

The AI assistant was generating **simple, irrelevant diagrams on the first attempt**, but produced correct, professional diagrams when the user regenerated the response.

### Root Cause Analysis

1. **Diagram instructions appended at END of prompt**: The diagram enhancement was added at the end of a very long system prompt, making it less prominent to the LLM
2. **No "first attempt" emphasis**: The LLM didn't understand this was the only chance to get it right
3. **Insufficient reinforcement**: The quality requirements weren't reinforced in the user's question
4. **Limited max_tokens**: For non-streaming requests, max_tokens was set to 1000, which may truncate detailed diagrams

## Solution Implemented

### 1. Prepend Diagram Instructions (Not Append)

**Files Modified:** `backend/app.py`

Changed the diagram enhancement to be **prepended at the BEGINNING** of the system prompt instead of appended at the end. LLMs pay more attention to instructions at the start of prompts.

```python
# BEFORE (wrong - at end)
system_prompt += f"\n\n{diagram_enhancement}"

# AFTER (correct - at start)
system_prompt = f"{diagram_enhancement}\n\n{system_prompt}"
```

### 2. Enhanced "FIRST ATTEMPT" Directive

**Files Modified:** `backend/services/diagram_detection_service.py`, `backend/services/llm_service.py`

Added strong "FIRST AND ONLY ATTEMPT" language to the diagram prompt:

```
🚨🚨🚨 HIGHEST PRIORITY - DIAGRAM GENERATION REQUIRED 🚨🚨🚨

⚡ THIS IS YOUR FIRST AND ONLY ATTEMPT - GET IT RIGHT NOW ⚡
You MUST generate a PROFESSIONAL, COMPREHENSIVE Mermaid diagram on this FIRST response.
Do NOT create a simple placeholder diagram - create the COMPLETE, DETAILED diagram immediately.
```

### 3. User Question Enhancement

**Files Modified:** `backend/services/diagram_detection_service.py`, `backend/app.py`

Added a new method `enhance_user_question_for_diagram()` that appends explicit quality requirements to the user's question:

```python
def enhance_user_question_for_diagram(self, question: str, diagram_type: Optional[str] = None) -> str:
    """
    Enhance the user's question to explicitly request a professional diagram.
    """
    enhanced_question = f"""{question}

[IMPORTANT: Generate a COMPLETE, PROFESSIONAL {diagram_desc} with:
- 10-20 nodes showing ALL relevant components
- Subgraphs to organize related components
- Real component names from the context (not generic names)
- Labeled connections showing data/action flow
- This is my FIRST request - provide the FULL detailed diagram immediately, not a simple placeholder]"""
    
    return enhanced_question
```

### 4. Increased max_tokens for Diagram Queries

**Files Modified:** `backend/app.py`

Increased `max_tokens` from 1000 to 2000 for diagram queries to allow detailed diagrams without truncation:

```python
response_max_tokens = 2000 if is_diagram_query else 1000
```

### 5. Clear Quality Requirements

Updated the diagram prompts with explicit requirements:

- **MINIMUM 10-20 nodes** (never simple 3-5 node diagrams)
- **MUST use subgraphs** for organization
- **MUST use real component names** from context
- **MUST add labels** on connections
- **"ABSOLUTELY FORBIDDEN"** section showing what NOT to do

## Files Modified

| File | Changes |
|------|---------|
| `backend/app.py` | Prepend diagram enhancement, enhance user question, increase max_tokens |
| `backend/services/diagram_detection_service.py` | Enhanced prompt with FIRST ATTEMPT directive, added `enhance_user_question_for_diagram()` |
| `backend/services/llm_service.py` | Enhanced base mermaid instructions with FIRST ATTEMPT policy |

## Testing

Run the test to verify the changes:

```bash
cd choreo-ai-assistant/backend
python3 -c "
from services.diagram_detection_service import get_diagram_detection_service

service = get_diagram_detection_service()

# Test detection
assert service.is_diagram_query('Show me the architecture') == True
print('✅ Diagram detection works')

# Test question enhancement
enhanced = service.enhance_user_question_for_diagram('Show me the deployment flow', 'flowchart')
assert 'COMPLETE, PROFESSIONAL' in enhanced
assert 'FIRST request' in enhanced
print('✅ Question enhancement works')

# Test prompt enhancement
prompt = service.generate_diagram_prompt_enhancement('Show architecture', 'graph')
assert 'FIRST AND ONLY ATTEMPT' in prompt
assert 'HIGHEST PRIORITY' in prompt
print('✅ Prompt enhancement works')

print()
print('All tests passed! ✅')
"
```

## Expected Behavior After Fix

| Scenario | Before | After |
|----------|--------|-------|
| First diagram request | Simple 3-node diagram | Complete 10-20 node professional diagram |
| Diagram position in prompt | End (low priority) | Beginning (high priority) |
| User question | Original only | Enhanced with requirements |
| max_tokens | 1000 | 2000 (for diagram queries) |
| "First attempt" emphasis | None | Strong emphasis |

## Key Improvements

1. ✅ **Prepend, don't append**: Diagram instructions at START of prompt for maximum attention
2. ✅ **First attempt directive**: Clear message that this is the ONLY chance
3. ✅ **User question reinforcement**: Quality requirements in the user message itself
4. ✅ **Explicit "forbidden" examples**: Show what NOT to generate
5. ✅ **Adequate token limit**: Enough tokens for detailed diagrams

