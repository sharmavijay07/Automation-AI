'use client';

import { useState, useEffect } from 'react';
import { Mic, MicOff, Send, Bot, Phone, Calendar, FileText, Search, MessageCircle, Settings } from 'lucide-react';

interface CommandResult {
  success: boolean;
  message: string;
  intent: string;
  agent_used: string;
  timestamp: string;
  details?: any;
}

interface CommandHistory {
  timestamp: string;
  command: string;
  result: CommandResult;
}

export default function Home() {
  const [isListening, setIsListening] = useState(false);
  const [command, setCommand] = useState('');
  const [commandHistory, setCommandHistory] = useState<CommandHistory[]>([]);
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [isProcessing, setIsProcessing] = useState(false);

  // Check backend status
  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkBackendStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setBackendStatus('online');
      } else {
        setBackendStatus('offline');
      }
    } catch {
      setBackendStatus('offline');
    }
  };

  const sendCommand = async (cmdText: string) => {
    if (!cmdText.trim() || backendStatus !== 'online') return;

    setIsProcessing(true);
    try {
      const response = await fetch('http://localhost:8000/process-command', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command: cmdText }),
      });

      const result: CommandResult = await response.json();
      
      const historyItem: CommandHistory = {
        timestamp: new Date().toLocaleTimeString(),
        command: cmdText,
        result,
      };
      
      setCommandHistory(prev => [historyItem, ...prev.slice(0, 9)]); // Keep last 10 items
      setCommand('');
    } catch (error) {
      console.error('Error sending command:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const startVoiceRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
      };
      
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setCommand(transcript);
        sendCommand(transcript);
      };
      
      recognition.onerror = () => {
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognition.start();
    } else {
      alert('Speech recognition not supported in this browser');
    }
  };

  const agents = [
    { name: 'WhatsApp', icon: MessageCircle, color: 'bg-green-500', description: 'Send messages' },
    { name: 'Call', icon: Phone, color: 'bg-blue-500', description: 'Make calls' },
    { name: 'Calendar', icon: Calendar, color: 'bg-purple-500', description: 'Manage events' },
    { name: 'Files', icon: FileText, color: 'bg-orange-500', description: 'File operations' },
    { name: 'Search', icon: Search, color: 'bg-indigo-500', description: 'Web search' },
    { name: 'Settings', icon: Settings, color: 'bg-gray-500', description: 'Configuration' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-2 rounded-xl">
                <Bot className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">AI Task Assistant</h1>
                <p className="text-sm text-gray-600 dark:text-gray-400">Voice-powered daily automation</p>
              </div>
            </div>
            
            {/* Backend Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${
                backendStatus === 'online' ? 'bg-green-500' :
                backendStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {backendStatus === 'online' ? 'Connected' :
                 backendStatus === 'offline' ? 'Disconnected' : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Command Input Section */}
        <div className="mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
              <Mic className="mr-2 h-5 w-5" />
              Give Your Command
            </h2>
            
            {/* Voice Input */}
            <div className="flex flex-col sm:flex-row gap-4 mb-4">
              <button
                onClick={startVoiceRecognition}
                disabled={isListening || backendStatus !== 'online'}
                className={`flex-1 flex items-center justify-center space-x-2 py-4 px-6 rounded-xl font-medium transition-all ${
                  isListening 
                    ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse' 
                    : backendStatus === 'online'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                <span>{isListening ? 'Listening...' : 'Start Voice Command'}</span>
              </button>
            </div>
            
            {/* Text Input */}
            <div className="flex gap-3">
              <input
                type="text"
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendCommand(command)}
                placeholder="Or type your command here... (e.g., Send WhatsApp to Jay: Hello!)"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                disabled={backendStatus !== 'online'}
              />
              <button
                onClick={() => sendCommand(command)}
                disabled={!command.trim() || isProcessing || backendStatus !== 'online'}
                className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white rounded-xl transition-colors flex items-center space-x-2"
              >
                <Send className="h-4 w-4" />
                <span>Send</span>
              </button>
            </div>
            
            {/* Processing Indicator */}
            {isProcessing && (
              <div className="mt-4 flex items-center justify-center text-blue-500">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mr-2"></div>
                <span>Processing command...</span>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Available Agents */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Available Agents</h3>
              <div className="space-y-3">
                {agents.map((agent, index) => {
                  const Icon = agent.icon;
                  return (
                    <div key={index} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer">
                      <div className={`p-2 rounded-lg ${agent.color}`}>
                        <Icon className="h-4 w-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 dark:text-white">{agent.name}</p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">{agent.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Voice Tips */}
            <div className="mt-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-700 dark:to-purple-900 rounded-2xl p-6 border border-blue-200 dark:border-purple-700">
              <h4 className="font-semibold text-blue-900 dark:text-blue-100 mb-3">💡 Voice Command Tips</h4>
              <ul className="text-sm text-blue-800 dark:text-blue-200 space-y-2">
                <li>• "Send WhatsApp to Jay: Hello how are you"</li>
                <li>• "Message Mom: I'll be late today"</li>
                <li>• "WhatsApp Vijay: Meeting at 5 PM"</li>
                <li>• Speak clearly and at normal pace</li>
                <li>• Start speaking immediately after clicking</li>
              </ul>
            </div>
          </div>

          {/* Command History */}
          <div className="lg:col-span-2">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-200 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Command History</h3>
              
              {commandHistory.length === 0 ? (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No commands yet. Try saying "Send WhatsApp to Jay: Hello!"</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {commandHistory.map((item, index) => (
                    <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 dark:text-white">{item.command}</p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">{item.timestamp}</p>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                          item.result.success 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {item.result.success ? 'Success' : 'Failed'}
                        </div>
                      </div>
                      
                      <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 mt-2">
                        <p className="text-sm text-gray-700 dark:text-gray-300">{item.result.message}</p>
                        <div className="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
                          <span>Agent: {item.result.agent_used}</span>
                          <span>Intent: {item.result.intent}</span>
                        </div>
                        
                        {/* WhatsApp URL */}
                        {item.result.details?.agent_response?.whatsapp_url && (
                          <div className="mt-2">
                            <a 
                              href={item.result.details.agent_response.whatsapp_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center space-x-1 text-green-600 hover:text-green-800 text-sm font-medium"
                            >
                              <MessageCircle className="h-4 w-4" />
                              <span>Open WhatsApp</span>
                            </a>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
