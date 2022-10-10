"""Abstract, base class definition..
"""
from os import path
from abc import ABCMeta, abstractmethod
from time import time
from logging import getLogger
from copy import deepcopy
from threading import Thread
from queue import Queue

import numpy as np
from cv2 import cv2

from . import processor

logger = getLogger(__name__)


class Singleton(object):
    """singleton."""
    _instance = None

    def __new__(cls, *args, **kargs):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance


class CameraBase(metaclass=ABCMeta):
    """Camera base class."""
    border_color = (0, 255, 0)
    border_width = 1
    finally_callback = None
    exception_callback = None

    def __init__(self, save_directory, *args, **kwargs) -> None:
        """Constructor..

        Args:
            save_directory: destination directory
        """
        self.save_directory = save_directory
        self.error_queue = Queue()
        super().__init__(*args, **kwargs)

    @abstractmethod
    def capture(self):
        """Run Capture."""
        pass

    @staticmethod
    def image_process(frame, attribute) -> np.ndarray:
        """Post-process image processing.

        Args:
            frame: ndarray
            attribute: Attribute

        Returns: ndarray
        """
        # Contrast & Brightness
        frame = np.clip(attribute.contrast * frame + attribute.brightness, 0, 255).astype(np.uint8)

        # Gamma Compensation
        frame = processor.gamma_compensation(frame, attribute.gamma)

        # Flatten Histogram
        if attribute.high_contrast:
            frame = processor.flatten_histogram(frame)

        # Grayscale
        if attribute.grayscale:
            frame = processor.to_gray(frame)

        # Background removal
        if attribute.background_removal:
            frame = processor.BackgroundRemoval.apply(frame)

        return frame

    def preview(self, frame, upper_x, upper_y, lower_x, lower_y) -> None:
        """Image preview.

        Args:
            frame: ndarray
            upper_x: denotes the upper left vertex x coordinate.
            upper_y: indicates the upper left vertex y coordinate.
            lower_x: denotes the lower right vertex x coordinate.
            lower_y: indicates the lower left vertex y coordinate.
        """
        # プレビュー表示用画像加工
        preview = deepcopy(frame)
        if len(frame.shape) == 2:
            preview = cv2.cvtColor(preview, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(preview,
                      (upper_x, upper_y),
                      (lower_x, lower_y),
                      self.border_color,
                      self.border_width)
        cv2.imshow('Capture', preview)

    def output(self, image: np.ndarray) -> None:
        """Writing images.

        Args:
            image: ndarray
        """
        thread = Thread(target=self._output, args=(image,))
        thread.setDaemon(True)
        thread.start()

    def _output(self, image: np.ndarray):
        if not self.save_directory:
            return
        if not path.isdir(self.save_directory):
            self.error_queue.put(RuntimeError(_('Cannot find destination directory')))
        timestamp: str = str(int(time() * 1000))
        filename = path.join(self.save_directory, f'{timestamp}.jpg')
        try:
            processor.write_image(filename, image)
        except Exception as e:
            logger.error(str(e))
            self.error_queue.put(e)
        logger.debug(f'save {filename}')

    def __enter__(self):
        logger.debug('enter')

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug('throw')
