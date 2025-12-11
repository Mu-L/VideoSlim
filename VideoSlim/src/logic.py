import logging
import os
from queue import Queue
from typing import Any, List, Tuple

from .model import *
from .model.message import *


def clean_temp_files(temp_file_names: list[str]):
    """Clean up temporary files"""
    for temp_file in temp_file_names:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logging.warning(f"删除临时文件 {temp_file} 失败: {e}")


def get_output_filename(input_path: str) -> str:
    """
    Generate output filename for compressed video

    Args:
        input_path: Input video file path

    Returns:
        Output file path
    """
    file_name, _ = os.path.splitext(input_path)
    return f"{file_name}_x264.mp4"


def scan_directory(
    directory: str, extensions: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Recursively scan directory for files with specific extensions

    Args:
        directory: Directory to scan
        extensions: List of file extensions to include

    Returns:
        Tuple of (subfolders, files)
    """
    subfolders, files = [], []

    for entry in os.scandir(directory):
        if entry.is_dir():
            subfolders.append(entry.path)
        elif entry.is_file() and os.path.splitext(entry.name)[1].lower() in extensions:
            files.append(entry.path)

    # Recursively scan subfolders
    for folder in list(subfolders):
        sf, f = scan_directory(folder, extensions)
        subfolders.extend(sf)
        files.extend(f)

    return subfolders, files


def send_message(queue: Queue, message: IMessage):
    queue.put(message)


def get_file_paths_from_list(
    file_paths: list[str],
    files_to_process: list[Any],
    recurse: bool,
    video_extensions: list[str],
):
    for file_path in file_paths:
        if not file_path or not os.path.exists(file_path):
            continue

        if os.path.isdir(file_path) and recurse:
            # Recursively scan directory for video files
            _, video_files = scan_directory(file_path, video_extensions)
            files_to_process.extend(video_files)
        elif is_video_file(file_path, video_extensions):
            files_to_process.append(file_path)


def check_for_updates(queue, version):
    """Check for newer versions on GitHub"""
    try:
        url = "https://api.github.com/repos/mainite/VideoSlim/releases"
        response = requests.get(url, timeout=10)
        data = response.json()

        if data and len(data) > 0:
            latest_release = data[0]
            if latest_release["tag_name"] != version:
                send_message(queue, UpdateMessage())
    except Exception as e:
        logging.warning(f"检查更新失败: {e}")
