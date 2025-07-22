# VLM-Enhanced Robotic Assistant

## Abstract

This repository presents an advanced modular robotic control system that leverages Vision-Language Models (VLMs) for natural language-based robotic manipulation. The system addresses the fundamental challenge of ambiguity resolution in human-robot interaction by integrating real-time visual perception with multimodal AI models. The architecture implements a pluggable design pattern that enables seamless integration and substitution of core components including Automatic Speech Recognition (ASR), Vision-Language Models, and Text-to-Speech (TTS) services.

## Key Features

-   **VLM-Driven Ambiguity Resolution**: Employs state-of-the-art Gemini 2.5 Flash model to interpret ambiguous commands (e.g., "pick that up") through real-time visual context analysis
-   **Modular Pluggable Architecture**: Core components built around well-defined interfaces (`ASRInterface`, `VLMInterface`) enabling developers to seamlessly switch between services (e.g., Whisper vs. mock ASR, Gemini API vs. local models)
-   **Real-time Audio Capture**: Supports direct microphone input without requiring pre-recorded audio files
-   **Persistent Session Management**: System maintains continuous operation, processing multiple voice interactions without restart requirements
-   **Intelligent Voice-Controlled Shutdown**: Implements safe system termination through voice commands with confirmation mechanisms
-   **Multilingual Speech Processing**: Comprehensive Traditional Chinese speech recognition and synthesis capabilities
-   **Secure API Key Management**: Implements secure credential management through environment variable configuration
-   **Robust Error Handling**: Main application loop features comprehensive error handling and automatic recovery mechanisms
-   **Interactive Feedback System**: Provides real-time voice feedback, clarification requests, and action confirmations through TTSbotic Assistant

## System Architecture

The system implements a VLM-centric sequential processing pipeline following established patterns in multimodal AI systems:

1.  **Input Layer**: The system accepts two primary input modalities:
    -   Acoustic input from user voice commands (captured via microphone or from `.wav` files)
    -   Visual input representing workspace snapshots (image files)

