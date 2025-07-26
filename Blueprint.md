# Blueprint: RealSense and GUI Integration

## Part 1: RealSense Real-time Stream Integration

### 1. Project Goal

Upgrade the VLM-Enhanced Robotic Assistant's vision module from reading static image files to processing a real-time video stream from an Intel RealSense camera. This will enable the system to make decisions based on live visual information from the physical world.

### 2. Technology Stack

-   **Camera**: Intel RealSense Depth Camera (e.g., D400 series)
-   **Core Library**: `pyrealsense2` - The official Intel RealSense Python SDK.

### 3. Implementation Steps

(Completed in the previous phase)

---

## Part 2: GUI for Real-time Visualization

### 6. Project Goal

Develop a simple Graphical User Interface (GUI) to provide real-time operational feedback. The GUI will display two video feeds side-by-side:
1.  **Live Camera Feed**: A continuous, real-time stream from the RealSense camera.
2.  **VLM Input Frame**: The specific static frame that is captured and sent to the Vision-Language Model for analysis upon receiving a voice command.

This will allow the operator to easily monitor what the system is seeing and on what visual basis it is making its decisions, which is crucial for debugging and building trust.

### 7. Technology Stack

-   **GUI Library**: `tkinter` - Python's standard, built-in GUI library. It is lightweight and sufficient for this task, requiring no new dependencies.
-   **Image Library**: `Pillow` (PIL) - Already used in the project, it integrates seamlessly with `tkinter` for displaying images.

### 8. Implementation Steps

The core challenge is running the blocking GUI `mainloop` concurrently with the application's main processing loop. We will solve this using Python's `threading` module.

#### Phase 1: Create the GUI Module

**Goal**: Encapsulate all GUI-related code into a separate, manageable module.

1.  **Create New Directory**:
    Create a new directory `src/ui/` to house the GUI code.

2.  **Create `gui_manager.py`**:
    Inside `src/ui/`, create a new file `gui_manager.py`. This file will contain the `GUIManager` class responsible for creating and managing the GUI window and its components.

#### Phase 2: Implement the `GUIManager` Class

**Goal**: Build a class that handles window creation, image updates, and thread-safe operations.

1.  **`GUIManager` Class Structure (`src/ui/gui_manager.py`)**:

    ```python
    import tkinter as tk
    from PIL import Image, ImageTk
    import threading
    import time

    class GUIManager:
        def __init__(self, width=1280, height=480):
            self.root = None
            self.live_panel = None
            self.captured_panel = None
            self.live_image = None
            self.captured_image = None
            self.lock = threading.Lock()
            self.is_running = False

            self.width = width
            self.height = height

            # Start the GUI in a separate thread
            self.gui_thread = threading.Thread(target=self._run_gui, daemon=True)
            self.gui_thread.start()

        def _run_gui(self):
            self.root = tk.Tk()
            self.root.title("VLM Robotic Assistant - Vision Console")
            self.root.protocol("WM_DELETE_WINDOW", self.close)

            # Create main frame
            main_frame = tk.Frame(self.root)
            main_frame.pack(padx=10, pady=10)

            # Create panels
            self.live_panel = self._create_image_panel(main_frame, "Live Camera Feed")
            self.captured_panel = self._create_image_panel(main_frame, "Frame for VLM")
            
            self.is_running = True
            self._update_loop()
            self.root.mainloop()

        def _create_image_panel(self, parent, title):
            frame = tk.Frame(parent, borderwidth=2, relief="sunken")
            frame.pack(side="left", padx=10, pady=5)
            label = tk.Label(frame, text=title, font=("Helvetica", 14))
            label.pack(pady=5)
            panel = tk.Label(frame)
            panel.pack()
            return panel

        def _update_loop(self):
            if not self.is_running:
                return

            with self.lock:
                if self.live_image:
                    self._update_panel_image(self.live_panel, self.live_image)
                    self.live_image = None # Consume the frame

                if self.captured_image:
                    self._update_panel_image(self.captured_panel, self.captured_image)
                    self.captured_image = None # Consume the frame
            
            self.root.after(30, self._update_loop) # ~33 FPS refresh rate

        def _update_panel_image(self, panel, pil_image):
            img_tk = ImageTk.PhotoImage(image=pil_image)
            panel.configure(image=img_tk)
            panel.image = img_tk # Keep a reference!

        def update_image(self, pil_image, panel_type):
            if not self.is_running:
                return
            with self.lock:
                if panel_type == "live":
                    self.live_image = pil_image.copy()
                elif panel_type == "captured":
                    self.captured_image = pil_image.copy()

        def close(self):
            if self.is_running:
                self.is_running = False
                # Give the update loop a moment to stop
                time.sleep(0.1)
                if self.root:
                    self.root.quit()
                    self.root.destroy()
    ```

2.  **Create `__init__.py`**:
    Create an empty `src/ui/__init__.py` file to make it a Python package.

#### Phase 3: Integrate GUI into the Main Application

**Goal**: Modify `main.py` to instantiate the `GUIManager` and send image frames to it.

1.  **Update `main.py`**:
    -   Import the `GUIManager` class.
    -   In the `main` function, create an instance of `GUIManager` at the beginning.
    -   In the main `while` loop, after capturing a frame from the camera, immediately call `gui.update_image(current_frame, "live")` to update the live feed.
    -   Just before calling `vlm.get_decision`, call `gui.update_image(image_to_be_processed, "captured")` to show the frame being analyzed.
    -   In the final `finally` block, ensure `gui.close()` is called to gracefully shut down the GUI window.

    **Example `main.py` modifications:**

    ```python
    # main.py
    # ... other imports
    from src.ui.gui_manager import GUIManager

    def main():
        # ...
        # 1. Initialize GUI
        gui = GUIManager()
        
        # Wait for GUI to be ready
        import time
        while not gui.is_running:
            time.sleep(0.1)

        # ... initialize other services
        
        try:
            while True:
                # ...
                try:
                    # 2. Update live feed
                    audio_file, image_file = get_user_inputs(config, camera_service)
                    gui.update_image(image_file, "live")
                    
                    # ... (transcribe audio)
                    
                    if instruction_text:
                        # 3. Update captured frame before sending to VLM
                        gui.update_image(image_file, "captured")
                        should_continue = process_command(...)
                    
                    # ...
                # ...
        finally:
            # 4. Close GUI
            print("Closing GUI...")
            gui.close()
            # ... release other resources
    ```

## 9. Next Steps

With this blueprint updated, the next step is to implement the code changes. This will involve creating the new `src/ui` module and then integrating it into the existing `main.py` application flow.