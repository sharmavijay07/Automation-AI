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
  
  const {
    backendStatus,
    isProcessing,
    lastResult,
    executeCommand,
    executeWorkflow,
    checkStatus
  } = useCrewAI();
  
  const { playSound } = useSound();
  const { isListening: voiceListening, startVoiceRecognition } = useVoiceRecognition();
  
  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

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
        
        // Process the voice command
        const result = await executeCommand(transcript);
        
        if (result) {
          setShowResults(true);
          playSound(result.success ? 'success' : 'error');
          
          // Optional: Play TTS feedback
          if (result.success) {
            console.log('✅ Command executed successfully');
          } else {
            console.log('❌ Command failed:', result.message);
          }
        } else {
          playSound('error');
          console.log('❌ No result received from backend');
        }
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
            onClose={() => setShowResults(false)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
