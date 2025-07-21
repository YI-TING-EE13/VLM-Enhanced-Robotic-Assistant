# src/asr/whisper_asr.py
from .asr_interface import ASRInterface
import whisper
import os
import torch

class WhisperASR(ASRInterface):
    """
    Provides an Automatic Speech Recognition (ASR) service using OpenAI's
    Whisper model.

    This class implements the ASRInterface and is responsible for loading a
    specified Whisper model and using it to transcribe audio files. It handles
    file validation and manages the transcription process, including language
    specification for improved accuracy.

    Note:
        This implementation requires `ffmpeg` to be installed on the system and
        accessible in the environment's PATH for audio processing.
    """

    def __init__(self, model_name: str = "base"):
        """
        Loads a specified Whisper model into memory.

        Upon initialization, this method checks for available GPU and loads the
        model accordingly. Using a GPU is highly recommended for better performance.

        Args:
            model_name (str): The name of the Whisper model to load. Options
                              include "tiny", "base", "small", "medium", "large".
                              Larger models offer higher accuracy at the cost of
                              increased resource consumption and slower speed.
                              Defaults to "base".
        """
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"WhisperASR: Loading model '{model_name}' onto device '{device}'.")
        try:
            self.model = whisper.load_model(model_name, device=device)
            print("WhisperASR: Model loaded successfully.")
        except Exception as e:
            print(f"WhisperASR: Failed to load model '{model_name}'. Error: {e}")
            raise

    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribes an audio file into Traditional Chinese text.

        This method validates the existence of the audio file, then invokes the
        Whisper model to perform the transcription. It is configured to expect
        Chinese language input for optimal results.

        Args:
            audio_file_path (str): The absolute path to the audio file.

        Returns:
            str: The transcribed text as a string.

        Raises:
            FileNotFoundError: If the audio file does not exist at the given path.
            Exception: For errors raised by the Whisper library during transcription,
                       which can include issues with `ffmpeg` or corrupted audio data.
        """
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found at: {audio_file_path}")

        try:
            print(f"WhisperASR: Starting transcription for {os.path.basename(audio_file_path)}...")
            # The 'language' parameter helps improve accuracy by focusing the model.
            result = self.model.transcribe(audio_file_path, language="chinese", fp16=torch.cuda.is_available())
            
            transcribed_text = result.get("text", "").strip()
            print("WhisperASR: Transcription successful.")
            return transcribed_text
        except Exception as e:
            print(f"WhisperASR: An error occurred during transcription: {e}")
            # Re-raising the exception allows the caller to handle it,
            # which is a better practice than returning an empty string.
            raise
