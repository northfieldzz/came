"""ストリーミングのMixinモジュール.

OpenCVの使ったストリーミングを行うMixinクラスを持つ.
同じI/Fで他ライブラリのMixinクラスを実装することがあるかも.みたいな考えでMixin化されています.

"""
from threading import Thread
from time import sleep
from logging import getLogger

from requests import Response
import numpy as np
from cv2 import cv2

logger = getLogger(__name__)


class DisconnectError(Exception):
    pass


class CaptureBase:

    def _loop(self, frame) -> bool:
        frame = self.image_process(frame, self.attribute)
        h, w = frame.shape[:2]
        upper_x = round(w * self.crop.left / 100)
        upper_y = round(h * self.crop.top / 100)
        lower_x = w - round(w * self.crop.right / 100) - self.border_width
        lower_y = h - round(h * self.crop.bottom / 100) - self.border_width

        self.preview(frame, upper_x, upper_y, lower_x, lower_y)

        # シャッターイベント発火時処理
        if self.shutter.wait(0):
            self.shutter.clear()
            frame = frame[
                    upper_y + self.border_width: lower_y - self.border_width,
                    upper_x + self.border_width:lower_x - self.border_width
                    ]
            self.output(frame)
            self.shuttered_callback(frame)

        # 停止イベント発火処理
        if self.stop.wait(0):
            return True
        if not self.error_queue.empty():
            error = self.error_queue.get(block=False)
            raise error
        if cv2.waitKey(1) & 0xff == ord('q'):
            return True
        return False

    def shuttered_callback(self, image: np.ndarray) -> None:
        """Callback function when the shutter event is kicked.

        Args:
            image: ndarray
        """
        if self.shuttered_callback_subprocess is not None:
            thread = Thread(target=self.shuttered_callback_subprocess, args=(image, self.error_queue))
            thread.setDaemon(True)
            thread.start()


class RequestsCaptureMixin(CaptureBase):
    def loop(self, response: Response):
        sleep(1)
        content = bytes()
        for chunk in response.iter_content(chunk_size=1024):
            content += chunk
            a = content.find(b'\xff\xd8')
            b = content.find(b'\xff\xd9')
            if a != -1 and b != -1:
                try:
                    jpg = content[a:b + 2]
                    content = content[b + 2:]
                    frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    is_break = self._loop(frame)
                    if is_break:
                        break
                except Exception as e:
                    raise DisconnectError(_('Camera disconnected, please stop Capture.'))


class OpencvCaptureMixin(CaptureBase):
    """mixin class that implements processing during capture with opencv."""

    def loop(self, video: cv2.VideoCapture) -> None:
        sleep(1)
        while video.isOpened():
            result, frame = video.read()
            if not result:
                raise DisconnectError(_('Camera disconnected, please stop Capture.'))
            is_break = self._loop(frame)
            if is_break:
                break
