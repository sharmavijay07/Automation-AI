"""
Test Email Agent AI Enhancement
Shows how the new AI-powered email generation works
"""

from agents.email_agent import email_agent

# Test Case 1: Your exact command
print("=" * 60)
print("TEST 1: Internship Application with AI")
print("=" * 60)

command1 = "send email to Jay his email is 7819Vijaysharma@gmail.com send a subject line as application for internship and give the details from the graph API"

result1 = email_agent.process_command(command1)

print(f"\n✅ Success: {result1['success']}")
print(f"\n📧 Message:\n{result1['message']}")
print(f"\n📋 Details:")
print(f"  Recipient: {result1['details'].get('recipient', 'N/A')}")
print(f"  Subject: {result1['details'].get('subject', 'N/A')}")
print(f"  AI Generated: {result1['details'].get('ai_generated', False)}")
if result1['details'].get('body'):
    print(f"\n📝 Email Body Preview:")
    print(f"{result1['details']['body'][:200]}...")

print("\n" + "=" * 60)
print("TEST 2: Simple Email (No AI)")
print("=" * 60)

command2 = "email john@test.com saying Meeting at 3 PM today"

result2 = email_agent.process_command(command2)

print(f"\n✅ Success: {result2['success']}")
print(f"\n📧 Message:\n{result2['message']}")
print(f"\n📋 Details:")
print(f"  Recipient: {result2['details'].get('recipient', 'N/A')}")
print(f"  Subject: {result2['details'].get('subject', 'N/A')}")
print(f"  Body: {result2['details'].get('body', 'N/A')}")
print(f"  AI Generated: {result2['details'].get('ai_generated', False)}")

print("\n" + "=" * 60)
print("TEST 3: Explicit AI Request")
print("=" * 60)

command3 = "compose email to hr@company.com about leave request, use AI to write it professionally"

result3 = email_agent.process_command(command3)

print(f"\n✅ Success: {result3['success']}")
print(f"\n📧 Message:\n{result3['message']}")
print(f"\n📋 Details:")
print(f"  Recipient: {result3['details'].get('recipient', 'N/A')}")
print(f"  Subject: {result3['details'].get('subject', 'N/A')}")
print(f"  AI Generated: {result3['details'].get('ai_generated', False)}")
if result3['details'].get('body'):
    print(f"\n📝 Email Body Preview:")
    print(f"{result3['details']['body'][:200]}...")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
