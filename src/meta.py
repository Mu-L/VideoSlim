import os
import sys

"""
VideoSlim 应用程序常量定义
"""

# 应用程序版本号
VERSION = "v2.0.0"

# 检查更新的 GitHub API URL
CHECK_UPDATE_URL = "https://api.github.com/repos/mainite/VideoSlim/releases"

# 支持的视频文件扩展名列表
SUPPORTED_VIDEO_EXTENSIONS = [".mp4", ".mkv", ".mov", ".avi"]

# 配置文件路径
CONFIG_FILE_PATH = "config.json"

# 存储文件路径
STORE_PATH = "store"

# 临时文件路径列表
TEMP_FILES = ["./pre_temp.mp4"]


def get_ffmpeg_path() -> str:
    if hasattr(sys, "_MEIPASS"):
        # Running in a bundled environment
        return os.path.join(sys._MEIPASS, "tools", "ffmpeg.exe")  # type: ignore[attr-defined]
    else:
        # Running in a development environment
        return os.path.join("./tools", "ffmpeg.exe")


FFMPEG_PATH = get_ffmpeg_path()
