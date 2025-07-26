# main.py
"""
Main entry point for the VLM-Enhanced Robot Assistant application.

This script orchestrates the entire workflow, from initializing services
(ASR, VLM, TTS, Camera, GUI) to managing the main processing loop. It is
responsible for capturing user input (audio and video), processing it,
and providing feedback.
"""

import os
import json
import time
from PIL import Image
from typing import Tuple

# Import factory functions and interfaces from the source directory
from src.asr import get_asr_model, ASRInterface
from src.vlm import get_vlm_service, VLMInterface
from src.tts import speak
from src.audio_recorder import AudioRecorder
from src.camera import get_camera, CameraInterface
from src.ui.gui_manager import GUIManager

class AppConfig:
    """
    Centralized configuration for the application.

    This class holds all configurable parameters, making it easy to manage
    and modify the application's behavior without changing the core logic.
    """
    # --- Service Selection ---
    ASR_SERVICE: str = "whisper"
    VLM_SERVICE: str = "gemini"

    # --- Model & Path Configuration ---
    WHISPER_MODEL: str = "base"
    RECORDING_MODE: str = "microphone"
    TEST_AUDIO_FILE: str = "test_data/test_audio.wav"
    CAMERA_TYPE: str = "realsense"

    # --- VLM Prompt Template ---
    VLM_PROMPT_TEMPLATE: str = """
# Role
You are a high-precision, safety-first intelligent assembly line robot arm assistant. You observe the assembly line through a camera. Make decisions based on the real-time image below and the operator's instructions.

# Operator's Instruction
"{user_instruction_text}"

# Your Task
1.  **Visual Analysis**: Carefully observe all objects in the image, especially aluminum profiles of different lengths and hole spacings, screws, tools, and material racks.
2.  **Localization**: Link words from the operator's instruction (e.g., "that long one," "the one on the left," "that one") to a specific object in the image.
3.  **System Control**: Check for system shutdown commands (e.g., "shutdown system," "exit program," "stop running," "power off").
4.  **Ambiguity Detection**:
    -   **Referential Ambiguity**: Can the description in the instruction uniquely map to one object in the image? If it maps to multiple, it's ambiguous.
    -   **Intent/Parameter Ambiguity**: Is the command clear and directly executable, or does it need more information? For example, "I want to build a display rack" is a high-level intent that needs to be broken down.
5.  **Decision and Output**:
    -   **If it's a system shutdown command**: Generate the shutdown confirmation format.
    -   **If the command is clear and unambiguous**: Generate a structured JSON format command. In the command, use the object's visual features or relative position as its description in `target_description`.
    -   **If the command is ambiguous**: Generate a JSON format for a clarification question.

# Output Format (Must strictly follow one of the JSON formats below)
## System Shutdown Format:
{{"action": "shutdown", "confirmation_needed": true, "message": "Are you sure you want to shut down the system?"}}
## Clear Command Format:
{{"action": "pick_up", "target_description": "the 60cm long aluminum profile on top of rack A"}}
## Clarification Question Format:
{{"action": "clarify", "question": "Do you mean the long part in front of me, the one next to the green box?"}}

# Respond in Traditional Chinese
# Begin Analysis:
"""

def initialize_services(config: AppConfig) -> Tuple[ASRInterface, VLMInterface, CameraInterface]:
    """
    Initializes and returns the required services based on the configuration.

    Args:
        config (AppConfig): The application configuration object.

    Returns:
        A tuple containing the initialized ASR, VLM, and Camera service instances.

    Raises:
        SystemExit: If any service fails to initialize.
    """
    print("--- Initializing Services ---")
    try:
        asr_service = get_asr_model(config.ASR_SERVICE, model_name=config.WHISPER_MODEL)
        vlm_service = get_vlm_service(config.VLM_SERVICE, model_name="gemini-2.5-flash")
        camera_service = get_camera(config.CAMERA_TYPE)
        print("--- Services Initialized Successfully ---\n")
        return asr_service, vlm_service, camera_service
    except Exception as e:
        print(f"\n--- FATAL ERROR: Service Initialization Failed ---")
        print(f"Error: {e}")
        print("Please check your configuration, dependencies, and API keys.")
        raise SystemExit(1)

