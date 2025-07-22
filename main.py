# main.py
"""
Main entry point for the VLM-Enhanced Robot Assistant application.

This script orchestrates the entire workflow, from capturing user input to
executing commands. It initializes the necessary services (ASR, VLM, TTS),
manages the application's configuration, and runs the main processing loop.
"""

import os
import json
from PIL import Image
from typing import Dict, Any

# Import factory functions and interfaces from the source directory
from src.asr import get_asr_model, ASRInterface
from src.vlm import get_vlm_service, VLMInterface
from src.tts import speak
from src.audio_recorder import AudioRecorder

class AppConfig:
    """
    Centralized configuration for the application.

    This class holds all the configurable parameters, making it easy to
    manage and modify the application's behavior without changing the core logic.
    """
    # --- Service Selection ---
    # Switch between 'whisper' (real) and 'funasr' (mock)
    ASR_SERVICE: str = "whisper"
    # Switch between 'gemini' (real) and 'qwen_vl' (mock)
    VLM_SERVICE: str = "gemini"

    # --- Model & Path Configuration ---
    # Specific model name for Whisper ASR
    WHISPER_MODEL: str = "base"
    # Recording mode: 'file' for test files, 'microphone' for live recording
    RECORDING_MODE: str = "microphone"  # Change to "file" to use test files
    # Path to the test audio file (used when RECORDING_MODE is 'file')
    TEST_AUDIO_FILE: str = "test_data/test_audio.wav"
    # Path to the test image file (replace with a real camera capture function)
    TEST_IMAGE_FILE: str = "test_data/test_image_01.jpeg"

    # --- VLM Prompt Template ---
    # This is the master prompt that defines the VLM's persona, tasks, and
    # output format. Its quality is critical to the system's performance.
    VLM_PROMPT_TEMPLATE: str = """
# 角色
您是一位高精度、安全優先的智慧生產線機械手臂助理。您透過攝影機觀察生產線。請根據下方即時影像和操作員的指令做出決策。

# 操作員指令
"{user_instruction_text}"

# 您的任務
1.  **視覺分析**：仔細觀察影像中的所有物件，特別是不同長度和孔距的鋁型材、螺絲、工具和材料架。
2.  **定位**：將操作員指令中的詞語（例如「那個長的」、「左邊那個」、「那一個」）與影像中的特定物件連結。
3.  **系統控制**：檢查是否為系統關閉指令（例如「關閉系統」、「結束程式」、「停止運行」、「關機」等）。
4.  **歧義偵測**：
    -   **指向歧義**：指令中的描述能否唯一對應影像中的一個物件？如果對應多個，則為歧義。
    -   **意圖/參數歧義**：指令是否清楚且可直接執行？還是需要更多資訊？例如「我想要組裝一個展示架」是高層級意圖，需要分解。
5.  **決策與輸出**：
    -   **如果是系統關閉指令**：生成關閉確認格式。
    -   **如果指令清楚且無歧義**：生成結構化的 JSON 格式指令。在指令中，使用物件的視覺特徵或相對位置作為描述，例如 `target_description`。
    -   **如果指令有歧義**：生成澄清問題的 JSON 格式。

# 輸出格式（必須嚴格遵循以下 JSON 格式之一）
## 系統關閉格式：
{{"action": "shutdown", "confirmation_needed": true, "message": "您確定要關閉系統嗎？"}}
## 清楚指令格式：
{{"action": "pick_up", "target_description": "位於 A 架頂部約 60 公分長的鋁型材"}}
## 澄清問題格式：
{{"action": "clarify", "question": "您是指我面前那個長的零件，綠色盒子旁邊的那個嗎？"}}

# 請用繁體中文回應
# 開始分析：
"""

def initialize_services(config: AppConfig) -> tuple[ASRInterface, VLMInterface]:
    """
    Initializes and returns the required services based on the configuration.

    Args:
        config (AppConfig): The application configuration object.

    Returns:
        A tuple containing the initialized ASR and VLM service instances.

    Raises:
        SystemExit: If any service fails to initialize.
    """
    print("--- Initializing Services ---")
    try:
        asr_service = get_asr_model(config.ASR_SERVICE, model_name=config.WHISPER_MODEL)
        # Use the latest Gemini 2.5 Flash model for better performance
        vlm_service = get_vlm_service(config.VLM_SERVICE, model_name="gemini-2.5-flash")
        print("--- Services Initialized Successfully ---\n")
        return asr_service, vlm_service
    except Exception as e:
        print(f"\n--- FATAL ERROR: Service Initialization Failed ---")
        print(f"Error: {e}")
        print("Please check your configuration, dependencies, and API keys.")
        raise SystemExit(1)

