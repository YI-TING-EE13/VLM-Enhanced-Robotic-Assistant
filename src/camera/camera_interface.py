# src/camera/camera_interface.py
from abc import ABC, abstractmethod
from PIL import Image

class CameraInterface(ABC):
    """
    Defines the interface for camera hardware services.

    This abstract base class establishes a contract for any class that provides
    image frames to the application. By ensuring all camera implementations
    (e.g., RealSense, standard webcam) adhere to this interface, the system can
    treat them as interchangeable components.
    """

    @abstractmethod
    def get_frame(self) -> Image.Image:
        """
        Captures and returns a single frame from the camera.

        Returns:
            Image.Image: A PIL (Pillow) Image object representing the captured frame.

        Raises:
            RuntimeError: If a frame cannot be captured from the camera source.
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """
        Releases the camera hardware and cleans up resources.

        This method should be called to safely shut down the camera connection,
        ensuring that the hardware is available for other applications.
        """
        pass