"""推論カメラパッケージ.
"""

from enum import Enum
from logging import getLogger
from gettext import install

from .webcam import WebCam
from .droidcam import DroidCam

install('messages')

logger = getLogger(__name__)


class CameraType(Enum):
    WebCam = 0
    DroidCam = 1


def get_camera_class(camera_type):
    """get Camera class.

    Args:
        camera_type: CameraType

    Returns: CameraBase

    """
    if camera_type == CameraType.WebCam:
        return WebCam
    if camera_type == CameraType.DroidCam:
        return DroidCam