def handle_shutdown_confirmation() -> bool:
    """
    Handles the shutdown confirmation process by recording user's response.
    
    Returns:
        bool: False to shutdown, True to continue running
    """
    try:
        print("\n🔴 系統關閉確認模式")
        print("請說「是」或「確定」來關閉系統，或說「否」、「取消」來繼續運行")
        
        # Record user's confirmation
        recorder = AudioRecorder()
        confirmation_audio = recorder.record_audio(duration=3.0, countdown=True)
        
        # Use a simple ASR to get the confirmation
        from src.asr import get_asr_model
        asr_service = get_asr_model("whisper", model_name="base")
        
        confirmation_text = asr_service.transcribe(confirmation_audio).strip().lower()
        print(f"確認回應: '{confirmation_text}'")
        
        # Check for positive confirmation
        positive_words = ["是", "對", "確定", "關閉", "好", "yes", "確認"]
        negative_words = ["否", "不", "取消", "繼續", "no", "不要"]
        
        if any(word in confirmation_text for word in positive_words):
            speak("好的，正在關閉系統。再見！")
            print("👋 用戶確認關閉系統")
            return False  # Shutdown
        elif any(word in confirmation_text for word in negative_words):
            speak("好的，繼續運行系統。")
            print("✅ 用戶取消關閉，繼續運行")
            return True  # Continue
        else:
            speak("我沒有聽清楚您的回應，系統將繼續運行。")
            print("❓ 無法識別確認回應，預設繼續運行")
            return True  # Continue by default
            
    except Exception as e:
        print(f"關閉確認過程出錯: {e}")
        speak("確認過程出現問題，系統將繼續運行。")
        return True  # Continue on error
    finally:
        # Clean up confirmation audio file
        try:
            if 'confirmation_audio' in locals():
                recorder.cleanup_temp_file(confirmation_audio)
        except:
            pass

def get_user_inputs(config: AppConfig) -> tuple[str, Image.Image]:
    """
    Gets user inputs either from files or by recording from microphone.

    Args:
        config (AppConfig): Application configuration containing recording mode and file paths.

    Returns:
        A tuple containing the audio file path and the loaded PIL Image object.
    """
    # Always load the image from file
    image_path = config.TEST_IMAGE_FILE
    if not os.path.exists(image_path):
        print(f"ERROR: Image file not found at {image_path}")
        raise FileNotFoundError
    
    image = Image.open(image_path)
    print(f"Loaded image: {os.path.basename(image_path)} (Size: {image.size})")
    
    # Handle audio input based on recording mode
    if config.RECORDING_MODE == "microphone":
        print("--- 使用麥克風錄音模式 ---")
        recorder = AudioRecorder()
        
        # Optional: List available audio devices for debugging
        # recorder.list_audio_devices()
        
        try:
            # Record audio from microphone
            audio_path = recorder.record_audio(duration=5.0)
            print(f"錄音完成，儲存至: {os.path.basename(audio_path)}")
            return audio_path, image
        except Exception as e:
            print(f"麥克風錄音失敗: {e}")
            print("切換至檔案模式...")
            # Fall back to file mode if microphone fails
            audio_path = config.TEST_AUDIO_FILE
    else:
        print("--- 使用音檔模式 ---")
        audio_path = config.TEST_AUDIO_FILE
    
    # File mode validation
    if not os.path.exists(audio_path):
        print(f"ERROR: Audio file not found at {audio_path}")
        raise FileNotFoundError
    
    print(f"Loaded audio: {os.path.basename(audio_path)}")
    return audio_path, image

