"""Image Processing Module.

画像処理を行うmodule.
NOTE: 今後もこのmoduleは巨大化することが予想されるのでパッケージ化等考える必要あり.

"""
from os import path, remove
from logging import getLogger
import numpy as np
from cv2 import cv2

logger = getLogger(__name__)


def read_image(filename: str, flags=cv2.IMREAD_COLOR, dtype=np.uint8) -> np.ndarray:
    try:
        n = np.fromfile(filename, dtype)
        image = cv2.imdecode(n, flags)
        return image
    except Exception as e:
        logger.error(str(e))
        return None


def write_image(filename: str, image: np.ndarray, params=None) -> None:
    try:
        ext = path.splitext(filename)[1]
        result, n = cv2.imencode(ext, image, params)
        if result:
            with open(filename, mode='w+b') as f:
                n.tofile(f)
    except Exception as e:
        if path.isfile(filename):
            remove(filename)
        logger.error(str(e))
        message = _("The image could not be saved")
        raise RuntimeError(f'{message}({e})')


def to_gray(img) -> np.ndarray:
    """Convert an image to grayscale.

    Args:
        img: ndarray

    Returns: ndarray
    """
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


class BackgroundRemoval:
    sub_tractor = cv2.createBackgroundSubtractorMOG2()

    @classmethod
    def apply(cls, frame) -> np.ndarray:
        return cls.sub_tractor.apply(frame)


def gamma_compensation(img, gamma) -> np.ndarray:
    """Gamma correction.

    Args:
        img: ndarray
        gamma: float

    Returns: ndarray
    """
    gamma_cvt = np.zeros((256, 1), dtype='uint8')
    for i in range(256):
        gamma_cvt[i][0] = 255 * (float(i) / 255) ** gamma
    return cv2.LUT(img, gamma_cvt)


def flatten_histogram(img) -> np.ndarray:
    """Histogram flattening.

    Args:
        img: ndarray

    Returns: ndarray
    """
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    img_yuv[:, :, 0] = cv2.equalizeHist(img_yuv[:, :, 0])
    img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    return img


def white_balance(img) -> np.ndarray:
    """Automatic white balance adjustment.

    Args:
        img: ndarray

    Returns: ndarray
    """
    result = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    avg_a = np.average(result[:, :, 1])
    avg_b = np.average(result[:, :, 2])
    result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
    result = cv2.cvtColor(result, cv2.COLOR_LAB2BGR)
    return result
