# src/asr/funasr_asr.py
from .asr_interface import ASRInterface
import time
import os

class FunASR(ASRInterface):
    """
    A mock implementation of the ASRInterface for the FunASR model.

    This class serves as a placeholder for integrating FunASR from Alibaba's
    ModelScope. It simulates the behavior of a real ASR service by returning a
    predefined string after a short delay. This allows for testing the
    application's overall architecture and flow without requiring a full
    FunASR dependency and setup.

    To implement this for real, you would typically:
    1. Install the 'modelscope' and 'funasr' packages.
    2. Import the necessary components from 'modelscope.pipelines'.
    3. Load the actual model in the __init__ method.
    4. Replace the mock 'transcribe' logic with a call to the real model.
    """

    def __init__(self, model_name: str = "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"):
        """
        Initializes the mock FunASR service.

        In a real implementation, this is where the actual model would be
        downloaded from ModelScope and loaded into memory.

        Args:
            model_name (str): The model identifier from ModelScope that would
                              be used in a real implementation.
        """
        self.model_name = model_name
        print("FunASR: Service initialized (mock).")
        print(f"FunASR: Real implementation would use model: '{self.model_name}'")

    def transcribe(self, audio_file_path: str) -> str:
        """
        Simulates the transcription of an audio file.

        This mock method does not perform any real transcription. It validates
        the file path, simulates a processing delay, and returns a fixed
        string to the caller.

        Args:
            audio_file_path (str): The path to the audio file.

        Returns:
            str: A mock transcription result for testing purposes.
        """
        print(f"FunASR: Simulating transcription for {os.path.basename(audio_file_path)}...")
        
        # In a real implementation, you would check os.path.exists(audio_file_path)
        # but we skip it here as it's a mock.
        
        # Simulate a network or processing delay.
        time.sleep(1)
        
        mock_result = "這是來自 FunASR 的模擬辨識結果。"
        print("FunASR: Mock transcription complete.")
        return mock_result
