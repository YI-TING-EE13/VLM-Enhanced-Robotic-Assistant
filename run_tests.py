# run_tests.py
import os
from PIL import Image
import sys

# Add src to the Python path to allow direct imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from asr import get_asr_model, ASRInterface
from vlm import get_vlm_service, VLMInterface
from tts import speak

def test_asr_module():
    """
    Tests the ASR module functionality.
    It uses a mock ASR model to avoid dependency on actual audio files.
    """
    print("\n--- Testing ASR Module ---")
    try:
        # We use the 'funasr' mock model for this test to avoid real transcription
        asr_service = get_asr_model(model_name="funasr")
        assert isinstance(asr_service, ASRInterface)
        
        # The mock FunASR doesn't need a real file, just a path
        mock_audio_path = "dummy/path/to/audio.wav"
        transcription = asr_service.transcribe(mock_audio_path)
        
        assert isinstance(transcription, str)
        assert "FunASR" in transcription
        
        print("ASR Module Test: PASSED")
        return True
    except Exception as e:
        print(f"ASR Module Test: FAILED - {e}")
        return False

def test_vlm_module():
    """
    Tests the VLM module functionality.
    It uses a mock VLM model to avoid API calls and image dependencies.
    """
    print("\n--- Testing VLM Module ---")
    try:
        # We use the 'qwen_vl' mock model for this test
        vlm_service = get_vlm_service(service_name="qwen_vl")
        assert isinstance(vlm_service, VLMInterface)
        
        # Prepare dummy inputs
        dummy_prompt = "This is a test prompt."
        dummy_image = Image.new('RGB', (100, 100), color='red')
        
        decision = vlm_service.get_decision(dummy_prompt, dummy_image)
        
        assert isinstance(decision, str)
        assert "Qwen-VL" in decision
        
        print("VLM Module Test: PASSED")
        return True
    except Exception as e:
        print(f"VLM Module Test: FAILED - {e}")
        return False

def test_tts_module():
    """
    Tests the TTS module functionality.
    This test will generate and play a short audio clip.
    """
    print("\n--- Testing TTS Module ---")
    try:
        # This will attempt to generate and play a real audio file
        speak("This is a test of the text-to-speech module.")
        print("TTS Module Test: PASSED (Check for audio output)")
        return True
    except Exception as e:
        print(f"TTS Module Test: FAILED - {e}")
        print("Note: TTS tests can fail due to audio device issues or internet connection problems.")
        return False

def run_all_tests():
    """
    Runs all defined tests and reports a summary.
    """
    print("=============================")
    print("  Running Project Test Suite  ")
    print("=============================")
    
    results = {
        "ASR": test_asr_module(),
        "VLM": test_vlm_module(),
        "TTS": test_tts_module(),
    }
    
    print("\n--- Test Summary ---")
    all_passed = True
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        print(f"- {test_name} Test: {status}")
        if not result:
            all_passed = False
            
    print("=============================")
    if all_passed:
        print("All tests passed successfully!")
    else:
        print("Some tests failed. Please review the logs above.")
    print("=============================")

if __name__ == "__main__":
    run_all_tests()
