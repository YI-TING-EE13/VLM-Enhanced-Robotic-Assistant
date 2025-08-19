# VLM-Enhanced Robotic Assistant

## Abstract

This repository presents an advanced modular robotic control system that leverages Vision-Language Models (VLMs) for natural language-based robotic manipulation. The system addresses the fundamental challenge of ambiguity resolution in human-robot interaction by integrating real-time visual perception with multimodal AI models to generate detailed, executable task plans. The architecture implements a pluggable design pattern that enables seamless integration and substitution of core components, now including live video streams and a real-time graphical user interface (GUI).

## Key Features

-   **VLM-Powered Task Decomposition**: Automatically breaks down high-level user commands into a sequence of executable, step-by-step actions using a custom markup language format for reliable parsing.
-   **VLM-Driven Ambiguity Resolution**: Employs a state-of-the-art VLM to interpret ambiguous commands by grounding them in visual context.
-   **Real-time Video Input**: Directly processes live video streams from an Intel RealSense camera, enabling true real-time interaction with the physical world.
-   **Live Vision Console (GUI)**: A new graphical interface that displays the live camera feed alongside the specific frame being analyzed by the VLM, offering crucial real-time feedback for operators and developers.
-   **Modular Pluggable Architecture**: Core components (ASR, VLM, Camera, UI) are built around well-defined interfaces, enabling developers to seamlessly switch between services.
-   **Real-time Audio Capture**: Supports direct microphone input without requiring pre-recorded audio files.
-   **Intelligent Voice-Controlled Shutdown**: Implements safe system termination through voice commands with confirmation mechanisms.
-   **Secure API Key Management**: Uses environment variables for secure credential management.
-   **Robust Error Handling**: The main application loop features comprehensive error handling and automatic recovery mechanisms.
-   **High-Quality, Maintainable Code**: The entire codebase is fully type-hinted and follows modern API documentation standards, making it easy to understand, maintain, and extend.

## System Architecture

The system implements a VLM-centric sequential processing pipeline:

1.  **Input Layer**: The system accepts two primary input modalities:
    -   **Acoustic Input**: User voice commands captured via microphone.
    -   **Visual Input**: A real-time video stream from an Intel RealSense camera.
