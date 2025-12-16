"""
Conversation Memory Management with Smart Summarization

This module handles conversation history with intelligent summarization
to maintain context while staying within token limits.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import json
import time
from dataclasses import dataclass, asdict
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in conversation history."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    SUMMARY = "summary"


@dataclass
class ConversationMessage:
    """Structured conversation message with metadata."""
    role: str
    content: str
    timestamp: str
    tokens: int
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        return cls(**data)


@dataclass
class ConversationSummary:
    """Structured summary of conversation history."""
    content: str
    timestamp: str
    messages_summarized: int
    topics_covered: List[str]
    key_questions: List[str]
    important_decisions: List[str]
    token_count: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary."""
        return cls(**data)


class ConversationMemoryManager:
    """
    Manages conversation history with intelligent summarization.
    
    Features:
    - Token-based tracking
    - Automatic summarization when limits exceeded
    - Metadata tagging for topics, questions, and decisions
    - Sliding window for recent messages
    - Hierarchical summarization for long conversations
    """
    
    def __init__(
        self,
        llm_service,
        max_total_tokens: int = 8000,
        max_history_tokens: int = 4000,
        recent_window_size: int = 6,  # Keep last 6 messages (3 turns) fully detailed
        summarization_trigger_ratio: float = 0.75,  # Summarize when 75% of limit reached
        enable_llm_summarization: bool = True,  # Toggle LLM-based summarization
        max_summarization_retries: int = 2  # Retries for failed summarization
    ):
        """
        Initialize conversation memory manager.
        
        Args:
            llm_service: LLM service for generating summaries
            max_total_tokens: Maximum total tokens to send to LLM
            max_history_tokens: Maximum tokens for conversation history
            recent_window_size: Number of recent messages to keep detailed
            summarization_trigger_ratio: When to trigger summarization (0.0-1.0)
            enable_llm_summarization: Use LLM for summaries or simple fallback
            max_summarization_retries: Number of retries for failed summarization
        """
        self.llm_service = llm_service
        self.max_total_tokens = max_total_tokens
        self.max_history_tokens = max_history_tokens
        self.recent_window_size = recent_window_size
        self.summarization_trigger_ratio = summarization_trigger_ratio
        self.enable_llm_summarization = enable_llm_summarization
        self.max_summarization_retries = max_summarization_retries

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses rough approximation: ~4 characters per token
        For production, consider using tiktoken library for accurate counting.
        """
        return max(1, len(text) // 4)
    
    def extract_metadata(self, messages: List[Dict]) -> Dict:
        """
        Extract metadata from conversation messages using LLM.
        
        Returns:
            Dictionary with topics_covered, key_questions, important_decisions
        """
        default_metadata = {
            "topics_covered": [],
            "key_questions": [],
            "important_decisions": []
        }

        if not messages:
            return default_metadata

        # Skip LLM if disabled
        if not self.enable_llm_summarization:
            return default_metadata

        # Build conversation text
        conversation_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        )
        
        # Ask LLM to extract metadata with retry logic
        metadata_prompt = f"""Analyze this conversation and extract structured metadata:

{conversation_text}

Provide a JSON response with:
1. topics_covered: List of main topics discussed (max 5)
2. key_questions: List of important questions asked (max 5)
3. important_decisions: List of key decisions or conclusions (max 3)

