import threading

from model.video import Task, TaskInfo
from service.updater import UpdateService
from service.video import VideoService


class Controller:
    def __init__(self):
        threading.Thread(
            target=UpdateService.check_for_updates,
            daemon=True,
        ).start()

    def compression(
        self,
        config_name: str,
        delete_audio: bool,
        delete_source: bool,
        file_paths: list[str],
        recurse: bool,
    ):
        """
        压缩视频文件

        Args:
            config_name (str): 配置名称
            delete_audio (bool): 是否删除音频
            delete_source (bool): 是否删除源文件
            file_paths (list[str]): 文件路径列表
            recurse (bool): 是否递归子目录
        """

        task = Task(
            info=TaskInfo(
                targets=file_paths,
                process_config_name=config_name,
                delete_audio=delete_audio,
                delete_source=delete_source,
                recursive=recurse,
            ),
        )

        threading.Thread(
            target=VideoService.process_task,
            args=(task,),
            daemon=True,
        ).start()
