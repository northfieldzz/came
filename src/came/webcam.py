"""Ipカメラのラッパーモジュール.

Ipカメラをラップしたクラスが格納される.
OpenCVを使用したストリーミングを行うが、
Mixinクラスを変更するもしくは変更したクラスを定義すれば
OpenCV以外のコンピュータービジョンライブラリでも実装できるはず.

"""
from threading import Event
from logging import getLogger

from cv2 import cv2

from .abstracts import Singleton, CameraBase
from .crop import Crop
from .attribute import Attribute
from .mixin import OpencvCaptureMixin, DisconnectError

logger = getLogger(__name__)


class WebCam(Singleton, CameraBase, OpencvCaptureMixin):
    """Webcam, network camera class."""

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

        # パスの変換
        # ネットワーク経由のカメラであればstring
        # シリアルポート経由のカメラであればint
        capture_path = self.address
        if capture_path.isdecimal():
            capture_path = int(capture_path)

        # OpenCV キャプチャインスタンス
        video = cv2.VideoCapture(capture_path, cv2.CAP_DSHOW)
        try:
            if not video.isOpened():
                raise DisconnectError(_('Unable to connect to the camera. please stop Capture.'))
            video.set(cv2.CAP_PROP_FPS, 60)
            video.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_size[0])
            video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_size[1])
            width = video.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            logger.debug(f'FPS   : {video.get(cv2.CAP_PROP_FPS)}')
            logger.debug(f'WIDTH : {width}')
            logger.debug(f'HEIGHT: {height}')
            window_name = _('Capture')
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, (int(width), int(height)))
            self.loop(video)
        except Exception as e:
            if self.exception_callback is not None:
                self.exception_callback(e)
        finally:
            logger.debug('break capture loop')
            video.release()
            cv2.destroyAllWindows()
            if self.finally_callback is not None:
                self.finally_callback()
