"""DroidCamモジュール.

DroidCamアプリのラッパークラス.
OpenCVを使用したストリーミングを行うが、
Mixinクラスを変更するもしくは変更したクラスを定義すれば
OpenCV以外のコンピュータビジョンライブラリでも実装できるはず.

"""
from threading import Event
from logging import getLogger

from cv2 import cv2
from requests import get

from .abstracts import Singleton, CameraBase
from .crop import Crop
from .attribute import Attribute
from .mixin import RequestsCaptureMixin

logger = getLogger(__name__)


class DroidCam(Singleton, CameraBase, RequestsCaptureMixin):
    """DroidCam application wrapper."""

    def __init__(self,
                 address: str,
                 crop: Crop,
                 attribute: Attribute,
                 frame_size,
                 shuttered_callback=None,
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.shutter = Event()
        self.stop = Event()
        self.address = address
        self.crop = crop
        self.attribute = attribute
        self.frame_size = frame_size
        self.shuttered_callback_subprocess = shuttered_callback

    def capture(self) -> None:
        logger.debug('capture loop running...')
        capture_path = self.address
        response = None
        try:
            response = get(
                f'{capture_path}?{self.frame_size[0]}x{self.frame_size[1]}',
                stream=True,
                timeout=5
            )
            cv2.namedWindow('Capture', cv2.WINDOW_NORMAL)
            if response.status_code == 200:
                self.loop(response)
            else:
                raise Exception(f'Api Error Response: {response.status_code} {response.text}')
        except Exception as e:
            if self.exception_callback is not None:
                message = _('If you still see the streaming image on the Droidcam screen, '
                            'disconnect the connection from the settings.')
                self.exception_callback(e, message)
        finally:
            logger.debug('break capture loop')
            if response is not None:
                response.close()
            cv2.destroyAllWindows()
            if self.finally_callback is not None:
                self.finally_callback()
