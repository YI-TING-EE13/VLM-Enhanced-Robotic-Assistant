# src/asr/asr_interface.py
from abc import ABC, abstractmethod

class ASRInterface(ABC):
    """
    Defines the interface for Automatic Speech Recognition (ASR) services.

    This abstract base class serves as a contract for all ASR implementations
    within the system. By adhering to this interface, different ASR models
    (e.g., Whisper, FunASR) can be used interchangeably without requiring
    modifications to the core application logic. This promotes modularity and
    flexibility.
    """

    @abstractmethod
    def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribes a given audio file into its text representation.

        Args:
            audio_file_path (str): The absolute path to the audio file that
                                   needs to be transcribed.

        Returns:
            str: The transcribed text, expected to be in Traditional Chinese.

        Raises:
            FileNotFoundError: If the specified audio file cannot be found.
            Exception: For any underlying errors during the transcription
                       process (e.g., model loading issues, invalid audio format).
        """
        pass
