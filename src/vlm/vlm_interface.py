# src/vlm/vlm_interface.py
from abc import ABC, abstractmethod
from PIL import Image

class VLMInterface(ABC):
    """
    Defines the interface for Vision-Language Model (VLM) services.

    This abstract base class is the cornerstone of the system's multimodal
    understanding capabilities. It establishes a contract for any service
    that can interpret combined text and image inputs to make decisions.
    By ensuring all VLM services (e.g., cloud-based APIs like Gemini, or
    local models like Qwen-VL) adhere to this interface, the system can
    treat them as interchangeable components.
    """

    @abstractmethod
    def get_decision(self, text_prompt: str, image: Image.Image) -> str:
        """
        Processes a text prompt and an image to generate a decision.

        The core function of a VLM service is to ground the textual prompt
        in the visual context of the image and produce a structured output,
        such as a command for a robot or a clarification question for a user.

        Args:
            text_prompt (str): The textual instruction or query from the user.
            image (Image.Image): A PIL Image object representing the current
                                 visual scene (e.g., a live camera frame).

        Returns:
            str: A string containing the model's response, which is expected
                 to be in a structured format (e.g., JSON) for reliable parsing.

        Raises:
            Exception: For any underlying errors during the decision-making
                       process, such as API connection failures or model errors.
        """
        pass
