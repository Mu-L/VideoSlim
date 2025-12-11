import logging
import os
from enum import Enum

import meta
from pydantic import BaseModel

from src.utils import scan_directory


class VideoFile:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path

        if not self.is_supported():
            raise ValueError(f"文件 {self.file_path} 不是支持的视频文件")

    @property
    def fullname(self) -> str:
        """
        获取视频文件的文件名（包含扩展名）

        Returns:
            str: 视频文件的文件名
        """
        return os.path.basename(self.file_path)

    @property
    def filename(self) -> str:
        """
        获取视频文件的文件名（不包含扩展名）

        Returns:
            str: 视频文件的文件名（不包含扩展名）
        """
        return os.path.splitext(self.fullname)[0]

    @property
    def ext(self) -> str:
        """
        获取视频文件的扩展名（小写）

        Returns:
            str: 视频文件的扩展名（小写）
        """
        return os.path.splitext(self.file_path)[1].lower()

    @property
    def output_fullname(self) -> str:
        """
        获取压缩后的视频文件名（包含扩展名）

        Returns:
            str: 压缩后的视频文件名（包含扩展名）
        """
        return f"{self.filename}_x264{self.ext}"

    def is_supported(self) -> bool:
        """
        检查文件是否为支持的视频文件

        Returns:
            bool: 如果文件为支持的视频文件，则返回True
        """
        _, ext = os.path.splitext(self.file_path)
        return (
            os.path.isfile(self.file_path)
            and ext.lower() in meta.SUPPORTED_VIDEO_EXTENSIONS
        )


class TaskStatus(Enum):
    """
    视频处理状态枚举类
    """

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class TaskInfo(BaseModel):
    targets: list[str]
    process_config_name: str
    delete_audio: bool = False
    delete_source: bool = False
    recursive: bool = False


class Task:
    """
    视频处理模型类
    """

    def __init__(self, info: TaskInfo):
        self.current_index: int = 0
        self.info = info

        self.status: TaskStatus = TaskStatus.PENDING

        # 遍历展开文件夹
        self.video_sequence: list[VideoFile] = []
        for path in self.info.targets:
            if not os.path.exists(path):
                continue

            if os.path.isdir(path) and self.info.recursive:
                _, video_files = scan_directory(path, meta.SUPPORTED_VIDEO_EXTENSIONS)
                for file_path in video_files:
                    try:
                        video_file = VideoFile(file_path)
                        self.video_sequence.append(video_file)
                    except ValueError:
                        logging.warning(
                            f"文件 {file_path} 不是支持的视频文件, 已被略过"
                        )
                        continue
                continue

            try:
                video_file = VideoFile(path)
                self.video_sequence.append(video_file)
            except ValueError:
                logging.warning(f"文件 {path} 不是支持的视频文件, 已被略过")
                continue

    @property
    def files_num(self) -> int:
        """
        获取任务中的总文件数

        Returns:
            int: 任务中的总文件数
        """
        return len(self.video_sequence)