2.  **Speech Recognition Module**: Transcribes audio commands to textual representation
    -   **Primary Implementation**: `WhisperASR` (utilizing OpenAI's Whisper model)
    -   **Alternative Implementation**: `FunASR` (mock implementation for testing)

3.  **Vision-Language Model Core**: Processes transcribed text and visual input through multimodal transformer architecture
    -   **Primary Implementation**: `GeminiAPI_VLM` (Google Gemini 2.5 Flash)
    -   **Alternative Implementation**: `LocalQwenVL` (mock for self-hosted models)

4.  **Task Execution and Feedback Module**: Parses VLM JSON responses and executes appropriate actions
    -   For `clarify` actions: TTS module vocalizes clarification questions
    -   For `shutdown` actions: System requests voice confirmation before safe termination
    -   For command actions (e.g., `pick_up`): System confirms action execution through TTS

5.  **Continuous Operation Loop**: System automatically prepares for subsequent interactions until user-initiated shutdown

## Installation and Setup

### Prerequisites

-   **Python Environment**: Python 3.10+ with Conda environment management (recommended)
-   **Audio Processing**: FFmpeg installation required for Whisper ASR model functionality
-   **API Access**: Valid Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Installation Procedure

1.  **Repository Cloning**:
    ```bash
    git clone <your-repository-url>
    cd VLM-Enhanced-Robotic-Assistant
    ```

2.  **Python Environment Configuration**:
    ```bash
    # Using Conda (recommended)
    conda create --name vlm_robot_env python=3.10 -y
    conda activate vlm_robot_env
    
    # Alternative: using venv
    python -m venv vlm_robot_env
    # Windows
    vlm_robot_env\Scripts\activate
    # macOS/Linux
    source vlm_robot_env/bin/activate
    ```

3.  **Dependency Installation**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **FFmpeg Installation**:
    
    **Windows (using winget - recommended)**:
    ```powershell
    winget install Gyan.FFmpeg
    ```
    
    **Windows (using Chocolatey)**:
    ```powershell
    choco install ffmpeg
    ```
    
    **macOS**:
    ```bash
    brew install ffmpeg
    ```
    
    **Linux**:
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```

5.  **API Key Configuration**:
    -   Rename `.env.example` to `.env`
    -   Edit `.env` file and add your Gemini API key:
        ```
        GEMINI_API_KEY="YOUR_ACTUAL_API_KEY_HERE"
        ```

### System Execution

```bash
python main.py
```

## Usage Instructions

### Continuous Operation Mode (Default)
1. Upon execution, the system initializes all service modules
2. System enters continuous operation mode with interaction counter display
3. For each interaction cycle:
   - Audio capture countdown timer provides user guidance (5-second recording window)
   - System performs multimodal analysis of speech and visual input
   - Voice response delivered through TTS synthesis
   - Automatic preparation for subsequent interaction

### Safe System Shutdown Protocol
1. **Voice Shutdown Command**: Issue "關閉系統" (shutdown system) command
2. **System Confirmation**: System queries "您確定要關閉系統嗎？" (Are you sure you want to shutdown?)
3. **Voice Confirmation**:
   - Affirmative responses ("是", "確定", "好") → System termination
   - Negative responses ("否", "不", "取消") → Continue operation
4. **Emergency Exit**: `Ctrl+C` for immediate safe shutdown

### Microphone Mode Configuration
- **Recording Prompts**: Clear countdown timer and visual feedback
- **Recording Duration**: Default 5-second window (configurable in source)
- **Language Optimization**: Enhanced Traditional Chinese speech recognition
- **Error Recovery**: Automatic retry mechanism for failed recordings

### File-based Input Mode
Modify configuration in `main.py`:
```python
RECORDING_MODE: str = "file"  # Change to "file"
```

### Service Configuration
Modify service selection in `AppConfig` class:
```python
# ASR Service Selection
ASR_SERVICE: str = "whisper"  # or "funasr" (mock)

# VLM Service Selection  
VLM_SERVICE: str = "gemini"   # or "qwen_vl" (mock)
```

## Testing Framework

Execute comprehensive test suite for module validation:

```bash
python run_tests.py
```

## System Extension

### Adding ASR Models

1.  **Class Creation**: Create new file in `src/asr/` directory
2.  **Interface Implementation**: Inherit from `ASRInterface` and implement `transcribe` method
3.  **Factory Update**: Add new option in `src/asr/__init__.py`

### Adding VLM Services

1.  **Class Creation**: Create new file in `src/vlm/` directory
2.  **Interface Implementation**: Inherit from `VLMInterface` and implement `get_decision` method
3.  **Factory Update**: Add new option in `src/vlm/__init__.py`

## Project Structure

```
VLM-Enhanced-Robotic-Assistant/
├── main.py                    # Main application entry point (continuous operation mode)
├── requirements.txt           # Python dependency specifications
├── .env.example              # API key template file
├── .env                      # API key configuration file
├── README.md                 # Project documentation
├── CODE_REVIEW.md            # Code review report
├── UPDATE_SUMMARY.md         # Feature update summary
├── run_tests.py              # Test execution framework
├── src/                      # Source code directory
│   ├── audio_recorder.py     # Audio recording module (microphone functionality)
│   ├── asr/                  # Automatic Speech Recognition modules
│   │   ├── __init__.py
│   │   ├── asr_interface.py
│   │   ├── whisper_asr.py
│   │   └── funasr_asr.py
│   ├── vlm/                  # Vision-Language Model modules
│   │   ├── __init__.py
│   │   ├── vlm_interface.py
│   │   ├── gemini_vlm.py     # Gemini 2.5 Flash integration
│   │   └── local_qwen_vlm.py
│   └── tts/                  # Text-to-Speech modules
│       ├── __init__.py
│       └── tts_module.py     # Traditional Chinese TTS
└── test_data/                # Test datasets
    ├── test_audio.wav
    └── test_image_*.jpeg
```

## Troubleshooting

### Common Issues and Solutions

1.  **FFmpeg Installation Error**:
    ```
    [WinError 2] The system cannot find the file specified
    ```
    **Resolution**: Ensure FFmpeg is properly installed and added to system PATH

2.  **API Quota Limitation**:
    ```
    429 You exceeded your current quota
    ```
    **Resolution**: Verify Gemini API quota limits or switch to lightweight model variants

3.  **Microphone Permission Error**:
    **Resolution**: Ensure application has microphone access permissions in system settings

4.  **Audio Device Configuration Issues**:
    **Resolution**: Verify audio device functionality or switch to file-based input mode

## Contributing

I welcome contributions through Pull Requests and Issues. Please ensure:
1. Code adheres to existing style and architectural patterns
2. Appropriate documentation and test coverage is provided
3. Descriptive commit messages follow conventional commit standards

## License

MIT

## Research Roadmap and Future Development

### Short-term Objectives (1-3 months)

#### Real-time Interaction Enhancement
- **Continuous Dialogue Mode**: Implement persistent conversational context without per-interaction re-initialization
- **Contextual Memory Systems**: Develop episodic memory for instruction history and conversational context retention
- **Wake Word Detection**: Implement voice activation through configurable wake words for hands-free operation
- **Multi-turn Conversation Management**: Support complex multi-step instruction decomposition and sequential execution

#### Real-time Video Stream Processing
- **Live Camera Integration**: Direct USB and network camera input for real-time visual perception
- **Dynamic Scene Analysis**: Continuous workspace monitoring and change detection algorithms
- **Object Tracking and Identification**: Real-time tracking of moving objects and workspace elements
- **Multi-camera Fusion**: Support for simultaneous multi-viewpoint visual input processing

### Medium-term Research Goals (3-6 months)

#### Robotic Arm Integration
- **ROS (Robot Operating System) Integration**: Complete hardware-software interface for real robotic manipulation
- **Motion Planning and Path Optimization**: Intelligent obstacle avoidance and optimal trajectory computation
- **Force Feedback Control Systems**: Precise force control mechanisms with safety protocols
- **Human-Robot Collaboration**: Safe human-robot interaction protocols and collaborative workspace management

#### AI Capability Enhancement
- **Autonomous Learning Systems**: Implement reinforcement learning from human interaction feedback
- **Multimodal Sensor Fusion**: Integration of tactile, auditory, and visual sensory modalities
- **Intent Prediction Models**: Predictive models for anticipating user command sequences
- **Contextual Understanding**: Advanced workspace environment and task context comprehension

### Long-term Vision (6-12 months)

#### Enterprise-scale Applications
- **Multi-user Support Systems**: Concurrent multi-operator system access and management
- **Role-based Access Control**: Hierarchical permission systems for different operator levels
- **Cloud and Edge Deployment**: Scalable deployment architectures for cloud and edge computing environments
- **Real-time Monitoring Dashboard**: Comprehensive system status and performance metrics visualization