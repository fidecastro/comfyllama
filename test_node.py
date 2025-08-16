#!/usr/bin/env python3
"""
Test script for the LlamaLiteNode ComfyUI custom node.

This script provides a simple test to validate that the node works correctly
without requiring a full ComfyUI installation. It's useful for development
and debugging.

Run this script to test:
1. Node initialization
2. Input validation 
3. Basic functionality (requires a running llama.cpp server)

Usage:
    python test_node.py [server_url]

Example:
    python test_node.py http://localhost:8080/v1
"""

import sys
import json
from comfy_llama_node import LlamaLiteNode


def test_node_initialization():
    """Test that the node can be initialized properly."""
    print("Testing node initialization...")
    try:
        node = LlamaLiteNode()
        print("✓ Node initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Node initialization failed: {e}")
        return False


def test_input_types():
    """Test that INPUT_TYPES method works correctly."""
    print("Testing INPUT_TYPES method...")
    try:
        input_types = LlamaLiteNode.INPUT_TYPES()
        
        # Validate structure
        assert "required" in input_types
        assert "optional" in input_types
        assert "server_url" in input_types["required"]
        assert "prompt" in input_types["required"]
        assert "system_prompt" in input_types["optional"]
        assert "chat_history" in input_types["optional"]
        
        print("✓ INPUT_TYPES structure is correct")
        return True
    except Exception as e:
        print(f"✗ INPUT_TYPES test failed: {e}")
        return False


def test_chat_history_parsing():
    """Test chat history parsing functionality."""
    print("Testing chat history parsing...")
    node = LlamaLiteNode()
    
    # Test empty history
    try:
        result = node._parse_chat_history("")
        assert result == []
        print("✓ Empty chat history parsed correctly")
    except Exception as e:
        print(f"✗ Empty chat history test failed: {e}")
        return False
    
    # Test valid history
    try:
        valid_history = json.dumps([
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ])
        result = node._parse_chat_history(valid_history)
        assert len(result) == 3
        assert result[0]["role"] == "system"
        print("✓ Valid chat history parsed correctly")
    except Exception as e:
        print(f"✗ Valid chat history test failed: {e}")
        return False
    
    # Test invalid JSON
    try:
        node._parse_chat_history("invalid json")
        print("✗ Invalid JSON should have raised an error")
        return False
    except ValueError:
        print("✓ Invalid JSON correctly rejected")
    except Exception as e:
        print(f"✗ Unexpected error with invalid JSON: {e}")
        return False
    
    return True


def test_with_server(server_url):
    """Test the node with an actual llama.cpp server."""
    print(f"Testing with server: {server_url}")
    node = LlamaLiteNode()
    
    try:
        response_message, chat_history = node.execute_llama_chat(
            server_url=server_url,
            prompt="Hello! This is a test. Please respond with 'Test successful'.",
            system_prompt="You are a test assistant. Always respond with exactly what the user asks for.",
            chat_history="[]"
        )
        
        # Check if we got a response
        if "Error:" in response_message:
            print(f"⚠ Server returned an error: {response_message}")
            return False
        
        print(f"✓ Server responded: {response_message[:100]}...")
        
        # Check chat history format
        try:
            history_data = json.loads(chat_history)
            assert isinstance(history_data, list)
            print("✓ Chat history format is valid")
        except:
            print("✗ Chat history format is invalid")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Server test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("LlamaLiteNode Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Basic tests (no server required)
    basic_tests = [
        test_node_initialization,
        test_input_types,
        test_chat_history_parsing,
    ]
    
    for test in basic_tests:
        total_tests += 1
        if test():
            tests_passed += 1
        print()
    
    # Server test (if URL provided)
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/v1"
    
    print(f"Attempting server test with: {server_url}")
    print("(Make sure your llama.cpp server is running)")
    
    total_tests += 1
    if test_with_server(server_url):
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! The node is ready to use.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