Format as valid JSON only:
{{
  "topics_covered": ["topic1", "topic2"],
  "key_questions": ["question1", "question2"],
  "important_decisions": ["decision1"]
}}"""
        
        # Retry with exponential backoff
        for attempt in range(self.max_summarization_retries):
            try:
                response = self.llm_service.get_response(metadata_prompt, max_tokens=500)
                # Extract JSON from response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    metadata = json.loads(json_str)
                    return metadata
                else:
                    # Fallback to empty metadata
                    return default_metadata
            except Exception as e:
                error_msg = str(e)
                print(f"Metadata extraction attempt {attempt + 1}/{self.max_summarization_retries} failed: {error_msg}")
                if attempt < self.max_summarization_retries - 1:
                    if "429" in error_msg or "NoCapacity" in error_msg:
                        # Exponential backoff for capacity errors
                        wait_time = 2 ** attempt
                        print(f"Capacity error, waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                    else:
                        # Non-capacity error, fail fast
                        return default_metadata
                else:
                    # Final fallback: return empty metadata
                    print("All metadata extraction attempts failed, using empty metadata")
                    return default_metadata

        return default_metadata

    def create_summary(
        self,
        messages: List[Dict],
        existing_summary: Optional[ConversationSummary] = None
    ) -> Optional[ConversationSummary]:
        """
        Create a concise summary of conversation messages.
        
        Args:
            messages: List of message dictionaries to summarize
            existing_summary: Optional previous summary to build upon
            
        Returns:
            ConversationSummary object with metadata or None if no messages
        """
        if not messages:
            return None
        
        # Extract metadata first (with retry logic built-in)
        metadata = self.extract_metadata(messages)
        
        # Build messages text
        messages_text = "\n".join(
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        )
        
        # Create summary prompt
        if existing_summary:
            summary_prompt = f"""You are creating an updated summary of a conversation.

Previous Summary:
{existing_summary.content}

Previous Topics: {', '.join(existing_summary.topics_covered)}
Previous Key Questions: {', '.join(existing_summary.key_questions)}
Previous Decisions: {', '.join(existing_summary.important_decisions)}

Recent Conversation:
{messages_text}

Create a comprehensive summary that:
1. Integrates the previous summary with new information
2. Preserves all key facts, decisions, and context
3. Maintains chronological flow
4. Is concise but complete (3-5 sentences)

Summary:"""
        else:
            summary_prompt = f"""Summarize the following conversation concisely while preserving all key information:

{messages_text}

Create a summary that:
1. Captures the main topics discussed
2. Preserves important questions and answers
3. Includes any decisions or conclusions
4. Maintains context for future questions
5. Is concise but complete (3-5 sentences)

