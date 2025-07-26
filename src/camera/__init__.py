# src/camera/__init__.py
from .camera_interface import CameraInterface
from .realsense_camera import RealsenseCamera

def get_camera(camera_type: str = "realsense", **kwargs) -> CameraInterface:
    """
    Factory function to create and return a camera instance based on type.

    This function acts as a single point of entry for creating camera objects,
    allowing the main application to be decoupled from specific camera implementations.

    Args:
        camera_type (str): The type of camera to create. Currently supports
                           'realsense'.
        **kwargs: Additional keyword arguments to be passed to the camera's
                  constructor (e.g., width, height, fps).

    Returns:
        CameraInterface: An instance of a class that implements the CameraInterface.

    Raises:
        ValueError: If an unsupported camera_type is provided.
    """
    if camera_type == "realsense":
        return RealsenseCamera(**kwargs)
    # Future camera types like "webcam" can be added here.
    else:
        raise ValueError(f"Unsupported camera type: {camera_type}")