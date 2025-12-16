#!/usr/bin/env python3
"""
Test script for conversation history with retrieval implementation.
Tests both the regular and streaming endpoints with conversation history.
"""

import requests
import json
import sys


BASE_URL = "http://localhost:8000"


def test_basic_question():
    """Test 1: Basic question without history"""
    print("\n" + "="*80)
    print("TEST 1: Basic Question (No History)")
    print("="*80)
    
    response = requests.post(
        f"{BASE_URL}/api/ask",
        json={
            "question": "What is Choreo?",
            "conversation_history": []
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
        print(f"Context Count: {data.get('context_count', 0)}")
        return data.get('answer', '')
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None


def test_followup_question(first_answer):
    """Test 2: Follow-up question with history"""
    print("\n" + "="*80)
    print("TEST 2: Follow-up Question (With History)")
    print("="*80)
    
    conversation_history = [
        {"role": "user", "content": "What is Choreo?"},
        {"role": "assistant", "content": first_answer}
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/ask",
        json={
            "question": "How do I deploy applications in it?",
            "conversation_history": conversation_history
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
        print(f"Context Count: {data.get('context_count', 0)}")
        return data.get('answer', '')
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None


def test_multi_turn_conversation():
    """Test 3: Multi-turn conversation"""
    print("\n" + "="*80)
    print("TEST 3: Multi-turn Conversation")
    print("="*80)
    
    conversation_history = [
        {"role": "user", "content": "What is Choreo?"},
        {"role": "assistant", "content": "Choreo is a platform for building cloud-native applications."},
        {"role": "user", "content": "What languages does it support?"},
        {"role": "assistant", "content": "Choreo supports multiple languages including Python, Java, Node.js, and Go."},
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/ask",
        json={
            "question": "Which one is best for microservices?",
            "conversation_history": conversation_history
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
        print(f"Context Count: {data.get('context_count', 0)}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)


def test_streaming():
    """Test 4: Streaming with conversation history"""
    print("\n" + "="*80)
    print("TEST 4: Streaming Response (With History)")
    print("="*80)
    
    conversation_history = [
        {"role": "user", "content": "What is Choreo?"},
        {"role": "assistant", "content": "Choreo is a platform for cloud applications."}
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/ask/stream",
            json={
                "question": "Tell me more about its features",
                "conversation_history": conversation_history
            },
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Streaming started...")
            print("Response: ", end="", flush=True)
            
            full_response = ""
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            print("\n✅ Streaming completed!")
                            break
                        try:
                            parsed = json.loads(data)
                            if 'content' in parsed:
                                content = parsed['content']
                                print(content, end="", flush=True)
                                full_response += content
                            elif 'error' in parsed:
                                print(f"\n❌ Error: {parsed['error']}")
                                break
                        except json.JSONDecodeError:
                            pass
            
            return full_response
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None


def test_empty_history():
    """Test 5: Empty/null history handling"""
    print("\n" + "="*80)
    print("TEST 5: Empty History Handling")
    print("="*80)
    
    # Test with None
    response = requests.post(
        f"{BASE_URL}/api/ask",
        json={
            "question": "What is Choreo?"
            # No conversation_history field
        }
    )
    
    if response.status_code == 200:
        print("✅ Handles None/missing history correctly")
    else:
        print(f"❌ Failed with None: {response.status_code}")
    
    # Test with empty list
    response = requests.post(
        f"{BASE_URL}/api/ask",
        json={
            "question": "What is Choreo?",
            "conversation_history": []
        }
    )
    
    if response.status_code == 200:
        print("✅ Handles empty list correctly")
    else:
        print(f"❌ Failed with empty list: {response.status_code}")


def test_health():
    """Test 0: Health check"""
    print("\n" + "="*80)
    print("TEST 0: Health Check")
    print("="*80)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False


def main():
    print("\n" + "="*80)
    print("CONVERSATION HISTORY WITH RETRIEVAL - TEST SUITE")
    print("="*80)
    
    # Test health first
    if not test_health():
        print("\n❌ Backend is not running. Please start the backend first.")
        print("Run: cd backend && python -m app")
        sys.exit(1)
    
    # Run tests
    first_answer = test_basic_question()
    
    if first_answer:
        test_followup_question(first_answer)
    
    test_multi_turn_conversation()
    test_streaming()
    test_empty_history()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)
    print("\n✅ If all tests passed, your implementation is working correctly!")
    print("\nNext steps:")
    print("1. Test in the frontend UI")
    print("2. Try multi-turn conversations")
    print("3. Test edit and regenerate features")
    print("4. Monitor token usage and performance")


if __name__ == "__main__":
    main()