def handle_shutdown_confirmation() -> bool:
    """
    Handles the user confirmation process for shutting down the system.

    It records a short audio clip, transcribes it, and checks for affirmative
    or negative responses.

    Returns:
        bool: Returns `False` to confirm shutdown, or `True` to cancel.
    """
    try:
        print("\n🔴 System Shutdown Confirmation Mode")
        print("Please say 'Yes' or 'Confirm' to shut down, or 'No' / 'Cancel' to continue.")
        
        recorder = AudioRecorder()
        confirmation_audio = recorder.record_audio(duration=3.0, countdown=True)
        
        # Use a dedicated, lightweight ASR for this simple confirmation task
        asr_service = get_asr_model("whisper", model_name="base")
        confirmation_text = asr_service.transcribe(confirmation_audio).strip().lower()
        print(f"Confirmation response: '{confirmation_text}'")
        
        positive_words = ["是", "對", "確定", "關閉", "好", "yes", "confirm"]
        negative_words = ["否", "不", "取消", "繼續", "no", "cancel"]
        
        if any(word in confirmation_text for word in positive_words):
            speak("Affirmative. Shutting down the system. Goodbye!")
            print("👋 User confirmed shutdown.")
            return False  # Proceed with shutdown
        elif any(word in confirmation_text for word in negative_words):
            speak("Negative. Operation will continue.")
            print("✅ User canceled shutdown.")
            return True  # Cancel shutdown
        else:
            speak("I didn't understand your response. The system will continue to run.")
            print("❓ Unrecognized confirmation. Defaulting to continue operation.")
            return True  # Cancel shutdown by default
            
    except Exception as e:
        print(f"An error occurred during shutdown confirmation: {e}")
        speak("There was a problem during the confirmation process. The system will continue to run.")
        return True
    finally:
        # Clean up the temporary confirmation audio file
        if 'confirmation_audio' in locals() and os.path.exists(confirmation_audio):
            os.remove(confirmation_audio)

def get_audio_input(config: AppConfig) -> str:
    """
    Captures audio input based on the configured mode and returns the file path.

    Args:
        config (AppConfig): The application configuration.

    Returns:
        str: The file path to the captured or specified audio file.
    """
    if config.RECORDING_MODE == "microphone":
        print("--- Using microphone recording mode ---")
        recorder = AudioRecorder()
        try:
            audio_path = recorder.record_audio(duration=5.0)
            print(f"Recording complete, saved to: {os.path.basename(audio_path)}")
            return audio_path
        except Exception as e:
            print(f"Microphone recording failed: {e}. Falling back to file mode...")
            return config.TEST_AUDIO_FILE
    else:
        print("-- Using audio file mode ---")
        return config.TEST_AUDIO_FILE

def process_interaction(
    asr: ASRInterface, vlm: VLMInterface, gui: GUIManager, 
    audio_path: str, image: Image.Image, prompt_template: str
) -> bool:
    """
    Executes the core logic for a single user interaction.

    This function orchestrates the process of transcribing audio, sending the
    command and image to the VLM, and acting on the VLM's decision.

    Args:
        asr (ASRInterface): The initialized ASR service.
        vlm (VLMInterface): The initialized VLM service.
        gui (GUIManager): The GUI manager instance.
        audio_path (str): Path to the user's audio command.
        image (Image.Image): The visual context for the command.
        prompt_template (str): The master prompt for the VLM.

    Returns:
        bool: `True` to continue running, `False` to shut down the system.
    """
    # 1. Transcribe Audio to Text
    print("\n--- Step 1: Transcribing Audio ---")
    try:
        instruction_text = asr.transcribe(audio_path)
        print(f"ASR Output: '{instruction_text}'")
        if not instruction_text.strip():
            speak("I didn't hear anything. Please try again.")
            return True  # Continue running
    except Exception as e:
        print(f"ASR Error: {e}")
        speak("I encountered an error trying to understand what you said.")
        return True

    # 2. Update GUI with captured frame and get VLM decision
    print("\n--- Step 2: Getting Decision from VLM ---")
    gui.update_image(image, "captured")
    final_prompt = prompt_template.format(user_instruction_text=instruction_text)
    try:
        decision = vlm.get_decision(final_prompt, image)
        print(f"VLM Raw Response: {decision}")
    except Exception as e:
        print(f"VLM Error: {e}")
        speak("I couldn't connect to the vision-language model. Please check the connection or API key.")
        return True

    # 3. Process VLM Response and Provide Feedback
    print("\n--- Step 3: Processing Response and Acting ---")
    try:
        action = decision.get("action")
        if action == "shutdown":
            message = decision.get("message", "Are you sure you want to shut down?")
            print(f"Action: Shutdown Request -> Asking: '{message}'")
            speak(message)
            return handle_shutdown_confirmation()
        elif action == "clarify":
            question = decision.get("question", "I need more information.")
            print(f"Action: Clarify -> Asking: '{question}'")
            speak(question)
        elif action == "pick_up":
            target = decision.get("target_description", "the specified object")
            confirmation_text = f"Okay, I will now pick up {target}."
            print(f"Action: Execute -> Task: '{confirmation_text}'")
            speak(confirmation_text)
        else:
            print(f"Warning: Received unknown action '{action}' from VLM.")
            speak("I've received a plan, but I'm not sure how to execute it.")
    except Exception as e:
        print(f"Error during action processing: {e}")
        speak("I encountered an error while trying to carry out the command.")
    
    return True

