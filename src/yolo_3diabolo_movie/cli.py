"""パッケージのコマンドラインインターフェース。"""

import argparse

import cv2

from .video import get_video_info


def main() -> None:
    parser = argparse.ArgumentParser(description="3ディアボロ動画の解析ツール")
    commands = parser.add_subparsers(dest="command", required=True)
    info_parser = commands.add_parser("video-info", help="動画のFPSと画素数を表示")
    info_parser.add_argument("path", help="入力動画のパス（MP4など）")
    args = parser.parse_args()
    try:
        info = get_video_info(args.path)
    except (OSError, ValueError, cv2.error) as error:
        parser.exit(1, f"エラー: {error}\n")
    print(f"FPS: {info.fps:.6f}")
    print(f"解像度: {info.width} × {info.height} px")
    print(f"総画素数: {info.pixel_count:,} px / フレーム")
