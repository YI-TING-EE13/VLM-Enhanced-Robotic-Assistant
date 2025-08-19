# src/vlm/__init__.py
"""
VLM module for providing multimodal (vision-language) services.

This package uses a factory pattern to instantiate and provide access to
various Vision-Language Model (VLM) services. The `get_vlm_service` function
acts as a single entry point, allowing the application to dynamically select
a VLM implementation (e.g., a cloud API like Gemini or a local model like Qwen-VL).

This design decouples the core application from the specific VLM technology,
making it easy to switch backends or add new models without major refactoring.

To add a new VLM service:
1. Create a new class that inherits from `VLMInterface`.
2. Implement the `get_decision` method in your new class.
3. Add a new condition to the `get_vlm_service` factory function to return
   an instance of your new class.
"""

from typing import Any
from .vlm_interface import VLMInterface
from .gemini_vlm import GeminiAPI_VLM
from .local_qwen_vlm import LocalQwenVL

def get_vlm_service(service_name: str = "gemini", **kwargs: Any) -> VLMInterface:
    """
    Factory function to create and return an instance of a VLM service.

    This function centralizes the creation of VLM objects. It takes a service
    name and optional keyword arguments to instantiate the desired VLM service.
    This allows for flexible configuration, such as passing a specific model
    name or path to the service's constructor.

    Args:
        service_name (str): The identifier for the desired VLM service.
                            Supported values: "gemini", "qwen_vl".
                            Defaults to "gemini".
        **kwargs: Additional keyword arguments to be passed to the constructor
                  of the selected VLM service (e.g., `model_name` for Gemini,
                  `model_path` for a local model).

    Returns:
        VLMInterface: An object that conforms to the VLMInterface.

    Raises:
        ValueError: If the specified `service_name` is not supported.
    """
    if service_name == "gemini":
        # For Gemini, kwargs can be used to specify a different model,
        # e.g., get_vlm_service("gemini", model_name="gemini-1.5-flash")
        return GeminiAPI_VLM(**kwargs)
    elif service_name == "qwen_vl":
        # For a local model, kwargs would be essential for providing the model path.
        # e.g., get_vlm_service("qwen_vl", model_path="/path/to/model")
        # Provide a default path for the mock if not specified.
        kwargs.setdefault("model_path", "mock/path/to/Qwen-VL-Chat")
        return LocalQwenVL(**kwargs)
    else:
        raise ValueError(f"Unsupported VLM service: '{service_name}'")

# Expose the core components for easy import from other modules.
__all__ = ["VLMInterface", "get_vlm_service"]
