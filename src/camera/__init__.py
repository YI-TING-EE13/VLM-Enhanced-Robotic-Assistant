# src/camera/__init__.py
"""
Camera module for providing image capture services.

This package uses a factory pattern to instantiate and provide access to
various camera services. The `get_camera_service` function acts as a single
entry point, allowing the application to dynamically select a camera
implementation (e.g., a physical RealSense camera or a mock/test camera).
"""

from typing import Any
from .camera_interface import CameraInterface
from .realsense_camera import RealsenseCamera

def get_camera_service(service_name: str = "realsense", **kwargs: Any) -> CameraInterface:
    """
    Factory function to create and return an instance of a camera service.

    Args:
        service_name (str): The identifier for the desired camera service.
                            Supported values: "realsense".
                            Defaults to "realsense".
        **kwargs: Additional keyword arguments to be passed to the constructor
                  of the selected camera service.

    Returns:
        CameraInterface: An object that conforms to the CameraInterface.

    Raises:
        ValueError: If the specified `service_name` is not supported.
    """
    if service_name == "realsense":
        return RealsenseCamera(**kwargs)
    else:
        raise ValueError(f"Unsupported camera service: '{service_name}'")

# Expose the core components for easy import.
__all__ = ["CameraInterface", "get_camera_service"]
