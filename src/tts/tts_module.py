# src/tts/tts_module.py
import asyncio
import edge_tts
from playsound import playsound
import os
import tempfile

# Define the default voice for Text-to-Speech.
# 'zh-TW-HsiaoChenNeural' is a high-quality female voice for Traditional Chinese (Taiwan).
DEFAULT_VOICE = "zh-TW-HsiaoChenNeural"

async def _generate_and_play(text: str, voice: str) -> None:
    """
    An asynchronous helper function that generates speech and plays it.

    This function creates a temporary file to store the generated speech,
    plays it using the `playsound` library, and ensures the temporary file
    is cleaned up afterward.

    Args:
        text (str): The text to be synthesized into speech.
        voice (str): The voice to use for the synthesis.
    """
    output_file: Optional[str] = None
    try:
        # Create a temporary file to store the MP3 output.
        # Using tempfile is safer and cleaner than hardcoding a filename.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            output_file = fp.name
        
        print(f"TTS: Generating speech for: '{text}'")
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)

        if os.path.exists(output_file):
            print(f"TTS: Playing audio from {os.path.basename(output_file)}...")
            # The `playsound` library is simple but can be blocking.
            # It's suitable for this application where we wait for speech to finish.
            playsound(output_file)
            print("TTS: Audio playback finished.")
        else:
            print("TTS: Error - Could not find the generated audio file.")

    except Exception as e:
        # Catching a broad exception is acceptable here as `edge-tts` or `playsound`
        # can have various issues (network, audio drivers, etc.).
        print(f"TTS: An error occurred during speech generation or playback: {e}")
    finally:
        # Ensure the temporary file is always deleted.
        if output_file and os.path.exists(output_file):
            os.remove(output_file)
            # print(f"TTS: Temporary audio file '{os.path.basename(output_file)}' removed.")

def speak(text: str, voice: str = DEFAULT_VOICE) -> None:
    """
    Converts text to speech and plays it aloud using Microsoft Edge's TTS service.

    This function provides a simple, synchronous interface for the asynchronous
    TTS generation and playback process. It handles the creation and management
    of the asyncio event loop.

    Args:
        text (str): The text to be spoken.
        voice (str): The voice to use. Defaults to `DEFAULT_VOICE`.
    """
    if not text:
        print("TTS: Received empty text, nothing to speak.")
        return
        
    try:
        # `asyncio.run` is the modern way to run a top-level async function.
        asyncio.run(_generate_and_play(text, voice))
    except Exception as e:
        print(f"TTS: An error occurred in the asyncio event loop: {e}")

if __name__ == '__main__':
    """
    Provides a simple demonstration of the `speak` function when the module
    is executed directly.
    """
    print("--- Running TTS Module Demonstration ---")
    speak("你好，這是一個語音合成功能的測試。")
    speak("This is a test of the speech synthesis function in English.")
    print("--- Demonstration Finished ---")
