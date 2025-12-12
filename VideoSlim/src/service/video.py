import logging
import os
import subprocess
from typing import Optional

from pymediainfo import MediaInfo

from src import meta
from src.model.message import (
    CompressionCurrentProgressMessage,
    CompressionErrorMessage,
    CompressionFinishedMessage,
    CompressionStartMessage,
    CompressionTotalProgressMessage,
)
from src.model.video import Task, VideoFile
from src.service.config import ConfigService
from src.service.message import MessageService


class VideoService:
    """
    视频处理服务类，提供视频压缩和处理的核心功能

    该类作为应用程序的核心服务之一，负责视频文件的压缩处理，支持单个文件处理和批量任务处理。
    它使用FFmpeg、x264、NeroAACEnc等工具实现视频压缩，并通过消息服务发送处理状态和进度信息，
    使UI能够实时更新处理进度。
    """

    _instance: Optional["VideoService"] = None

    def __init__(self) -> None:
        if self._instance is not None:
            raise ValueError("VideoService 是单例类，不能重复实例化")

        self.message_service = MessageService.get_instance()

    @staticmethod
    def get_instance() -> "VideoService":
        """
        获取 VideoService 的单例实例

        Returns:
            VideoService: VideoService 的单例实例
        """
        if VideoService._instance is None:
            VideoService._instance = VideoService()

        return VideoService._instance

    @staticmethod
    def process_single_file(
        file: VideoFile,
        config_name: str,
        delete_audio: bool,
        delete_source: bool,
    ):
        """
        处理单个视频文件的压缩任务

        Args:
            file: 视频文件对象，包含源文件路径和输出路径信息
            config_name: 压缩配置文件名，用于获取压缩参数
            delete_audio: 是否删除视频中的音频轨道
            delete_source: 是否在压缩完成后删除源文件

        Raises:
            ValueError: 当配置文件不存在或媒体信息读取错误时抛出
            subprocess.CalledProcessError: 当压缩命令执行失败时抛出
        """
        config_service = ConfigService.get_instance()

        # 读取配置
        config = config_service.get_config(config_name)
        if config is None:
            logging.error(f"配置文件 {config_name} 不存在")
            raise ValueError(f"配置文件 {config_name} 不存在")

        # Generate output filename
        output_path = file.output_path

        # Get media info
        media_info = MediaInfo.parse(file.file_path)
        if isinstance(media_info, str):
            logging.error("media_info 读取视频信息错误: 读取到文本")
            raise ValueError("media_info 读取视频信息错误: 读取到文本")

        commands = []

        # Handle video rotation if needed
        if (
            hasattr(media_info.video_tracks[0], "other_rotation")
            and media_info.video_tracks[0].other_rotation
        ):
            logging.info("视频元信息含有旋转，进行预处理")
            pre_temp = "./pre_temp.mp4"
            commands.append(f'./tools/ffmpeg.exe -i "{file.file_path}" "{pre_temp}"')

        # Generate compression commands based on audio presence
        has_audio = len(media_info.audio_tracks) > 0 and not delete_audio

        if has_audio:
            # Process with audio
            commands.extend(
                [
                    # Extract audio to WAV
                    f'./tools/ffmpeg.exe -i "{file.file_path}" -vn -sn -v 0 -c:a pcm_s16le -f wav "./old_atemp.wav"',
                    # Encode audio with AAC
                    './tools/neroAacEnc.exe -ignorelength -lc -br 128000 -if "./old_atemp.wav" -of "./old_atemp.mp4"',
                    # Encode video with x264
                    f"./tools/x264_64-8bit.exe --crf {config.x264.crf} --preset {config.x264.preset} "
                    f"-I {config.x264.I} -r {config.x264.r} -b {config.x264.b} "
                    f"--me umh -i 1 --scenecut 60 -f 1:1 --qcomp 0.5 --psy-rd 0.3:0 "
                    f'--aq-mode 2 --aq-strength 0.8 -o "./old_vtemp.mp4" "{file.file_path}"'
                    + (" --opencl" if config.x264.opencl_acceleration else ""),
                    # Mux video and audio
                    f'./tools/mp4box.exe -add "./old_vtemp.mp4#trackID=1:name=" '
                    f'-add "./old_atemp.mp4#trackID=1:name=" -new "{output_path}"',
                ]
            )
        else:
            # Process without audio
            commands.append(
                f"./tools/x264_64-8bit.exe --crf {config.x264.crf} --preset {config.x264.preset} "
                f"-I {config.x264.I} -r {config.x264.r} -b {config.x264.b} "
                f"--me umh -i 1 --scenecut 60 -f 1:1 --qcomp 0.5 --psy-rd 0.3:0 "
                f'--aq-mode 2 --aq-strength 0.8 -o "{output_path}" "{file.file_path}"'
                + (" --opencl" if config.x264.opencl_acceleration else "")
            )

        # Execute commands
        total_commands = len(commands)
        for index, command in enumerate(commands):
            logging.info(f"执行命令: {command}")

            result = subprocess.run(
                command,
                creationflags=subprocess.CREATE_NO_WINDOW,
                capture_output=True,
                text=True,
            )

            # Log command output
            if result.stdout:
                logging.debug(f"命令输出: {result.stdout.strip()}")
            # if result.stderr:
            #     logging.warning(f"命令警告: {result.stderr.strip()}")

            # Check return code
            if result.returncode != 0:
                logging.error(f"命令执行失败，退出码: {result.returncode}")
                raise subprocess.CalledProcessError(result.returncode, command)

            MessageService.get_instance().send_message(
                CompressionCurrentProgressMessage(
                    file_name=file.file_path,
                    current=index + 1,
                    total=total_commands,
                )
            )

        # Delete source if requested
        if delete_source and os.path.exists(output_path):
            os.remove(file.file_path)

    @staticmethod
    def process_task(task: Task):
        """
        处理视频压缩任务，支持批量处理多个视频文件

        Args:
            task: 视频处理任务对象，包含待处理文件列表和处理配置

        该方法会：
        1. 发送任务开始消息
        2. 遍历处理任务中的每个视频文件
        3. 发送当前文件处理进度消息
        4. 调用process_single_file处理单个文件
        5. 处理可能出现的异常并发送错误消息
        6. 发送任务完成消息
        """
        message_service = MessageService.get_instance()

        logging.info(f"process task: {task.info}")

        logging.debug(f"process task sequence: {task.video_sequence}")

        if task.files_num == 0:
            message_service.send_message(
                CompressionErrorMessage("错误", "没有找到可处理的视频文件")
            )
            return

        message_service.send_message(CompressionStartMessage(task.files_num))

        # Process each file
        for index, video_file in enumerate(task.video_sequence, 1):
            # Notify start of processing
            message_service.send_message(
                CompressionTotalProgressMessage(
                    index,
                    task.files_num,
                    video_file.file_path,
                )
            )

            try:
                VideoService.clean_temp_files()
                VideoService.process_single_file(
                    file=video_file,
                    config_name=task.info.process_config_name,
                    delete_audio=task.info.delete_audio,
                    delete_source=task.info.delete_source,
                )
            except Exception as e:
                logging.error(f"处理文件 {video_file.file_path} 失败: {e}")
                message_service.send_message(
                    CompressionErrorMessage(
                        "错误", f"处理文件 {video_file.file_path} 失败: {e}"
                    )
                )
            finally:
                VideoService.clean_temp_files()

        # Signal completion
        message_service.send_message(
            CompressionFinishedMessage(len(task.video_sequence))
        )

    @staticmethod
    def clean_temp_files():
        """
        清理视频处理过程中生成的临时文件

        该方法会遍历meta.TEMP_FILES中定义的所有临时文件路径，
        并删除存在的临时文件。如果删除失败，会记录警告日志但不会抛出异常。

        Returns:
            None
        """
        for temp_file in meta.TEMP_FILES:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logging.warning(f"删除临时文件 {temp_file} 失败: {e}")