def process_command(asr: ASRInterface, vlm: VLMInterface, audio_path: str, image: Image.Image, prompt_template: str) -> bool:
    """
    Executes the core logic: transcribe, decide, and act.

    Args:
        asr (ASRInterface): The initialized ASR service.
        vlm (VLMInterface): The initialized VLM service.
        audio_path (str): Path to the user's audio command.
        image (Image.Image): The visual context for the command.
        prompt_template (str): The master prompt for the VLM.
        
    Returns:
        bool: True to continue running, False to shutdown the system.
    """
    # 1. Transcribe Audio to Text
    print("\n--- Step 1: Transcribing Audio ---")
    try:
        instruction_text = asr.transcribe(audio_path)
        print(f"ASR Output: '{instruction_text}'")
        if not instruction_text.strip():
            speak("我沒有聽清楚，請您再說一次好嗎？")
            return True  # Continue running
    except FileNotFoundError as e:
        print(f"ASR Error: {e}. This often means 'ffmpeg' is not installed or not in the system's PATH.")
        speak("我的音頻處理工具出現問題，請檢查系統設定。")
        return True  # Continue running
    except Exception as e:
        print(f"ASR Error: An unexpected error occurred: {e}")
        speak("我在理解您的話時遇到了錯誤。")
        return True  # Continue running

    # 2. Get Decision from VLM
    print("\n--- Step 2: Getting Decision from VLM ---")
    final_prompt = prompt_template.format(user_instruction_text=instruction_text)
    try:
        vlm_response_str = vlm.get_decision(final_prompt, image)
        print(f"VLM Raw Response: {vlm_response_str}")
    except Exception as e:
        print(f"VLM Error: {e}")
        speak("我無法連接到視覺推理中心，請檢查連線或 API 金鑰。")
        return True  # Continue running

    # 3. Process VLM Response and Provide Feedback
    print("\n--- Step 3: Processing Response and Acting ---")
    try:
        # Clean up the response by removing markdown code blocks if present
        cleaned_response = vlm_response_str.strip()
        
        # Remove markdown code blocks
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        
        # Extract JSON from response that might have explanatory text
        import re
        json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
        if json_match:
            cleaned_response = json_match.group(0)
        
        cleaned_response = cleaned_response.strip()
        
        decision = json.loads(cleaned_response)
        action = decision.get("action")

        if action == "shutdown":
            # Handle system shutdown request
            confirmation_message = decision.get("message", "您確定要關閉系統嗎？")
            print(f"Action: Shutdown Request -> Asking: '{confirmation_message}'")
            speak(confirmation_message)
            
            # Get confirmation from user
            return handle_shutdown_confirmation()
            
        elif action == "clarify":
            question = decision.get("question", "我有個問題，但不確定是什麼。")
            print(f"Action: Clarify -> Asking: '{question}'")
            speak(question)
            return True  # Continue running
            
        elif action == "pick_up":
            target = decision.get("target_description", "指定的物件")
            confirmation_text = f"好的，我現在會拿起{target}。"
            print(f"Action: Execute -> Task: '{confirmation_text}'")
            speak(confirmation_text)
            # In a real system, this is where you would call the robot control module.
            return True  # Continue running
            
        else:
            print(f"Warning: Received unknown action '{action}' from VLM.")
            speak("我收到了一個計劃，但不確定如何執行。")
            return True  # Continue running
    except json.JSONDecodeError:
        print("VLM Error: Response was not valid JSON. Speaking raw response.")
        speak("我的思考過程出現格式錯誤，以下是我的想法：")
        speak(vlm_response_str)
        return True  # Continue running
    except Exception as e:
        print(f"Error during action processing: {e}")
        speak("我在執行指令時遇到了錯誤。")
        return True  # Continue running

def main():
    """
    Main function to run the VLM-enhanced robot assistant workflow.
    The system runs continuously until the user requests shutdown.
    """
    print("=============================================")
    print("  VLM-Enhanced Robot Assistant Initializing  ")
    print("=============================================")
    
    config = AppConfig()
    asr_service, vlm_service = initialize_services(config)
    
    print("🤖 系統已啟動！說「關閉系統」來安全退出")
    print("=============================================\n")
    
    # Main processing loop
    session_count = 0
    while True:
        session_count += 1
        audio_path = None
        
        try:
            print(f"\n🔄 === 第 {session_count} 次互動 ===")
            audio_file, image_file = get_user_inputs(config)
            audio_path = audio_file
            
            # Process command and check if system should continue
            should_continue = process_command(asr_service, vlm_service, audio_file, image_file, config.VLM_PROMPT_TEMPLATE)
            
            if not should_continue:
                print("\n🛑 系統正在關閉...")
                break
                
            print(f"✅ 第 {session_count} 次互動完成\n")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 檢測到 Ctrl+C，正在安全關閉系統...")
            speak("檢測到中斷信號，正在關閉系統。")
            break
            
        except FileNotFoundError:
            print("\n--- 警告: 找不到必要的輸入檔案 ---")
            speak("我找不到必要的輸入檔案，請檢查設定。")
            print("系統將繼續等待下一個指令...\n")
            
        except Exception as e:
            print(f"\n--- 發生未處理的異常 ---")
            print(f"錯誤: {e}")
            speak("發生了錯誤，但系統將繼續運行。")
            print("系統將繼續等待下一個指令...\n")
            
        finally:
            # Clean up temporary recording file if it was created
            if audio_path and config.RECORDING_MODE == "microphone":
                try:
                    recorder = AudioRecorder()
                    recorder.cleanup_temp_file(audio_path)
                except:
                    pass  # Ignore cleanup errors

    print("\n=============================================")
    print("           系統已安全關閉           ")
    print(f"           總共處理了 {session_count} 次互動           ")
    print("=============================================")

if __name__ == "__main__":
    main()
