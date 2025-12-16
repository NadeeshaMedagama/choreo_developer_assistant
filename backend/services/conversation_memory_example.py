"""
Example Usage of Conversation Memory Manager

This script demonstrates how the conversation memory manager works
with a simulated conversation.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.conversation_memory_manager import ConversationMemoryManager, ConversationSummary


# Mock LLM Service for demonstration
class MockLLMService:
    """Mock LLM service for testing without actual API calls"""
    
    def get_response(self, prompt: str, max_tokens: int = 4096) -> str:
        """Return a mock summary"""
        if "metadata" in prompt.lower() or "json" in prompt.lower():
            # Mock metadata extraction
            return """{
  "topics_covered": ["Choreo platform", "deployments", "authentication"],
  "key_questions": ["What is Choreo?", "How to deploy?"],
  "important_decisions": ["Use OAuth 2.0"]
}"""
        else:
            # Mock summary
            return "User is learning about Choreo platform. They asked about the platform basics and are now exploring deployment options with OAuth 2.0 authentication."


def demonstrate_conversation_memory():
    """Demonstrate the conversation memory management system"""
    
    print("=" * 80)
    print("CONVERSATION MEMORY MANAGER DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize the memory manager
    llm_service = MockLLMService()
    memory_manager = ConversationMemoryManager(
        llm_service=llm_service,
        max_total_tokens=8000,
        max_history_tokens=4000,
        recent_window_size=6,
        summarization_trigger_ratio=0.75
    )
    
    print("✓ Memory Manager Initialized")
    print(f"  - Max total tokens: 8000")
    print(f"  - Max history tokens: 4000")
    print(f"  - Recent window size: 6 messages")
    print(f"  - Summarization trigger: 75%")
    print()
    
    # Simulate a conversation
    conversation = [
        {"role": "user", "content": "What is Choreo?"},
        {"role": "assistant", "content": "Choreo is an internal developer platform by WSO2 that helps you build, deploy, and manage cloud-native applications."},
        {"role": "user", "content": "How do I create a project?"},
        {"role": "assistant", "content": "To create a project in Choreo: 1. Sign in to Choreo, 2. Click 'Create Project', 3. Enter project details, 4. Connect your GitHub repository."},
        {"role": "user", "content": "Can I deploy a Python service?"},
        {"role": "assistant", "content": "Yes! Choreo supports Python services. You can deploy FastAPI, Flask, or Django applications."},
        {"role": "user", "content": "How do I set up authentication?"},
        {"role": "assistant", "content": "Choreo supports OAuth 2.0, JWT tokens, and API keys for authentication. You can configure these in the Security settings."},
        {"role": "user", "content": "What about monitoring?"},
        {"role": "assistant", "content": "Choreo provides built-in monitoring with metrics, logs, and traces. You can also integrate with Prometheus and Grafana."},
    ]
    
    # Test 1: Small conversation (no summarization needed)
    print("TEST 1: Small Conversation (4 messages)")
    print("-" * 80)
    small_conversation = conversation[:4]
    
    summary, recent_messages, stats = memory_manager.manage_conversation_memory(
        conversation_history=small_conversation,
        existing_summary=None,
        current_context_tokens=500
    )
    
    print(f"Total messages: {stats['total_messages']}")
    print(f"Total tokens: {stats['total_tokens']}")
    print(f"Recent messages kept: {stats['kept_recent']}")
    print(f"Messages summarized: {stats['summarized_count']}")
    print(f"Summary created: {stats['summary_created']}")
    print()
    
    # Test 2: Longer conversation (trigger summarization)
    print("TEST 2: Longer Conversation (10 messages)")
    print("-" * 80)
    
    # Create a longer conversation by repeating
    long_conversation = conversation + [
        {"role": "user", "content": "Tell me about CI/CD pipelines."},
        {"role": "assistant", "content": "Choreo provides automated CI/CD pipelines that build and deploy your applications automatically when you push code to GitHub."},
    ]
    
    summary, recent_messages, stats = memory_manager.manage_conversation_memory(
        conversation_history=long_conversation,
        existing_summary=None,
        current_context_tokens=500
    )
    
    print(f"Total messages: {stats['total_messages']}")
    print(f"Total tokens: {stats['total_tokens']}")
    print(f"Recent messages kept: {stats['kept_recent']}")
    print(f"Messages summarized: {stats['summarized_count']}")
    print(f"Summary created: {stats['summary_created']}")
    
    if summary:
        print()
        print("Generated Summary:")
        print(f"  Content: {summary.content[:100]}...")
        print(f"  Topics: {', '.join(summary.topics_covered)}")
        print(f"  Key Questions: {', '.join(summary.key_questions)}")
        print(f"  Decisions: {', '.join(summary.important_decisions)}")
        print(f"  Token count: {summary.token_count}")
    print()
    
    # Test 3: Build LLM messages
    print("TEST 3: Build LLM Messages")
    print("-" * 80)
    
    messages = memory_manager.build_llm_messages(
        question="How do I monitor my Python service?",
        context="Monitoring documentation: You can use Choreo's built-in observability features...",
        recent_messages=recent_messages,
        summary=summary,
        system_prompt="You are DevChoreo AI assistant."
    )
    
    print(f"Total messages to LLM: {len(messages)}")
    for i, msg in enumerate(messages, 1):
        role = msg['role']
        content_preview = msg['content'][:60].replace('\n', ' ')
        print(f"  {i}. [{role}] {content_preview}...")
    print()
    
    # Test 4: Token estimation
    print("TEST 4: Token Estimation")
    print("-" * 80)
    
    test_text = "This is a test message to estimate tokens."
    estimated_tokens = memory_manager.estimate_tokens(test_text)
    print(f"Text: '{test_text}'")
    print(f"Estimated tokens: {estimated_tokens}")
    print(f"Actual characters: {len(test_text)}")
    print(f"Ratio: ~{len(test_text) / estimated_tokens:.1f} chars per token")
    print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE")
    print("=" * 80)
    print()
    print("Key Takeaways:")
    print("  ✓ Small conversations: All messages preserved")
    print("  ✓ Large conversations: Automatic summarization")
    print("  ✓ Sliding window: Recent messages always kept")
    print("  ✓ Metadata extraction: Topics, questions, decisions tracked")
    print("  ✓ LLM optimization: Clean message structure with context")
    print()


if __name__ == "__main__":
    demonstrate_conversation_memory()