def main():
    """
    Main function to run the VLM-enhanced robot assistant workflow.
    Initializes all services and enters a continuous loop to process interactions.
    """
    print("=============================================")
    print("  VLM-Enhanced Robot Assistant Initializing  ")
    print("=============================================")
    
    gui = GUIManager()
    print("Waiting for GUI to initialize...")
    while not gui.is_running:
        time.sleep(0.1)

    config = AppConfig()
    asr_service, vlm_service, camera_service = initialize_services(config)
    
    print("🤖 System is active! Say 'Shutdown System' to exit safely.")
    print("=============================================\n")
    
    session_count = 0
    try:
        while gui.is_running:
            session_count += 1
            audio_path = None
            
            try:
                print(f"\n🔄 === Interaction Cycle #{session_count} ===")
                
                # Continuously update the live feed while waiting for a command
                print("🎥 Displaying live feed. Please issue a voice command.")
                live_frame = camera_service.get_frame()
                gui.update_image(live_frame, "live")
                
                # Capture the final image to be processed right before audio recording
                image_to_process = camera_service.get_frame()
                gui.update_image(image_to_process, "live") # Also update live view
                
                audio_path = get_audio_input(config)
                
                if not os.path.exists(audio_path):
                    raise FileNotFoundError(f"Audio file not found: {audio_path}")

                # Process the interaction and decide whether to continue
                if not process_interaction(
                    asr_service, vlm_service, gui, 
                    audio_path, image_to_process, config.VLM_PROMPT_TEMPLATE
                ):
                    print("\n🛑 System shutdown initiated...")
                    break
                    
                print(f"✅ Interaction #{session_count} complete.\n")
                
            except KeyboardInterrupt:
                raise # Re-raise to be caught by the outer try/except block
            except FileNotFoundError as e:
                print(f"\n--- WARNING: {e} ---")
                speak("I couldn't find a necessary input file. Please check the configuration.")
            except Exception as e:
                print(f"\n--- An unexpected error occurred in the main loop: {e} ---")
                speak("An error occurred, but the system will continue to run.")
            finally:
                # Clean up temporary recording file if it exists
                if audio_path and config.RECORDING_MODE == "microphone" and os.path.exists(audio_path):
                    try:
                        os.remove(audio_path)
                    except OSError as e:
                        print(f"Error removing temp audio file: {e}")

    except KeyboardInterrupt:
        print("\n\n⚠️ Ctrl+C detected. Initiating safe shutdown...")
        speak("Interrupt signal detected. Shutting down.")
        
    finally:
        print("Releasing resources...")
        if 'camera_service' in locals():
            camera_service.release()
        if 'gui' in locals() and gui.is_running:
            gui.close()

        print("\n=============================================")
        print("           System Shut Down Safely           ")
        print(f"           Total interactions: {session_count}           ")
        print("=============================================")

if __name__ == "__main__":
    main()