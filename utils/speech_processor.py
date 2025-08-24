"""
Speech Processing Utilities for AI Task Automation Assistant
Handles speech-to-text and text-to-speech functionality
"""

import speech_recognition as sr
# Audio playback libraries commented out to avoid dependency issues
# import pygame
# import io
import os
import tempfile
# from gtts import gTTS
from typing import Optional, Tuple
import streamlit as st
from config import config

class SpeechProcessor:
    """Handles speech recognition and text-to-speech conversion"""
    
    def __init__(self):
        # Initialize speech recognizer with optimized settings
        self.recognizer = sr.Recognizer()
        
        # Configure speech recognition settings based on memory specifications
        self.recognizer.energy_threshold = 300  # Energy threshold for ambient noise
        self.recognizer.pause_threshold = 0.8   # Pause threshold
        self.recognizer.dynamic_energy_adjustment = True  # Dynamic energy adjustment
        
        self.microphone = sr.Microphone()
        
        # Audio playback disabled to avoid dependency issues
        # Following memory specification for audio workaround
        self.audio_initialized = False
        # Note: Audio playback disabled (using minimal setup for compatibility)
        
        # Adjust for ambient noise
        self._calibrate_microphone()
    
    def display_status(self):
        """Display status information in the UI"""
        if hasattr(st, 'info'):
            st.info("🔇 Audio playback disabled (using minimal setup for compatibility)")
            if hasattr(self, 'calibration_error'):
                st.warning(self.calibration_error)
    
    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        try:
            with self.microphone as source:
                # Ambient noise calibration for 1.5 seconds as per memory specs
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        except Exception as e:
            # Store error for later display instead of immediate st.warning
            self.calibration_error = f"⚠️ Microphone calibration failed: {str(e)}"
            pass
    
    def listen_for_speech(self, timeout: int = 7, phrase_time_limit: int = 15) -> Tuple[bool, str]:
        """
        Listen for speech input from microphone
        
        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time for a phrase
            
        Returns:
            Tuple of (success: bool, text: str)
        """
        try:
            with self.microphone as source:
                # Listen for audio
                st.info("🎤 Listening... Speak now!")
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout, 
                    phrase_time_limit=phrase_time_limit
                )
                
                # Recognize speech using Google Speech Recognition with language fallback
                # First attempt 'en-US' (American English), fallback to 'en-IN' (Indian English)
                st.info("🔄 Processing speech...")
                try:
                    text = self.recognizer.recognize_google(audio, language="en-US")
                except sr.UnknownValueError:
                    # Fallback to Indian English
                    try:
                        text = self.recognizer.recognize_google(audio, language="en-IN")
                    except sr.UnknownValueError:
                        return False, "🔇 Could not understand the speech. Please try again."
                
                return True, text
                
        except sr.WaitTimeoutError:
            return False, "⏰ Listening timeout. No speech detected."
        except sr.UnknownValueError:
            return False, "🔇 Could not understand the speech. Please try again."
        except sr.RequestError as e:
            return False, f"❌ Speech recognition service error: {str(e)}"
        except Exception as e:
            return False, f"❌ Speech recognition error: {str(e)}"
    
    def text_to_speech(self, text: str, language: str = 'en') -> bool:
        """Text-to-speech disabled in minimal setup"""
        # Audio playback disabled to avoid dependency issues
        # Display message in UI when called, not during import
        if hasattr(st, 'info'):  # Check if Streamlit is available
            st.info(f"🔊 Would say: '{text}' (TTS disabled in minimal setup)")
        return True  # Return success to avoid errors
    
    def get_audio_devices(self) -> list:
        """Get list of available audio input devices"""
        try:
            devices = []
            for index in range(sr.Microphone.list_microphone_names().__len__()):
                device_name = sr.Microphone.list_microphone_names()[index]
                devices.append(f"{index}: {device_name}")
            return devices
        except Exception as e:
            return [f"Error getting devices: {str(e)}"]
    
    def test_microphone(self) -> Tuple[bool, str]:
        """Test microphone functionality"""
        try:
            with self.microphone as source:
                # Quick ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Test recording
                audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                
                # Test recognition
                text = self.recognizer.recognize_google(audio)
                
                return True, f"✅ Microphone test successful! Heard: '{text}'"
                
        except sr.WaitTimeoutError:
            return False, "⏰ Microphone test timeout. Try speaking during the test."
        except sr.UnknownValueError:
            return False, "🔇 Microphone working but speech was unclear."
        except sr.RequestError:
            return False, "❌ Speech recognition service unavailable."
        except Exception as e:
            return False, f"❌ Microphone test failed: {str(e)}"

# Global speech processor instance
speech_processor = SpeechProcessor()