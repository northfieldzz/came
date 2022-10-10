"""カメラのハンドリングを行うモジュール.

CameraBaseクラスを継承したカメラのハンドリングを行う.
カメラ自体がタイマーとかそういった機能を持つのは違うのではないかという思いから
作成したが、正直いらないのではと思っている.
"""
from logging import getLogger
from threading import Thread

from .crop import Crop
from .attribute import Attribute

logger = getLogger(__name__)


class CameraController:
    """controller."""

    def __init__(self, camera, interval_time=None) -> None:
        """constructor.

        Args:
            camera: CameraBase.
            interval_time: Auto Shutter Interval Time.
        """
        self.camera = camera
        self.interval_time = interval_time
        self.capture_thread = Thread(target=self.camera.capture)
        self.capture_thread.setDaemon(True)
        if self.interval_time is not None:
            self.timer_thread = Thread(target=self.timer)
            self.timer_thread.setDaemon(True)

    def timer(self) -> None:
        """timer.

        Execute the shutter method of the camera instance
        at intervals of the number of seconds in interval_time.
        """
        logger.debug('timer loop running')
        while not self.camera.stop.wait(self.interval_time):
            logger.debug('Snap!!')
            self.camera.shutter.set()
        logger.debug('break timer loop')

    def hold(self) -> None:
        """Activate the camera..

        Launch the camera and make a capture.
        If interval_time is not None, the timer function is executed.
        """
        self.capture_thread.start()
        if self.interval_time is not None:
            self.timer_thread.start()

    def release(self) -> None:
        """Shutting down the camera."""
        logger.debug('releasing...')
        self.camera.stop.set()
        if self.interval_time is not None:
            self.timer_thread.join()

    @property
    def crop(self) -> Crop:
        return self.camera.crop

    @crop.setter
    def crop(self, value) -> None:
        self.camera.crop = value

    @property
    def attribute(self) -> Attribute:
        return self.camera.attribute

    @attribute.setter
    def attribute(self, value) -> None:
        self.camera.attribute = value
