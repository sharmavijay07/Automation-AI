'use client';

import { useState, useEffect } from 'react';
import { Mic, MicOff, Send, Bot, MessageCircle, Phone, Calendar, FileText, X, CheckCircle, AlertCircle, Volume2, Sparkles } from 'lucide-react';

interface CommandResult {
  success: boolean;
  message: string;
  intent: string;
  agent_used: string;
  timestamp: string;
  details?: any;
}

type BubbleType = 'whatsapp' | 'call' | 'calendar' | 'files' | null;

export default function Home() {
  const [isListening, setIsListening] = useState(false);
  const [command, setCommand] = useState('');
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeBubble, setActiveBubble] = useState<BubbleType>(null);
  const [showCommandPopup, setShowCommandPopup] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [lastResult, setLastResult] = useState<CommandResult | null>(null);
  const [showResult, setShowResult] = useState(false);
  const [floatingElements, setFloatingElements] = useState<Array<{id: number; x: number; y: number; delay: number}>>([]);

  // Check backend status
  useEffect(() => {
    checkBackendStatus();
    const interval = setInterval(checkBackendStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Auto-hide result
  useEffect(() => {
    if (showResult) {
      const timer = setTimeout(() => setShowResult(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [showResult]);

  // Create floating background elements
  useEffect(() => {
    const elements = Array.from({ length: 8 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 4
    }));
    setFloatingElements(elements);
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: cmdText }),
      });

      const result: CommandResult = await response.json();
      setCommand('');
      setLastResult(result);
      setShowResult(true);
      setShowCommandPopup(false);
      setActiveBubble(null);
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
      
      recognition.onstart = () => setIsListening(true);
      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setCommand(transcript);
        sendCommand(transcript);
      };
      recognition.onerror = () => setIsListening(false);
      recognition.onend = () => setIsListening(false);
      
      recognition.start();
    } else {
      alert('Speech recognition not supported. Please use Chrome or Edge.');
    }
  };

  const openBubble = (type: BubbleType, agentName: string) => {
    setActiveBubble(type);
    setSelectedAgent(agentName);
    setShowCommandPopup(true);
    setCommand('');
  };

  const closeBubble = () => {
    setShowCommandPopup(false);
    setActiveBubble(null);
    setSelectedAgent('');
    setCommand('');
  };

  const quickCommands = {
    whatsapp: [
      "Send message to Mom: I'm coming home",
      "Tell Dad: I'll call you later",
      "Message friend: How are you doing?",
      "Send to family group: Good morning everyone"
    ],
    call: [
      "Call Mom",
      "Call emergency contact",
      "Call doctor",
      "Call family"
    ],
    calendar: [
      "Add reminder: Take medicine at 8 PM",
      "Schedule doctor appointment tomorrow",
      "Remind me to call in 1 hour",
      "Add event: Family dinner Sunday"
    ],
    files: [
      "Open my photos",
      "Find important documents",
      "Show recent files",
      "Open music folder"
    ]
  };

  const handleQuickCommand = (commandText: string) => {
    setCommand(commandText);
    sendCommand(commandText);
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
        {/* Floating Background Elements */}
        {floatingElements.map((element) => (
          <div
            key={element.id}
            className="absolute rounded-full opacity-20 animate-pulse"
            style={{
              left: `${element.x}%`,
              top: `${element.y}%`,
              width: `${60 + Math.random() * 100}px`,
              height: `${60 + Math.random() * 100}px`,
              background: `linear-gradient(45deg, ${[
                '#3B82F6', '#8B5CF6', '#EC4899', '#10B981', '#F59E0B'
              ][Math.floor(Math.random() * 5)]}, transparent)`,
              animationDelay: `${element.delay}s`,
              animationDuration: `${3 + Math.random() * 2}s`
            }}
          />
        ))}
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex flex-col">
        {/* Simple Header */}
        <header className="text-center py-8">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <Bot className="w-16 h-16 text-blue-600 animate-bounce" />
              <Sparkles className="w-6 h-6 text-yellow-500 absolute -top-2 -right-2 animate-spin" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">AI Assistant</h1>
          <p className="text-xl text-gray-600">Just speak or tap to get help!</p>
          
          {/* Status Indicator */}
          <div className="flex items-center justify-center mt-4">
            <div className={`w-4 h-4 rounded-full mr-3 ${
              backendStatus === 'online' ? 'bg-green-500 animate-pulse' :
              backendStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-spin'
            }`} />
            <span className="text-lg font-medium text-gray-700">
              {backendStatus === 'online' ? '✅ Ready to Help' :
               backendStatus === 'offline' ? '❌ Connection Issue' : '🔄 Connecting...'}
            </span>
          </div>
        </header>

        {/* Main Action Area */}
        <div className="flex-1 flex flex-col items-center justify-center px-4 max-w-6xl mx-auto w-full">
          
          {/* Large Voice Button */}
          <div className="mb-12">
            <button
              onClick={startVoiceRecognition}
              disabled={backendStatus !== 'online' || isListening || isProcessing}
              className={`group relative w-48 h-48 rounded-full transition-all duration-300 transform hover:scale-110 ${
                isListening 
                  ? 'bg-red-500 shadow-2xl animate-pulse scale-110' 
                  : isProcessing
                  ? 'bg-yellow-500 shadow-xl animate-bounce'
                  : 'bg-blue-500 hover:bg-blue-600 shadow-xl hover:shadow-2xl'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <div className="absolute inset-4 rounded-full bg-white bg-opacity-20 flex items-center justify-center">
                {isListening ? (
                  <div className="flex flex-col items-center">
                    <Mic className="w-16 h-16 text-white animate-pulse" />
                    <span className="text-white text-sm font-bold mt-2">Listening...</span>
                  </div>
                ) : isProcessing ? (
                  <div className="flex flex-col items-center">
                    <Bot className="w-16 h-16 text-white animate-spin" />
                    <span className="text-white text-sm font-bold mt-2">Processing...</span>
                  </div>
                ) : (
                  <div className="flex flex-col items-center">
                    <Mic className="w-16 h-16 text-white group-hover:scale-110 transition-transform" />
                    <span className="text-white text-lg font-bold mt-2">TAP TO SPEAK</span>
                  </div>
                )}
              </div>
              
              {/* Ripple effect */}
              {(isListening || isProcessing) && (
                <div className="absolute inset-0 rounded-full border-4 border-white animate-ping opacity-30" />
              )}
            </button>
          </div>

          {/* Function Bubbles */}
          <div className="grid grid-cols-2 gap-8 mb-8 w-full max-w-4xl">
            {/* WhatsApp Bubble */}
            <div 
              onClick={() => openBubble('whatsapp', 'WhatsApp')}
              className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
            >
              <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-green-200 group-hover:border-green-400 group-hover:shadow-2xl">
                <div className="relative mb-4">
                  <MessageCircle className="w-16 h-16 text-green-500 mx-auto group-hover:animate-bounce" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 rounded-full animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Send Message</h3>
                <p className="text-gray-600 text-lg">Tap to send WhatsApp</p>
              </div>
            </div>

            {/* Call Bubble */}
            <div 
              onClick={() => openBubble('call', 'Phone')}
              className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
            >
              <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-blue-200 group-hover:border-blue-400 group-hover:shadow-2xl">
                <div className="relative mb-4">
                  <Phone className="w-16 h-16 text-blue-500 mx-auto group-hover:animate-bounce" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-500 rounded-full animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Make Call</h3>
                <p className="text-gray-600 text-lg">Tap to call someone</p>
              </div>
            </div>

            {/* Calendar Bubble */}
            <div 
              onClick={() => openBubble('calendar', 'Calendar')}
              className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
            >
              <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-purple-200 group-hover:border-purple-400 group-hover:shadow-2xl">
                <div className="relative mb-4">
                  <Calendar className="w-16 h-16 text-purple-500 mx-auto group-hover:animate-bounce" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-orange-500 rounded-full animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">Reminders</h3>
                <p className="text-gray-600 text-lg">Tap to set reminders</p>
              </div>
            </div>

            {/* Files Bubble */}
            <div 
              onClick={() => openBubble('files', 'Files')}
              className="group cursor-pointer transform transition-all duration-300 hover:scale-110 hover:-translate-y-2"
            >
              <div className="bg-white rounded-3xl shadow-xl p-8 text-center border-4 border-orange-200 group-hover:border-orange-400 group-hover:shadow-2xl">
                <div className="relative mb-4">
                  <FileText className="w-16 h-16 text-orange-500 mx-auto group-hover:animate-bounce" />
                  <div className="absolute -top-2 -right-2 w-6 h-6 bg-blue-500 rounded-full animate-pulse" />
                </div>
                <h3 className="text-2xl font-bold text-gray-800 mb-2">My Files</h3>
                <p className="text-gray-600 text-lg">Tap to open files</p>
              </div>
            </div>
          </div>
        </div>

        {/* Command Popup Modal */}
        {showCommandPopup && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto animate-scale-in">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-200">
                <div className="flex items-center">
                  {activeBubble === 'whatsapp' && <MessageCircle className="w-8 h-8 text-green-500 mr-3" />}
                  {activeBubble === 'call' && <Phone className="w-8 h-8 text-blue-500 mr-3" />}
                  {activeBubble === 'calendar' && <Calendar className="w-8 h-8 text-purple-500 mr-3" />}
                  {activeBubble === 'files' && <FileText className="w-8 h-8 text-orange-500 mr-3" />}
                  <h2 className="text-3xl font-bold text-gray-800">{selectedAgent}</h2>
                </div>
                <button
                  onClick={closeBubble}
                  className="w-12 h-12 rounded-full bg-gray-100 hover:bg-gray-200 flex items-center justify-center transition-colors"
                  aria-label="Close modal"
                  title="Close modal"
                >
                  <X className="w-6 h-6 text-gray-600" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6">
                {/* Voice Command Button */}
                <button
                  onClick={startVoiceRecognition}
                  disabled={isListening || isProcessing}
                  className={`w-full mb-6 p-4 rounded-2xl text-white font-bold text-xl transition-all duration-300 transform hover:scale-105 ${
                    isListening 
                      ? 'bg-red-500 animate-pulse' 
                      : isProcessing
                      ? 'bg-yellow-500 animate-bounce'
                      : 'bg-blue-500 hover:bg-blue-600'
                  }`}
                >
                  {isListening ? (
                    <div className="flex items-center justify-center">
                      <Mic className="w-8 h-8 mr-3 animate-pulse" />
                      🎤 Listening... Speak now!
                    </div>
                  ) : isProcessing ? (
                    <div className="flex items-center justify-center">
                      <Bot className="w-8 h-8 mr-3 animate-spin" />
                      ⚡ Processing your command...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center">
                      <Volume2 className="w-8 h-8 mr-3" />
                      🗣️ TAP TO SPEAK YOUR COMMAND
                    </div>
                  )}
                </button>

                {/* Text Input */}
                <div className="mb-6">
                  <label className="block text-lg font-semibold text-gray-700 mb-3">Or type your command:</label>
                  <div className="flex gap-3">
                    <input
                      type="text"
                      value={command}
                      onChange={(e) => setCommand(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && sendCommand(command)}
                      placeholder={`Type your ${selectedAgent.toLowerCase()} command...`}
                      className="flex-1 p-4 text-lg border-2 border-gray-300 rounded-2xl focus:border-blue-500 focus:outline-none"
                    />
                    <button
                      onClick={() => sendCommand(command)}
                      disabled={!command.trim() || isProcessing}
                      className="px-6 py-4 bg-blue-500 text-white rounded-2xl hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      aria-label="Send command"
                      title="Send command"
                    >
                      <Send className="w-6 h-6" />
                    </button>
                  </div>
                </div>

                {/* Quick Commands */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-700 mb-4">💡 Quick Commands:</h3>
                  <div className="grid gap-3">
                    {activeBubble && quickCommands[activeBubble]?.map((cmd, index) => (
                      <button
                        key={index}
                        onClick={() => handleQuickCommand(cmd)}
                        className="text-left p-4 bg-gray-50 hover:bg-blue-50 rounded-xl border-2 border-transparent hover:border-blue-200 transition-all duration-200 text-gray-700 hover:text-blue-700"
                      >
                        <span className="text-2xl mr-3">👆</span>
                        {cmd}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Result Notification */}
        {showResult && lastResult && (
          <div className="fixed top-6 right-6 z-50 animate-slide-in">
            <div className={`max-w-md p-6 rounded-2xl shadow-2xl border-2 ${
              lastResult.success 
                ? 'bg-green-50 border-green-200 text-green-800'
                : 'bg-red-50 border-red-200 text-red-800'
            }`}>
              <div className="flex items-start">
                <div className="mr-3 mt-1">
                  {lastResult.success ? (
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  ) : (
                    <AlertCircle className="w-6 h-6 text-red-600" />
                  )}
                </div>
                <div className="flex-1">
                  <h4 className="font-bold text-lg mb-2">
                    {lastResult.success ? '✅ Success!' : '❌ Error'}
                  </h4>
                  <p className="text-sm">{lastResult.message}</p>
                  <div className="text-xs mt-2 opacity-75">
                    Agent: {lastResult.agent_used} • {new Date(lastResult.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <button
                  onClick={() => setShowResult(false)}
                  className="ml-2 w-6 h-6 rounded-full bg-black bg-opacity-10 hover:bg-opacity-20 flex items-center justify-center"
                  aria-label="Close notification"
                  title="Close notification"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes scale-in {
          from {
            opacity: 0;
            transform: scale(0.8);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
        
        @keyframes slide-in {
          from {
            opacity: 0;
            transform: translateX(100%);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        .animate-scale-in {
          animation: scale-in 0.3s ease-out;
        }
        
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}