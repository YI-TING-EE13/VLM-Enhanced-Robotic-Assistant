# src/camera/realsense_camera.py
import pyrealsense2 as rs
import numpy as np
from PIL import Image
from .camera_interface import CameraInterface

class RealsenseCamera(CameraInterface):
    """
    An implementation of the CameraInterface for Intel RealSense cameras.

    This class manages the connection to a RealSense device, configures the
    color stream, and captures frames for the application.
    """

    def __init__(self, width: int = 640, height: int = 480, fps: int = 30):
        """
        Initializes the RealSense camera and starts the pipeline.

        Args:
            width (int): The desired width of the color stream.
            height (int): The desired height of the color stream.
            fps (int): The desired frames per second of the color stream.
        
        Raises:
            RuntimeError: If the camera fails to initialize or start the pipeline.
        """
        try:
            self.pipeline = rs.pipeline()
            config = rs.config()
            config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
            self.pipeline.start(config)
            print("RealSense Camera initialized.")
        except Exception as e:
            print(f"Failed to initialize RealSense Camera: {e}")
            raise

    def get_frame(self) -> Image.Image:
        """
        Waits for and retrieves a color frame from the RealSense pipeline.

        Returns:
            Image.Image: A PIL Image object in RGB format.

        Raises:
            RuntimeError: If a color frame could not be obtained from the device.
        """
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            raise RuntimeError("Could not get color frame from RealSense camera.")
        
        # Convert the image from BGR (used by RealSense) to RGB format.
        color_image = np.asanyarray(color_frame.get_data())
        color_image_rgb = color_image[:, :, ::-1]  # BGR to RGB
        
        return Image.fromarray(color_image_rgb)

    def release(self) -> None:
        """
        Stops the RealSense pipeline to release the camera hardware.
        """
        print("Stopping RealSense camera pipeline...")
        self.pipeline.stop()
        print("RealSense Camera stopped.")