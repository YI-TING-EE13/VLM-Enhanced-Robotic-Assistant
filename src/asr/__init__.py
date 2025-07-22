# src/asr/__init__.py
"""
ASR module for providing speech-to-text services.

This package implements a factory pattern to create and provide access to
various Automatic Speech Recognition (ASR) services. The factory function,
`get_asr_model`, allows the application to dynamically select an ASR
implementation (e.g., Whisper, FunASR) at runtime.

This design decouples the application from the concrete implementation of the
ASR services, making it easy to add new ASR models or switch between existing
ones with minimal code changes.

To add a new ASR service:
1. Create a new class that inherits from `ASRInterface`.
2. Implement the `transcribe` method in your new class.
3. Add a new condition to the `get_asr_model` factory function to return
   an instance of your new class.
"""

from .asr_interface import ASRInterface
from .whisper_asr import WhisperASR
from .funasr_asr import FunASR

def get_asr_model(service_name: str = "whisper", **kwargs) -> ASRInterface:
    """
    Factory function to create and return an instance of an ASR service.

    This function centralizes the creation of ASR objects. It takes a service
    name and optional keyword arguments to instantiate the desired ASR service.
    This approach allows for flexible configuration and easy swapping of
    backend ASR technologies.

    Args:
        service_name (str): The identifier for the desired ASR service.
                          Supported values: "whisper", "funasr".
                          Defaults to "whisper".
        **kwargs: Additional keyword arguments that will be passed to the
                  constructor of the selected ASR service. For example, you
                  can pass `model_name="large"` for the WhisperASR service.

    Returns:
        ASRInterface: An object that conforms to the ASRInterface, ready for use.

    Raises:
        ValueError: If the specified `service_name` is not supported.
    """
    if service_name == "whisper":
        # Pass any additional kwargs to the WhisperASR constructor.
        # This allows for flexible model selection (e.g., "base", "large").
        return WhisperASR(**kwargs)
    elif service_name == "funasr":
        # The mock FunASR currently doesn't take args, but a real one might.
        return FunASR(**kwargs)
    else:
        raise ValueError(f"Unsupported ASR model: '{service_name}'")

# Expose the core components of the package for easy access.
# This allows other parts of the application to import them via `from src.asr import ...`
__all__ = ["ASRInterface", "get_asr_model"]
