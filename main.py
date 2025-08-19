# main.py
import os
from PIL import Image

# Ensure the src directory is in the Python path
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from vlm import get_vlm_service
from camera import get_camera_service
from task_decomposer import TaskDecomposer

def main() -> None:
    """
    Main function to run the VLM-Enhanced Robotic Assistant.
    """
    print("--- VLM-Enhanced Robotic Assistant ---")
    
    # 1. Initialize services
    try:
        # Initialize the VLM service (e.g., "gemini" or "qwen_vl")
        vlm_service = get_vlm_service("gemini")
        
        # Initialize the Task Decomposer with the VLM service
        decomposer = TaskDecomposer(vlm_service)

        # Initialize the camera service
        try:
            camera = get_camera_service("realsense")
            print("RealSense camera initialized successfully.")
        except Exception as e:
            print(f"Could not initialize RealSense camera: {e}")
            print("Falling back to a placeholder image for testing.")
            camera = None

        print("\nAll services initialized successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to initialize services: {e}")
        print("Please check your configuration (e.g., .env file) and connections.")
        return

    # 2. Main application loop
    try:
        # Get user's task command
        user_task = input("What task would you like me to perform? ")
        if not user_task:
            print("No task provided. Exiting.")
            return

        # Get the current visual scene
        if camera:
            print("Capturing image from the camera...")
            current_image = camera.get_frame()
        else:
            print("Using a placeholder image for testing.")
            # Create a placeholder image
            current_image = Image.new('RGB', (640, 480), color = 'grey')
            # Optional: save the image to see what is being sent
            # current_image.save("placeholder_image.png")

        # 3. Decompose the task using the VLM
        print("\nSending task and image to VLM for decomposition...")
        steps = decomposer.decompose_task(user_task, current_image)

        # 4. Display the resulting plan
        print("\n--- Generated Task Plan ---")
        if not steps:
            print("The VLM could not generate a plan for this task.")
        else:
            for step in steps:
                print(f"Step {step.get('step', 'N/A')}:")
                print(f"  - Action: {step.get('action', 'Not specified')}")
                print(f"  - Target: {step.get('target', 'Not specified')}")
                print(f"  - Reason: {step.get('reason', 'Not specified')}")
        print("---------------------------\n")

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
    finally:
        # Clean up resources if necessary
        if 'camera' in locals() and hasattr(camera, 'release'):
            camera.release()
        print("Program finished.")

if __name__ == "__main__":
    main()
