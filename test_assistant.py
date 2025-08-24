"""
Test script for AI Task Automation Assistant
Tests the WhatsApp agent functionality
"""

import requests
import json
import time
from datetime import datetime
from config import config

class TestRunner:
    """Test runner for the AI assistant"""
    
    def __init__(self):
        self.api_base_url = f"http://{config.FASTAPI_HOST}:{config.FASTAPI_PORT}"
        self.passed_tests = 0
        self.failed_tests = 0
    
    def print_header(self, title: str):
        """Print test header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print(f"{'='*60}")
    
    def print_test(self, test_name: str, passed: bool, message: str = ""):
        """Print test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} | {test_name}")
        if message:
            print(f"     └─ {message}")
        
        if passed:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        self.print_header("Backend Health Tests")
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            
            # Test 1: Backend is responding
            is_responding = response.status_code == 200
            self.print_test("Backend responding", is_responding, f"Status: {response.status_code}")
            
            if is_responding:
                data = response.json()
                
                # Test 2: Health data structure
                has_status = "status" in data
                self.print_test("Health data structure", has_status, f"Status: {data.get('status', 'missing')}")
                
                # Test 3: Agents availability
                has_agents = "agents_available" in data
                self.print_test("Agents list available", has_agents, f"Agents: {data.get('agents_available', [])}")
        
        except requests.exceptions.ConnectionError:
            self.print_test("Backend responding", False, "Connection refused - is the server running?")
        except Exception as e:
            self.print_test("Backend responding", False, f"Error: {str(e)}")
    
    def test_whatsapp_commands(self):
        """Test WhatsApp agent commands"""
        self.print_header("WhatsApp Agent Tests")
        
        test_commands = [
            {
                "command": "Send WhatsApp to Jay: Hello how are you",
                "should_succeed": True,
                "expected_agent": "whatsapp"
            },
            {
                "command": "Message Mom on WhatsApp: I'll be late",
                "should_succeed": True,
                "expected_agent": "whatsapp"
            },
            {
                "command": "WhatsApp Vijay: Meeting at 5 PM",
                "should_succeed": True,
                "expected_agent": "whatsapp"
            },
            {
                "command": "Send WhatsApp to UnknownContact: Hello",
                "should_succeed": False,  # Contact not found
                "expected_agent": "whatsapp"
            },
            {
                "command": "Call John",
                "should_succeed": False,  # Not implemented
                "expected_agent": "unsupported"
            },
            {
                "command": "Open file project.pdf",
                "should_succeed": False,  # Not implemented
                "expected_agent": "unsupported"
            }
        ]
        
        for i, test_case in enumerate(test_commands, 1):
            try:
                payload = {"command": test_case["command"]}
                response = requests.post(
                    f"{self.api_base_url}/process-command",
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Test command processing
                    success = data.get("success", False)
                    agent_used = data.get("agent_used", "")
                    
                    # Validate based on expectation
                    if test_case["should_succeed"]:
                        test_passed = success and agent_used == test_case["expected_agent"]
                        message = f"Agent: {agent_used}, Success: {success}"
                    else:
                        test_passed = not success or agent_used == test_case["expected_agent"]
                        message = f"Expected failure - Agent: {agent_used}, Success: {success}"
                    
                    self.print_test(f"Test {i}: {test_case['command'][:30]}...", test_passed, message)
                    
                    # Additional validation for successful WhatsApp commands
                    if success and agent_used == "whatsapp":
                        agent_response = data.get("details", {}).get("agent_response", {})
                        has_url = bool(agent_response.get("whatsapp_url"))
                        self.print_test(f"  └─ WhatsApp URL generated", has_url, agent_response.get("whatsapp_url", "")[:50])
                
                else:
                    self.print_test(f"Test {i}: {test_case['command'][:30]}...", False, f"HTTP {response.status_code}")
                
            except Exception as e:
                self.print_test(f"Test {i}: {test_case['command'][:30]}...", False, f"Error: {str(e)}")
            
            # Small delay between tests
            time.sleep(0.5)
    
    def test_configuration(self):
        """Test configuration endpoint"""
        self.print_header("Configuration Tests")
        
        try:
            response = requests.get(f"{self.api_base_url}/config", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                config_data = data.get("config", {})
                
                # Test configuration fields
                has_model = "groq_model" in config_data
                self.print_test("Groq model configured", has_model, config_data.get("groq_model", "missing"))
                
                has_agents = "agents_available" in config_data
                self.print_test("Agents list in config", has_agents, str(config_data.get("agents_available", [])))
                
                has_temp = "agent_temperature" in config_data
                self.print_test("Agent temperature set", has_temp, str(config_data.get("agent_temperature", "missing")))
            
            else:
                self.print_test("Configuration endpoint", False, f"HTTP {response.status_code}")
        
        except Exception as e:
            self.print_test("Configuration endpoint", False, f"Error: {str(e)}")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        self.print_header("Edge Cases & Error Handling")
        
        edge_cases = [
            {"command": "", "test_name": "Empty command"},
            {"command": "   ", "test_name": "Whitespace only"},
            {"command": "x" * 1000, "test_name": "Very long command"},
            {"command": "!@#$%^&*()", "test_name": "Special characters only"},
            {"command": "Hello", "test_name": "Single word"},
        ]
        
        for case in edge_cases:
            try:
                payload = {"command": case["command"]}
                response = requests.post(
                    f"{self.api_base_url}/process-command",
                    json=payload,
                    timeout=10
                )
                
                # Edge cases should either succeed gracefully or fail gracefully
                handled_gracefully = response.status_code in [200, 400]
                
                if response.status_code == 200:
                    data = response.json()
                    message = f"Handled: {data.get('message', '')[:50]}"
                else:
                    message = f"HTTP {response.status_code}"
                
                self.print_test(case["test_name"], handled_gracefully, message)
            
            except Exception as e:
                self.print_test(case["test_name"], False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"\n🚀 Starting AI Task Automation Assistant Tests")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target: {self.api_base_url}")
        
        # Run test suites
        self.test_backend_health()
        self.test_configuration()
        self.test_whatsapp_commands()
        self.test_edge_cases()
        
        # Print summary
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"📊 TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.failed_tests == 0:
            print(f"\n🎉 All tests passed! Your AI assistant is ready to go!")
        else:
            print(f"\n⚠️  Some tests failed. Check the output above for details.")
        
        return self.failed_tests == 0

if __name__ == "__main__":
    # Check if config is valid
    if not config.validate_config():
        print("❌ Configuration validation failed!")
        print("Please check your .env file and ensure GROQ_API_KEY is set.")
        exit(1)
    
    # Run tests
    test_runner = TestRunner()
    success = test_runner.run_all_tests()
    
    exit(0 if success else 1)