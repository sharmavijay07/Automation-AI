'use client';

import { useCallback } from 'react';
import useSoundHook from 'use-sound';

type SoundType = 'start' | 'success' | 'error' | 'processing' | 'notification';

export function useSound() {
  // In a real implementation, you would load actual sound files
  // For now, we'll use Web Audio API for simple beeps
  
  const playBeep = useCallback((frequency: number, duration: number = 200) => {
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = frequency;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + duration / 1000);
    } catch (error) {
      console.warn('Audio playback failed:', error);
    }
  }, []);
  
  const playSound = useCallback((type: SoundType) => {
    switch (type) {
      case 'start':
        playBeep(800, 150);
        break;
      case 'success':
        // Play a success chord
        playBeep(523, 100); // C
        setTimeout(() => playBeep(659, 100), 100); // E
        setTimeout(() => playBeep(784, 200), 200); // G
        break;
      case 'error':
        playBeep(300, 300);
        break;
      case 'processing':
        playBeep(600, 100);
        break;
      case 'notification':
        playBeep(440, 150);
        setTimeout(() => playBeep(554, 150), 150);
        break;
      default:
        playBeep(440, 100);
    }
  }, [playBeep]);
  
  const playTTS = useCallback(async (text: string, language: string = 'en') => {
    try {
      const response = await fetch('http://localhost:8000/text-to-speech', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text,
          language,
          voice_speed: 1.0
        }),
        cache: 'no-cache'
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('🔊 TTS result:', result);
        return result;
      }
    } catch (error) {
      console.warn('TTS failed:', error);
    }
    
    return null;
  }, []);
  
  return {
    playSound,
    playTTS,
    playBeep
  };
}