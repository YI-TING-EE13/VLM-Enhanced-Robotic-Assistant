# src/vlm/gemini_vlm.py
from .vlm_interface import VLMInterface
import google.generativeai as genai
import os
from PIL import Image
from dotenv import load_dotenv

class GeminiAPI_VLM(VLMInterface):
    """
    Implements the VLMInterface using the Google Gemini Pro Vision API.

    This class handles the communication with Google's cloud-based VLM service.
    It is responsible for securely authenticating, sending multimodal (text and
    image) prompts, and returning the model's response. The quality of the
    output is highly dependent on the prompt engineering used by the caller.
    """

    def __init__(self, model_name: str = 'gemini-2.5-flash') -> None:
        """
        Initializes and configures the Gemini VLM service client.

        This constructor performs the following critical steps:
        1. Loads environment variables from a `.env` file.
        2. Retrieves the `GEMINI_API_KEY`.
        3. Validates the key's presence.
        4. Configures the `google.generativeai` client.
        5. Instantiates the specified generative model.

        Args:
            model_name (str): The identifier for the Gemini model to be used.
                              Defaults to 'gemini-2.5-flash', a powerful
                              and efficient multimodal model.

        Raises:
            ValueError: If the `GEMINI_API_KEY` is missing, empty, or still
                        set to its placeholder value in the `.env` file.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError(
                "GEMINI_API_KEY not found or not set. Please ensure a .env file "
                "exists in the project root with your valid API key."
            )

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
            print(f"GeminiVLM: Service initialized with model '{model_name}'.")
        except Exception as e:
            print(f"GeminiVLM: Failed to initialize Google GenAI. Error: {e}")
            raise

    def get_decision(self, text: str, image: Image.Image) -> str:
        """
        Sends a multimodal prompt to the Gemini API and returns the raw response.

        This method constructs a request containing both the user's text query
        and the visual context from an image. It then calls the Gemini API
        and returns the generated text.

        Args:
            text (str): The textual part of the prompt (e.g., user command).
            image (Image.Image): A PIL Image object providing the visual context.

        Returns:
            str: The raw text response from the Gemini API.

        Raises:
            Exception: Propagates any exceptions that occur during the API call,
                       which could be due to network issues, authentication errors,
                       or invalid input.
        """
        print("GeminiVLM: Sending request to API...")
        try:
            # The generate_content method accepts a list of mixed-modality parts.
            response = self.model.generate_content([text, image])
            print("GeminiVLM: Received response from API.")
            
            # Clean the response text
            cleaned_response = response.text.strip()
            if cleaned_response.startswith('```') and cleaned_response.endswith('```'):
                # Find the first newline and the last newline to extract content
                first_newline = cleaned_response.find('\n')
                last_newline = cleaned_response.rfind('\n')
                if first_newline != -1 and last_newline != -1 and last_newline > first_newline:
                    cleaned_response = cleaned_response[first_newline + 1:last_newline].strip()
            
            return cleaned_response
        except Exception as e:
            print(f"GeminiVLM: An error occurred during the API call: {e}")
            # Re-raising is important for the caller to handle API failures.
            raise
