# src/tts/__init__.py
"""
Text-to-Speech (TTS) module for providing voice feedback.

This package encapsulates the functionality for synthesizing speech from text.
It is designed to be a simple, drop-in solution for adding voice capabilities
to the application.

The primary component is the `speak` function, which is exposed for direct use.
"""

from .tts_module import speak

# Expose the `speak` function as the public API of the `tts` package.
# This allows other parts of the application to use it via `from src.tts import speak`.
__all__ = ["speak"]
