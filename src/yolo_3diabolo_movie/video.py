"""動画のFPSと解像度の取得。"""

from dataclasses import dataclass
import math
from pathlib import Path

import cv2


@dataclass(frozen=True)
class VideoInfo:
    """FPSはOpenCVの取得値、幅と高さは自動回転前の画素寸法。"""

    fps: float
    width: int
    height: int

    @property
    def pixel_count(self) -> int:
        """1フレームの総画素数。"""
        return self.width * self.height


def get_video_info(path: str | Path) -> VideoInfo:
    """ローカル動画の情報を返す。読み取り不能や不正な情報は例外にする。

    可変FPSの動画では、fpsは各フレームの間隔を保証しない。
    """
    path = Path(path).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"動画ファイルが見つかりません: {path}")

    capture = cv2.VideoCapture(str(path.resolve()))
    try:
        if not capture.isOpened():
            raise ValueError(f"動画を開けません: {path}")
        capture.set(cv2.CAP_PROP_ORIENTATION_AUTO, 0)
        fps = capture.get(cv2.CAP_PROP_FPS)
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        if not all(math.isfinite(value) and value > 0 for value in (fps, width, height)):
            raise ValueError(f"FPSまたは解像度を取得できません: {path}")
        return VideoInfo(fps=fps, width=int(width), height=int(height))
    finally:
        capture.release()
