"""
Test script for enhanced conversational AI capabilities
"""

def test_conversation_routing():
    """Test that questions are properly routed to conversation agent"""
    
    test_inputs = [
        "can you do file searching",  # Should go to conversation, not filesearch
        "what is artificial intelligence",  # General question
        "how does machine learning work",  # Knowledge question
        "tell me about yourself",  # Capability question
        "find my report.pdf",  # Should go to filesearch (actual operation)
        "send WhatsApp to Jay hello",  # Should go to whatsapp
        "what can you help me with",  # Should go to conversation
    ]
    
    print("🧪 Testing Conversational AI Routing")
    print("=" * 60)
    
    # Simulate the intent detection logic
    for i, user_input in enumerate(test_inputs, 1):
        user_input_lower = user_input.lower()
        
        print(f"\n{i}. Testing: '{user_input}'")
        print("-" * 40)
        
        # Detect file intent with better distinction
        file_keywords = ["find", "search", "open", "ownership", "folder", "photo", "video", "pdf", "doc", "docx", "excel", "presentation", "report"]
        whatsapp_keywords = ["whatsapp", "message", "send", "tell", "text", "share", "chat"]
        
        # Questions about capabilities (should go to conversation)
        capability_questions = ["can you", "are you able", "do you", "what can", "how do", "tell me about", "what is", "explain", "why", "how"]
        general_questions = ["what", "how", "why", "when", "where", "who", "?"]
        is_capability_question = any(phrase in user_input_lower for phrase in capability_questions)
        is_general_question = any(word in user_input_lower for word in general_questions) and not any(op_word in user_input_lower for op_word in ["find", "search", "open", "send"])
        
        # Actual file operations (should go to filesearch)
        file_operation_keywords = ["find", "search", "open", "locate", "show me"]
        has_file_operation = any(keyword in user_input_lower for keyword in file_operation_keywords) and not is_capability_question
        
        # Multi-agent detection (file + communication)
        has_whatsapp_intent = any(keyword in user_input_lower for keyword in whatsapp_keywords)
        
        # Special handling for WhatsApp patterns
        whatsapp_patterns = ["send whatsapp", "whatsapp to", "message to", "text to"]
        is_whatsapp_command = any(pattern in user_input_lower for pattern in whatsapp_patterns)
        
        print(f"   Is capability question: {is_capability_question}")
        print(f"   Is general question: {is_general_question}")
        print(f"   Has file operation: {has_file_operation}")
        print(f"   Has WhatsApp intent: {has_whatsapp_intent}")
        print(f"   Is WhatsApp command: {is_whatsapp_command}")
        
        # Determine routing
        if is_whatsapp_command or (has_whatsapp_intent and not has_file_operation and not is_capability_question):
            routing = "whatsapp"
            print(f"   ✅ ROUTED TO: whatsapp")
        elif has_file_operation and not is_capability_question and not is_general_question:
            routing = "filesearch"
            print(f"   ✅ ROUTED TO: filesearch")
        elif is_capability_question or is_general_question:
            routing = "conversation"
            print(f"   ✅ ROUTED TO: conversation (capability/general question)")
        else:
            routing = "conversation"
            print(f"   ✅ ROUTED TO: conversation (default)")
        
        # Validate routing
        expected_routes = {
            "can you do file searching": "conversation",
            "what is artificial intelligence": "conversation", 
            "how does machine learning work": "conversation",
            "tell me about yourself": "conversation",
            "find my report.pdf": "filesearch",
            "send WhatsApp to Jay hello": "whatsapp",
            "what can you help me with": "conversation"
        }
        
        expected = expected_routes.get(user_input, "conversation")
        if routing == expected:
            print(f"   ✅ CORRECT ROUTING")
        else:
            print(f"   ❌ WRONG ROUTING - Expected: {expected}, Got: {routing}")
    
    print("\n" + "=" * 60)
    print("✅ Conversation routing test completed!")
    print("\nNow the conversation agent should:")
    print("- Answer any questions intelligently")
    print("- Demonstrate file search when asked about capabilities")
    print("- Provide natural conversational responses")
    print("- Route operational commands to appropriate agents")

if __name__ == "__main__":
    test_conversation_routing()