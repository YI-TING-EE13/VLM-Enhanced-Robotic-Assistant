# src/audio_recorder.py
"""
Real-time audio recording module for the VLM-Enhanced Robot Assistant.

This module provides functionality to record audio from the microphone
and save it as a WAV file for processing by the ASR system. It supports
configurable recording parameters and provides user-friendly feedback
during the recording process.

Classes:
    AudioRecorder: Handles microphone recording and WAV file generation

Dependencies:
    sounddevice: For real-time audio capture
    numpy: For audio data processing
    wave: For WAV file format support
"""

import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
from typing import Optional, List, Any

class AudioRecorder:
    """
    Handles real-time audio recording from the microphone.
    
    This class provides methods to record audio from the default microphone,
    save it as a WAV file, and manage the recording process with user feedback.
    """
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        """
        Initialize the audio recorder.
        
        Args:
            sample_rate (int): Sample rate for recording (default: 16000 Hz, optimal for Whisper)
            channels (int): Number of audio channels (default: 1 for mono)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.audio_data: List[np.ndarray] = []
    
    def record_audio(self, duration: float = 5.0, countdown: bool = True) -> str:
        """
        Record audio from the microphone and save it as a temporary WAV file.
        
        Args:
            duration (float): Recording duration in seconds (default: 5.0)
            countdown (bool): Whether to show a countdown before recording
            
        Returns:
            str: Path to the temporary WAV file containing the recorded audio
        """
        if countdown:
            print("\n🎤 準備開始錄音...")
            print("請在聽到提示音後開始說話")
            for i in range(3, 0, -1):
                print(f"⏰ {i}...")
                sd.sleep(1000)  # Sleep for 1 second
        
        print(f"🔴 開始錄音 ({duration} 秒)...")
        
        # Record audio
        audio_data: np.ndarray = sd.rec(
            int(duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32
        )
        
        # Wait for recording to complete
        sd.wait()
        
        print("✅ 錄音完成！")
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Save as WAV file
        self._save_wav(audio_data, temp_path)
        
        return temp_path
    
    def record_audio_interactive(self) -> str:
        """
        Record audio with interactive controls (press Enter to start/stop).
        
        Returns:
            str: Path to the temporary WAV file containing the recorded audio
        """
        print("\n🎤 互動式錄音模式")
        print("按 Enter 開始錄音...")
        input()
        
        print("🔴 開始錄音...")
        print("按 Enter 停止錄音...")
        
        # Start recording in a separate thread
        audio_data: List[np.ndarray] = []
        
        def audio_callback(indata: np.ndarray, frames: int, time: Any, status: Any) -> None:
            if status:
                print(f"錄音狀態: {status}")
            audio_data.append(indata.copy())
        
        # Start recording
        with sd.InputStream(
            callback=audio_callback,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=np.float32
        ):
            input()  # Wait for user to press Enter
        
        print("✅ 錄音完成！")
        
        if not audio_data:
            raise RuntimeError("沒有錄製到音頻數據")
        
        # Concatenate all audio chunks
        full_audio: np.ndarray = np.concatenate(audio_data, axis=0)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        # Save as WAV file
        self._save_wav(full_audio, temp_path)
        
        return temp_path
    
    def _save_wav(self, audio_data: np.ndarray, file_path: str) -> None:
        """
        Save audio data as a WAV file.
        
        Args:
            audio_data (np.ndarray): Audio data to save
            file_path (str): Path where to save the WAV file
        """
        # Convert float32 to int16
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(file_path, 'w') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 2 bytes for int16
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    
    def cleanup_temp_file(self, file_path: str) -> None:
        """
        Clean up temporary audio file.
        
        Args:
            file_path (str): Path to the temporary file to delete
        """
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                print(f"🗑️ 清理暫存檔案: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"⚠️ 清理檔案時發生錯誤: {e}")
    
    @staticmethod
    def list_audio_devices() -> None:
        """
        List available audio devices for debugging purposes.
        """
        print("\n🔊 可用的音頻設備:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} (輸入: {device['max_input_channels']} 聲道)")