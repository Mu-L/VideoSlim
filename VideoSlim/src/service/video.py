import logging
import os
import subprocess

import meta
from model.message import (
    CompressionErrorMessage,
    CompressionFinishedMessage,
    CompressionProgressMessage,
    CompressionStartMessage,
)
from model.video import Task, VideoFile
from pymediainfo import MediaInfo
from service.config import ConfigService
from service.message import MessageService


class VideoService:
    @staticmethod
    def process_single_file(
        file: VideoFile,
        config_name: str,
        delete_audio: bool,
        delete_source: bool,
    ):
        """
        处理单个视频文件

        Args:
            file: 视频文件对象
            config_name: 配置文件名
            delete_audio: 是否删除音频轨道
            delete_source: 是否删除源文件
            index: 当前文件索引
            total: 总文件数
            temp_file_names: 临时文件名列表
        """
        config_service = ConfigService.get_instance()

        # 读取配置
        config = config_service.get_config(config_name)
        if config is None:
            logging.error(f"配置文件 {config_name} 不存在")
            raise ValueError(f"配置文件 {config_name} 不存在")

        # Generate output filename
        output_path = file.output_fullname

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
        for command in commands:
            logging.info(f"执行命令: {command}")
            subprocess.check_call(command, creationflags=subprocess.CREATE_NO_WINDOW)

        # Delete source if requested
        if delete_source and os.path.exists(output_path):
            os.remove(file.file_path)

    @staticmethod
    def process_task(task: Task):
        """
        压缩处理视频文件的主函数
        """
        message_service = MessageService.get_instance()

        if task.files_num:
            message_service.send_message(
                CompressionErrorMessage("错误", "没有找到可处理的视频文件")
            )
            return

        message_service.send_message(CompressionStartMessage(task.files_num))

        # Process each file
        for index, video_file in enumerate(task.video_sequence, 1):
            # Notify start of processing
            message_service.send_message(
                CompressionProgressMessage(index, task.files_num, video_file.file_path)
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
        清理临时文件
        """
        for temp_file in meta.TEMP_FILES:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logging.warning(f"删除临时文件 {temp_file} 失败: {e}")
