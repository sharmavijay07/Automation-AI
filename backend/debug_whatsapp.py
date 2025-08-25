import re

try:
    from agents.whatsapp_agent import whatsapp_agent, ContactSearchTool
    
    # Test the exact command that's failing
    test_command = "send WhatsApp message to Jay lion is coming"
    print(f"Testing command: '{test_command}'")
    print("-" * 50)
    
    # Test the regex patterns directly first
    print("1. Testing regex patterns:")
    
    # Pattern 3: "Send WhatsApp message to [name] [message]" (more specific)
    pattern3 = r'send\s+whatsapp\s+message\s+to\s+(\w+)\s+(.+)'
    match3 = re.search(pattern3, test_command, re.IGNORECASE)
    
    if match3:
        recipient, message = match3.groups()
        print(f"   Pattern 3 matched: recipient='{recipient}', message='{message}'")
    else:
        print("   Pattern 3 did not match")
    
    # Test the contact lookup
    print("\n2. Testing contact lookup:")
    contact_tool = ContactSearchTool()
    
    print(f"   Available contacts: {contact_tool.mock_contacts}")
    
    # Test lookup for "Jay"
    jay_result = contact_tool._run("Jay")
    print(f"   Lookup 'Jay': {jay_result}")
    
    # Test lookup for "jay" (lowercase)
    jay_lower_result = contact_tool._run("jay")
    print(f"   Lookup 'jay': {jay_lower_result}")
    
    # Test the full WhatsApp agent
    print("\n3. Testing full WhatsApp agent:")
    result = whatsapp_agent.process_command(test_command)
    print(f"   Success: {result.get('success', False)}")
    print(f"   Message: {result.get('message', 'No message')}")
    print(f"   Error: {result.get('error', 'No error')}")
    print(f"   URL: {result.get('whatsapp_url', 'No URL')}")
    
except Exception as e:
    print(f"Error during testing: {e}")
    import traceback
    traceback.print_exc()