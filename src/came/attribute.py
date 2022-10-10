"""カメラプロパティモジュール.

カメラセンサーでできる画像処理のフラグ、値の管理を行う.
現在はポストプロセスで処理をしているが、このモジュール自体の変更はなし.
"""


class Attribute:
    def __init__(self, gamma,
                 background_removal,
                 grayscale,
                 high_contrast,
                 contrast=1,
                 brightness=0,
                 filter_kernel=None, **kwargs) -> None:
        self.gamma = gamma
        self.background_removal = background_removal
        self.grayscale = grayscale
        self.high_contrast = high_contrast

        self.contrast = contrast
        self.brightness = brightness
        self.filter_kernel = filter_kernel

    def to_dict(self) -> dict:
        return {
            'gamma': self.gamma,
            'background_removal': self.background_removal,
            'grayscale': self.grayscale,
            'high_contrast': self.high_contrast,
            'contrast': self.contrast,
            'brightness': self.brightness,
            'filter': self.filter_kernel,
        }
