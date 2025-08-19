# src/ui/gui_manager.py
import tkinter as tk
from PIL import Image, ImageTk
import threading
import time
from typing import Optional

class GUIManager:
    """
    Manages the real-time visualization GUI for the robot assistant.

    This class runs a tkinter GUI in a separate thread to display a live
    camera feed and the specific frame captured for VLM analysis. It is
    designed to be thread-safe, allowing the main application loop to
    update images without blocking.
    """

    def __init__(self, width: int = 1280, height: int = 520) -> None:
        """
        Initializes the GUIManager and starts the GUI thread.

        Args:
            width (int): The total width of the GUI window.
            height (int): The total height of the GUI window.
        """
        self.root: Optional[tk.Tk] = None
        self.live_panel: Optional[tk.Label] = None
        self.captured_panel: Optional[tk.Label] = None
        self._live_image_tk: Optional[ImageTk.PhotoImage] = None
        self._captured_image_tk: Optional[ImageTk.PhotoImage] = None
        self._last_live_image: Optional[Image.Image] = None
        self._last_captured_image: Optional[Image.Image] = None
        self.lock = threading.Lock()
        self.is_running = False

        self.window_width = width
        self.panel_width = (width // 2) - 30
        self.panel_height = height - 80

        # Start the GUI in a separate, daemonic thread
        self.gui_thread = threading.Thread(target=self._run_gui, daemon=True)
        self.gui_thread.start()

    def _run_gui(self) -> None:
        """
        Creates and runs the main tkinter event loop.
        This method should only be called by the GUI thread.
        """
        self.root = tk.Tk()
        self.root.title("VLM Robotic Assistant - Vision Console")
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)

        self.live_panel = self._create_image_panel(main_frame, "Live Camera Feed")
        self.captured_panel = self._create_image_panel(main_frame, "Frame for VLM")
        
        self.is_running = True
        self._update_loop()
        self.root.mainloop()
        
        # Once mainloop exits, ensure the running flag is false
        self.is_running = False

    def _create_image_panel(self, parent: tk.Frame, title: str) -> tk.Label:
        """
        Creates a labeled panel for displaying an image.

        Args:
            parent (tk.Frame): The parent tkinter frame.
            title (str): The title to display above the image panel.

        Returns:
            tk.Label: The label widget that will serve as the image panel.
        """
        frame = tk.Frame(parent, borderwidth=2, relief="sunken")
        frame.pack(side="left", padx=10, pady=5, fill="both", expand=True)
        label = tk.Label(frame, text=title, font=("Helvetica", 14))
        label.pack(pady=5)
        panel = tk.Label(frame)
        panel.pack(padx=5, pady=5)
        return panel

    def _update_loop(self) -> None:
        """
        Periodically updates the images in the GUI panels.
        This is the core refresh loop for the GUI.
        """
        if not self.is_running or not self.root:
            return

        with self.lock:
            if self._last_live_image and self.live_panel:
                self._update_panel_image(self.live_panel, self._last_live_image)
                self._last_live_image = None  # Consume the frame

            if self._last_captured_image and self.captured_panel:
                self._update_panel_image(self.captured_panel, self._last_captured_image)
                self._last_captured_image = None  # Consume the frame
        
        self.root.after(30, self._update_loop)  # Aim for ~33 FPS refresh rate

    def _update_panel_image(self, panel: tk.Label, pil_image: Image.Image) -> None:
        """
        Resizes and displays a PIL image on a given tkinter panel.

        Args:
            panel (tk.Label): The panel to update.
            pil_image (Image.Image): The PIL image to display.
        """
        resized_image = pil_image.resize((self.panel_width, self.panel_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=resized_image)
        panel.configure(image=img_tk)
        # IMPORTANT: Keep a reference to the image to prevent it from being
        # garbage collected by Python's GC.
        panel.image = img_tk

    def update_image(self, pil_image: Image.Image, panel_type: str) -> None:
        """
        Thread-safe method to update an image for display.

        The main application thread calls this method to provide new frames.

        Args:
            pil_image (Image.Image): The new image to display.
            panel_type (str): The target panel, either "live" or "captured".
        """
        if not self.is_running:
            return
        
        with self.lock:
            if panel_type == "live":
                self._last_live_image = pil_image.copy()
            elif panel_type == "captured":
                self._last_captured_image = pil_image.copy()

    def close(self) -> None:
        """
        Signals the GUI thread to shut down and closes the tkinter window.
        """
        if self.is_running:
            print("GUI Manager: Close signal received.")
            self.is_running = False
            # The mainloop might be blocking. Destroy forces it to exit.
            if self.root:
                self.root.destroy()

    def wait_for_close(self) -> None:
        """
        Allows the main thread to block until the GUI is closed.
        """
        while self.is_running:
            try:
                time.sleep(0.1)
            except KeyboardInterrupt:
                self.close()
                break