Summary:"""
        
        # Get summary from LLM with retry logic
        summary_content = None

        # Skip LLM if disabled (use fallback directly)
        if not self.enable_llm_summarization:
            print("LLM summarization disabled, using fallback summary")
            summary_content = self._create_fallback_summary(messages, existing_summary)
        else:
            # Try LLM summarization with retries
            for attempt in range(self.max_summarization_retries):
                try:
                    summary_content = self.llm_service.get_response(summary_prompt, max_tokens=800)
                    break  # Success!
                except Exception as e:
                    error_msg = str(e)
                    print(f"Summary attempt {attempt + 1}/{self.max_summarization_retries} failed: {error_msg}")

                    # Check if it's a capacity error
                    if "429" in error_msg or "NoCapacity" in error_msg:
                        if attempt < self.max_summarization_retries - 1:
                            # Exponential backoff for capacity errors
                            wait_time = 2 ** attempt
                            print(f"Capacity error, waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                        else:
                            # Final fallback: create simple summary without LLM
                            print("All summary attempts failed due to capacity. Creating fallback summary.")
                            summary_content = self._create_fallback_summary(messages, existing_summary)
                            break
                    else:
                        # Non-capacity error, fail fast
                        print(f"Non-capacity error in summarization: {error_msg}")
                        summary_content = self._create_fallback_summary(messages, existing_summary)
                        break

        if not summary_content:
            # Ultimate fallback
            summary_content = self._create_fallback_summary(messages, existing_summary)

        # Create summary object
        summary = ConversationSummary(
            content=summary_content.strip(),
            timestamp=datetime.now(timezone.utc).isoformat(),
            messages_summarized=len(messages),
            topics_covered=metadata.get("topics_covered", []),
            key_questions=metadata.get("key_questions", []),
            important_decisions=metadata.get("important_decisions", []),
            token_count=self.estimate_tokens(summary_content)
        )
        
        return summary
    
    def _create_fallback_summary(
        self,
        messages: List[Dict],
        existing_summary: Optional[ConversationSummary] = None
    ) -> str:
        """
        Create a simple summary without LLM when capacity is exceeded.

        This is a fallback that doesn't require LLM calls.
        """
        if existing_summary:
            # Extend existing summary
            user_messages = [m for m in messages if m.get('role') == 'user']
            if user_messages:
                topics = ", ".join([m['content'][:30] + "..." for m in user_messages[:3]])
                return f"{existing_summary.content} The user then discussed: {topics}"
            else:
                return existing_summary.content
        else:
            # Create new simple summary
            user_messages = [m for m in messages if m.get('role') == 'user']
            if user_messages:
                topics = ", ".join([m['content'][:40] for m in user_messages[:5]])
                return f"User discussed: {topics}"
            else:
                return "Conversation about Choreo platform."

    def manage_conversation_memory(
        self,
        conversation_history: List[Dict],
        existing_summary: Optional[Dict] = None,
        current_context_tokens: int = 0
    ) -> Tuple[Optional[ConversationSummary], List[Dict], Dict]:
        """
        Manage conversation memory with smart summarization.
        
        Args:
            conversation_history: List of conversation messages
            existing_summary: Optional previous summary dictionary
            current_context_tokens: Tokens used by current context (DB chunks)
            
        Returns:
            Tuple of (updated_summary, recent_messages, stats)
        """
        stats = {
            "total_messages": len(conversation_history),
            "total_tokens": 0,
            "kept_recent": 0,
            "summarized_count": 0,
            "summary_created": False,
            "summary_updated": False
        }
        
        if not conversation_history:
            return None, [], stats
        
        # Convert existing summary if present
        summary = None
        if existing_summary:
            try:
                summary = ConversationSummary.from_dict(existing_summary)
            except:
                summary = None
        
        # Calculate tokens for all messages
        for msg in conversation_history:
            msg['tokens'] = self.estimate_tokens(msg.get('content', ''))
        
        total_history_tokens = sum(msg['tokens'] for msg in conversation_history)
        stats['total_tokens'] = total_history_tokens
        
        # Calculate available tokens for history
        available_tokens = self.max_history_tokens - current_context_tokens
        if summary:
            available_tokens -= summary.token_count
        
        # Always keep recent messages in sliding window
        recent_messages = conversation_history[-self.recent_window_size:] if len(conversation_history) > self.recent_window_size else conversation_history
        older_messages = conversation_history[:-self.recent_window_size] if len(conversation_history) > self.recent_window_size else []
        
        recent_tokens = sum(msg['tokens'] for msg in recent_messages)
        stats['kept_recent'] = len(recent_messages)
        
        # Decision logic for summarization
        should_summarize = False
        
        # Case 1: Recent messages alone exceed available tokens
        if recent_tokens > available_tokens:
            should_summarize = True
        
        # Case 2: We have older messages and approaching token limit
        elif older_messages and (total_history_tokens > available_tokens * self.summarization_trigger_ratio):
            should_summarize = True
        
        # Case 3: Many older messages accumulating (even if under token limit)
        elif len(older_messages) >= 10:  # More than 10 older messages
            should_summarize = True
        
        # Perform summarization if needed
        if should_summarize and older_messages:
            # Create or update summary
            summary = self.create_summary(older_messages, summary)
            stats['summarized_count'] = len(older_messages)
            stats['summary_created'] = not existing_summary
            stats['summary_updated'] = bool(existing_summary)
        
        return summary, recent_messages, stats
    
    def build_llm_messages(
        self,
        question: str,
        context: str,
        recent_messages: List[Dict],
        summary: Optional[ConversationSummary] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """
        Build optimized message list for LLM with summary and context.
        
        Args:
            question: Current user question
            context: Retrieved context from knowledge base
            recent_messages: Recent conversation messages
            summary: Optional conversation summary
            system_prompt: Optional custom system prompt
            
        Returns:
            List of messages ready for LLM
        """
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation summary if exists
        if summary:
            summary_context = f"""Conversation Summary:
{summary.content}

Topics Covered: {', '.join(summary.topics_covered) if summary.topics_covered else 'None'}
Key Questions: {', '.join(summary.key_questions) if summary.key_questions else 'None'}
Important Decisions: {', '.join(summary.important_decisions) if summary.important_decisions else 'None'}"""
            messages.append({"role": "system", "content": summary_context})
        
        # Add knowledge base context
        if context:
            context_message = f"""Retrieved Knowledge Base Context:
{context}

Use this context to answer the user's question accurately."""
            messages.append({"role": "system", "content": context_message})
        
        # Add recent conversation history
        for msg in recent_messages:
            if msg.get("role") in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        return messages

