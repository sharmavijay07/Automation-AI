'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  Bot, 
  MessageCircle, 
  FileText, 
  Calendar, 
  Zap, 
  Sparkles,
  Settings,
  Wifi,
  WifiOff
} from 'lucide-react';
import useVoiceRecognition from '@/hooks/useVoiceRecognition';
import { useCrewAI } from '@/hooks/useCrewAI';
import { useSound } from '@/hooks/useSound';
import { VoiceVisualization } from '@/components/VoiceVisualization';
import { AgentCard } from '@/components/AgentCard';
import { ResultDisplay } from '@/components/ResultDisplay';
import { StatusIndicator } from '@/components/StatusIndicator';

export default function CrewAIPage() {
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);
  const [showWhatsAppPopup, setShowWhatsAppPopup] = useState(false);
  const [isManuallyClosing, setIsManuallyClosing] = useState(false);
  
  const {
    backendStatus,
    isProcessing,
    lastResult,
    executeCommand,
    executeWorkflow,
    checkStatus,
    clearResult
  } = useCrewAI();
  
  const { playSound } = useSound();
  const { isListening: voiceListening, startVoiceRecognition } = useVoiceRecognition();
  
  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  // Handle WebSocket results for voice commands
  useEffect(() => {
    if (lastResult && !isProcessing && !isManuallyClosing) {
      console.log('🔄 Processing result:', lastResult);
      
      // Only auto-show results if they're from WebSocket (not from manual actions)
      // We can tell because WebSocket results come when not processing
      if (!showResults) {
        setShowResults(true);
        
        // Show WhatsApp popup for successful WhatsApp agent operations
        // Check multiple conditions to ensure it's actually a successful WhatsApp operation
        const isSuccessfulWhatsAppResult = lastResult.success && 
          (lastResult.agent_used?.toLowerCase().includes('whatsapp') ||
           lastResult.intent?.toLowerCase().includes('whatsapp')) &&
          !lastResult.error && // Ensure no error occurred
          (lastResult.whatsapp_url || lastResult.message?.includes('wa.me')); // Ensure we have a WhatsApp URL
           
        console.log('🔍 WhatsApp result check:', {
          success: lastResult.success,
          agent_used: lastResult.agent_used,
          intent: lastResult.intent,
          has_error: !!lastResult.error,
          has_whatsapp_url: !!lastResult.whatsapp_url,
          message_includes_wa_me: lastResult.message?.includes('wa.me'),
          isSuccessfulWhatsAppResult,
          isManuallyClosing
        });
        
        if (isSuccessfulWhatsAppResult) {
          console.log('✅ Triggering WhatsApp popup in 1.5 seconds');
          setTimeout(() => {
            setShowWhatsAppPopup(true);
          }, 1500); // Show after 1.5 seconds
        }
        
        // Play appropriate sound
        playSound(lastResult.success ? 'success' : 'error');
      }
    }
    
    // Reset manual closing flag after processing
    if (isManuallyClosing) {
      const timer = setTimeout(() => {
        setIsManuallyClosing(false);
      }, 500); // Wait 500ms to ensure modal close animation completes
      return () => clearTimeout(timer);
    }
  }, [lastResult, isProcessing, playSound, showResults, isManuallyClosing]);

  const handleVoiceStart = async () => {
    if (backendStatus !== 'online') return;
    
    playSound('start');
    
    // Use real voice recognition
    startVoiceRecognition(
      async (transcript: string) => {
        console.log('Voice transcript received:', transcript);
        playSound('processing');
        
        // Show visual feedback that we're processing
        console.log('✅ Processing command:', transcript);
        
        // Process the voice command (WebSocket will handle the result via useEffect)
        await executeCommand(transcript);
      },
      (message: string) => {
        console.log('🎤 Voice feedback:', message);
        // Show visual feedback to user (could be enhanced with toast notifications)
      }
    );
  };

  const handleAgentSelect = async (agentType: string, command: string) => {
    setCurrentAgent(agentType);
    const result = await executeWorkflow(agentType, { command });
    if (result) {
      setShowResults(true);
      
      // Show WhatsApp popup for successful WhatsApp operations from manual agent selection
      const isSuccessfulWhatsAppResult = result.success && 
        (result.agent_used?.toLowerCase().includes('whatsapp') ||
         result.intent?.toLowerCase().includes('whatsapp')) &&
        !result.error && // Ensure no error occurred
        (result.whatsapp_url || result.message?.includes('wa.me')); // Ensure we have a WhatsApp URL
        
      if (isSuccessfulWhatsAppResult) {
        setTimeout(() => {
          setShowWhatsAppPopup(true);
        }, 1500);
      }
    }
  };

  const shareToWhatsApp = async () => {
    if (!lastResult) return;
    
    // Extract WhatsApp link from the result message using regex pattern
    const whatsappLinkMatch = lastResult.message.match(/https:\/\/wa\.me\/[^\s]+/);
    if (whatsappLinkMatch) {
      // Use the existing WhatsApp link directly
      const whatsappLink = whatsappLinkMatch[0];
      setShowWhatsAppPopup(false);
      window.open(whatsappLink, '_blank');
    } else {
      // Fallback: try to extract phone number and message text separately
      const phoneMatch = lastResult.message.match(/wa\.me\/([+]?[0-9]+)/);
      const textMatch = lastResult.message.match(/text=([^&\s]+)/);
      
      if (phoneMatch && textMatch) {
        const phoneNumber = phoneMatch[1];
        const messageText = decodeURIComponent(textMatch[1]);
        const encodedPhone = encodeURIComponent(phoneNumber.startsWith('+') ? phoneNumber : '+' + phoneNumber);
        const encodedMessage = encodeURIComponent(messageText);
        const whatsappUrl = `https://api.whatsapp.com/send/?phone=${encodedPhone}&text=${encodedMessage}&type=phone_number&app_absent=0`;
        setShowWhatsAppPopup(false);
        window.open(whatsappUrl, '_blank');
      } else {
        // Final fallback - ask backend
        try {
          const response = await fetch('http://localhost:8000/process-command', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              command: `Open WhatsApp link from: ${lastResult.message}`
            })
          });
          
          if (response.ok) {
            const linkResult = await response.json();
            if (linkResult.success && linkResult.details && linkResult.details.whatsapp_link) {
              window.open(linkResult.details.whatsapp_link, '_blank');
            }
          }
          setShowWhatsAppPopup(false);
        } catch (error) {
          setShowWhatsAppPopup(false);
          console.error('Could not open WhatsApp link:', error);
        }
      }
    }
  };

  const agents = [
    {
      id: 'whatsapp',
      name: 'WhatsApp Agent',
      description: 'Send messages and create shareable links',
      icon: MessageCircle,
      color: 'from-green-500 to-emerald-600',
      command: 'Send WhatsApp message'
    },
    {
      id: 'file_management',
      name: 'File Manager',
      description: 'Search, open, and organize your files',
      icon: FileText,
      color: 'from-blue-500 to-cyan-600',
      command: 'Find and manage files'
    },
    {
      id: 'calendar',
      name: 'Calendar Agent',
      description: 'Schedule events and set reminders',
      icon: Calendar,
      color: 'from-purple-500 to-violet-600',
      command: 'Schedule appointment'
    },
    {
      id: 'research',
      name: 'Research Agent',
      description: 'Find information and conduct research',
      icon: Sparkles,
      color: 'from-orange-500 to-red-600',
      command: 'Research information'
    }
  ];

  return (
    <div className="min-h-screen p-4 md:p-8">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center mb-8"
      >
        <div className="flex items-center space-x-4">
          <motion.div
            whileHover={{ rotate: 360 }}
            transition={{ duration: 0.5 }}
            className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center"
          >
            <Bot className="w-8 h-8 text-white" />
          </motion.div>
          <div>
            <h1 className="text-3xl font-bold text-white">CrewAI Assistant</h1>
            <p className="text-gray-300">Multi-Agent AI System</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <StatusIndicator 
            status={backendStatus} 
            label="Backend" 
          />
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="glass p-3 rounded-xl text-white hover:bg-white/20 transition-all"
          >
            <Settings className="w-6 h-6" />
          </motion.button>
        </div>
      </motion.header>
      
      {/* Main Voice Interface */}
      <motion.section 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="text-center mb-12"
      >
        <motion.div
          className="relative mx-auto mb-8"
          style={{ width: 'fit-content' }}
        >
          <motion.button
            onClick={handleVoiceStart}
            disabled={backendStatus !== 'online' || voiceListening || isProcessing}
            className={`
              relative w-48 h-48 rounded-full transition-all duration-300 transform
              ${voiceListening 
                ? 'bg-red-500 shadow-2xl scale-110 animate-pulse' 
                : isProcessing
                ? 'bg-yellow-500 shadow-xl animate-bounce'
                : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 shadow-xl hover:shadow-2xl hover:scale-105'
              }
              disabled:opacity-50 disabled:cursor-not-allowed
              glass-strong voice-ripple ${voiceListening ? 'active' : ''}
            `}
            whileHover={{ scale: backendStatus === 'online' ? 1.05 : 1 }}
            whileTap={{ scale: backendStatus === 'online' ? 0.95 : 1 }}
          >
            <div className="absolute inset-4 rounded-full bg-white/20 flex items-center justify-center">
              <AnimatePresence mode="wait">
                {voiceListening ? (
                  <motion.div
                    key="listening"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="flex flex-col items-center"
                  >
                    <Mic className="w-16 h-16 text-white animate-pulse" />
                    <span className="text-white text-sm font-bold mt-2">Listening...</span>
                  </motion.div>
                ) : isProcessing ? (
                  <motion.div
                    key="processing"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="flex flex-col items-center"
                  >
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    >
                      <Zap className="w-16 h-16 text-white" />
                    </motion.div>
                    <span className="text-white text-sm font-bold mt-2">Processing...</span>
                  </motion.div>
                ) : (
                  <motion.div
                    key="ready"
                    initial={{ opacity: 0, scale: 0.5 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.5 }}
                    className="flex flex-col items-center"
                  >
                    <Mic className="w-16 h-16 text-white group-hover:scale-110 transition-transform" />
                    <span className="text-white text-lg font-bold mt-2">TAP TO SPEAK</span>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            
            {/* Ripple effect */}
            {(voiceListening || isProcessing) && (
              <motion.div 
                className="absolute inset-0 rounded-full border-4 border-white"
                animate={{
                  scale: [1, 1.2, 1],
                  opacity: [0.8, 0, 0.8]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              />
            )}
          </motion.button>
          
          {/* Voice Visualization */}
          <VoiceVisualization isActive={voiceListening} />
        </motion.div>
        
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-xl text-gray-300 mb-4"
        >
          Speak naturally or choose an agent below
        </motion.p>
        
        {backendStatus !== 'online' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-400"
          >
            <WifiOff className="w-5 h-5 mr-2" />
            Backend Offline - Please start the CrewAI server
          </motion.div>
        )}
      </motion.section>
      
      {/* Agent Cards */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mb-12"
      >
        <h2 className="text-2xl font-bold text-white text-center mb-8">Specialized Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agents.map((agent, index) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              isActive={currentAgent === agent.id}
              isDisabled={backendStatus !== 'online'}
              onClick={() => handleAgentSelect(agent.id, agent.command)}
              delay={index * 0.1}
            />
          ))}
        </div>
      </motion.section>
      
      {/* Results Display */}
      <AnimatePresence>
        {showResults && lastResult && (
          <ResultDisplay
            result={lastResult}
            onClose={() => {
              console.log('🚪 Manually closing results display');
              setIsManuallyClosing(true);
              setShowResults(false);
              setShowWhatsAppPopup(false); // Also close WhatsApp popup if open
              // Clear the lastResult to prevent modal from reopening
              setTimeout(() => {
                clearResult();
              }, 300); // Small delay to allow close animation
            }}
          />
        )}
      </AnimatePresence>
      
      {/* WhatsApp Popup */}
      <AnimatePresence>
        {showWhatsAppPopup && lastResult && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4"
            onClick={(e) => {
              e.preventDefault();
              setShowWhatsAppPopup(false);
            }}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ type: "spring", duration: 0.5 }}
              className="bg-white rounded-2xl p-6 max-w-md w-full mx-4 shadow-2xl relative"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Close button */}
              <button
                onClick={(e) => {
                  e.preventDefault();
                  e.stopPropagation();
                  setShowWhatsAppPopup(false);
                }}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
                aria-label="Close popup"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
              
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
                  <MessageCircle className="w-8 h-8 text-green-600" />
                </div>
                
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  WhatsApp Message Ready!
                </h3>
                
                {lastResult.agent_used && (
                  <div className="mb-3 px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full inline-block">
                    🤖 {lastResult.agent_used} Agent
                  </div>
                )}
                
                <p className="text-sm text-gray-600 mb-6 leading-relaxed">
                  Your WhatsApp message has been processed successfully. Click below to open WhatsApp and send your message.
                </p>
                
                {lastResult.message && (
                  <div className="mb-6 p-3 bg-gray-50 rounded-lg text-left">
                    <p className="text-xs text-gray-500 mb-1">Message Details:</p>
                    <p className="text-sm text-gray-700 line-clamp-3">{lastResult.message}</p>
                  </div>
                )}
                
                <div className="flex space-x-3">
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      setShowWhatsAppPopup(false);
                    }}
                    className="flex-1 px-4 py-3 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors font-medium"
                  >
                    Not Now
                  </button>
                  <button
                    onClick={(e) => {
                      e.preventDefault();
                      e.stopPropagation();
                      shareToWhatsApp();
                    }}
                    className="flex-1 px-4 py-3 text-white bg-green-600 hover:bg-green-700 rounded-lg transition-colors font-medium flex items-center justify-center space-x-2"
                  >
                    <MessageCircle className="w-4 h-4" />
                    <span>Open WhatsApp</span>
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
