# src/vlm/local_qwen_vlm.py
from .vlm_interface import VLMInterface
from PIL import Image
import time
import os

class LocalQwenVL(VLMInterface):
    """
    A mock implementation of the VLMInterface for a local Qwen-VL model.

    This class serves as a placeholder for a self-hosted Qwen-VL model. It
    simulates the model's behavior by returning a fixed JSON response after a
    brief delay, allowing the application to be tested end-to-end without
    the need for a powerful GPU and complex local model setup.

    To create a real implementation, you would need to:
    1. Install the necessary libraries (e.g., transformers, torch).
    2. Load the tokenizer and model from a local path in `__init__`.
    3. Implement the `get_decision` method to perform real inference, including
       image preprocessing, tokenization, and model generation.
    """

    def __init__(self, model_path: str, **kwargs):
        """
        Initializes the mock LocalQwenVL service.

        In a real scenario, this would involve loading a large model from the
        disk, which could be resource-intensive.

        Args:
            model_path (str): The path where the local model would be stored.
            **kwargs: Catches any additional arguments that might be passed.
        """
        self.model_path = model_path
        print("LocalQwenVL: Service initialized (mock).")
        print(f"LocalQwenVL: Real implementation would load model from: '{self.model_path}'")

    def get_decision(self, text: str, image: Image.Image) -> dict:
        """
        Simulates the decision-making process of a local VLM.

        This mock method prints the received inputs to simulate processing,
        waits for a short period to mimic inference time, and then returns a
        hardcoded, structured JSON response as a dictionary.

        Args:
            text (str): The user's textual command.
            image (Image.Image): A PIL Image object of the visual context.

        Returns:
            dict: A mock dictionary representing a clarification question.
        """
        import json
        print("LocalQwenVL: Simulating local VLM inference...")
        print(f"LocalQwenVL: Received prompt: '{text}'")
        print(f"LocalQwenVL: Received image of size: {image.size}")

        # Simulate the inference delay of a large local model.
        time.sleep(2)

        # Return a mock structured response for development and testing.
        mock_response = '{"action": "clarify", "question": "您是指哪一個物件？(This is a mock response from the local Qwen-VL model)"}'
        
        print("LocalQwenVL: Mock inference complete.")
        return json.loads(mock_response)