2.  **GUI Layer**: A `tkinter`-based GUI runs in a separate thread, providing a non-blocking, real-time view of the camera feed and the captured frame for VLM analysis.
3.  **Speech Recognition Module**: Transcribes audio commands to text.
    -   **Primary Implementation**: `WhisperASR` (OpenAI's Whisper).
4.  **Vision-Language Model Core**: Processes the transcribed text and a captured image frame to make a decision.
    -   **Primary Implementation**: `GeminiAPI_VLM` (Google Gemini).
5.  **Task Decomposition Module**: A new layer (`TaskDecomposer`) takes the user's goal and the visual context to generate a detailed, step-by-step plan in a custom markup language, guided by a sophisticated prompt.
6.  **Task Execution and Feedback Module**: Parses the structured plan from the Task Decomposer and executes the appropriate action (e.g., vocalizing a clarification question, confirming an action, or initiating shutdown).
7.  **Continuous Operation Loop**: The system automatically prepares for the next interaction until the user initiates a shutdown.

## Installation and Setup

### Prerequisites

-   **Python Environment**: Python 3.10+ (Conda recommended).
-   **Camera Hardware**: An Intel RealSense Depth Camera (e.g., D400 series).
-   **Audio Processing**: FFmpeg installation is required for the Whisper ASR model.
-   **API Access**: A valid Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### Installation Procedure

1.  **Clone Repository**:
    ```bash
    git clone <your-repository-url>
    cd VLM-Enhanced-Robotic-Assistant
    ```

2.  **Configure Python Environment**:
    ```bash
    # Using Conda (recommended)
    conda create --name vlm_robot_env python=3.10 -y
    conda activate vlm_robot_env
    ```

3.  **Install Dependencies**: This will install all required Python packages, including `pyrealsense2` for the camera.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install FFmpeg**:
    -   **Windows (winget)**: `winget install Gyan.FFmpeg`
    -   **macOS (Homebrew)**: `brew install ffmpeg`
    -   **Linux (APT)**: `sudo apt update && sudo apt install ffmpeg`

5.  **Configure API Key**:
    -   Rename `.env.example` to `.env`.
    -   Edit the `.env` file and add your Gemini API key:
        ```
        GEMINI_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
        ```

### System Execution

To run the application:
```bash
# Activate your conda environment first
conda activate vlm_robot_env

# Run the main script
python main.py
```

## Usage Instructions

### Vision Console (GUI)
Upon launching the application, a new window titled "VLM Robotic Assistant - Vision Console" will appear.
-   **Live Camera Feed (Left Panel)**: Shows the continuous, real-time video stream from the RealSense camera. This allows you to see what the robot is currently observing.
-   **Frame for VLM (Right Panel)**: When you issue a command, this panel updates to show the exact static image that was captured and sent to the VLM for analysis. This is critical for debugging, as it shows the visual basis for the AI's decision.

### Command Interaction
1.  With the system running, enter a command in the terminal when prompted (e.g., "pick up the apple").
2.  The system will capture the current video frame.
3.  The right panel of the GUI will update with the captured frame.
4.  The system will contact the VLM to break down the task. The terminal will then display a structured, step-by-step plan for how the robot would execute your command.

### Safe Shutdown
-   **Voice Command**: Say "關閉系統" (shutdown system). (Note: Voice input is temporarily replaced by text input in the current `main.py`).
-   **GUI Window**: Simply closing the GUI window will also initiate a safe shutdown.
-   **Emergency Exit**: Press `Ctrl+C` in the terminal.

## Project Structure

```
VLM-Enhanced-Robotic-Assistant/
├── main.py                    # Main application entry point
├── requirements.txt           # Python dependency specifications
├── README.md                  # Project documentation
├── Task_Decomposition_Plan.md # Planning document for the VLM task decomposer
├── .env.example               # API key template file
├── src/                       # Source code directory
│   ├── audio_recorder.py      # Audio recording module
│   ├── task_decomposer.py     # NEW: Module for VLM-based task planning
│   ├── asr/                   # Automatic Speech Recognition modules
│   │   ├── __init__.py
│   │   ├── asr_interface.py
│   │   ├── funasr_asr.py
│   │   └── whisper_asr.py
│   ├── camera/                # Camera hardware integration modules
│   │   ├── __init__.py
│   │   ├── camera_interface.py
│   │   └── realsense_camera.py
│   ├── ui/                    # User Interface modules
│   │   ├── __init__.py
│   │   └── gui_manager.py
│   ├── vlm/                   # Vision-Language Model modules
│   │   ├── __init__.py
│   │   ├── vlm_interface.py
│   │   ├── gemini_vlm.py
│   │   └── local_qwen_vlm.py
│   └── tts/                   # Text-to-Speech modules
│       ├── __init__.py
│       └── tts_module.py
└── test_data/                 # Test datasets (for file-based modes)
    ├── test_audio.wav
    └── test_image_*.jpeg
```

## Troubleshooting

1.  **RealSense Camera Not Detected**:
    -   **Error**: `RuntimeError: No device connected` or similar.
    -   **Resolution**: Ensure the RealSense camera is securely connected to a compatible USB 3.0+ port. Verify that the `pyrealsense2` library was installed correctly. The application can now fall back to a placeholder image if no camera is found.
2.  **FFmpeg Installation Error**:
    -   **Error**: `[WinError 2] The system cannot find the file specified`.
    -   **Resolution**: Ensure FFmpeg is installed and its location is in your system's PATH environment variable.

## Research Roadmap and Future Development

### Short-term Objectives (1-3 months)

#### Real-time Interaction Enhancement
- **Task Decomposition**: **Completed**.
- **Live Camera Integration**: **Completed**.
- **Dynamic Scene Analysis**: **In Progress**.
- **Wake Word Detection**: Implement voice activation for hands-free operation.
- **Multi-turn Conversation Management**: Support complex, multi-step instruction sequences.

### Medium-term Research Goals (3-6 months)

#### Robotic Arm Integration
- **ROS (Robot Operating System) Integration**: Complete the hardware-software interface for a real robotic manipulator.
- **Motion Planning and Path Optimization**: Implement intelligent obstacle avoidance.

(The rest of the roadmap remains the same)
