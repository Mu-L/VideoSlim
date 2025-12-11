"""
VideoSlim - 服务模块

提供应用程序所需的各种服务，包括配置管理、消息传递、存储管理和更新检查等。
"""

import logging

from .config import ConfigService
from .message import MessageService
from .store import StoreService
from .updater import UpdateService
from .video import VideoService


def init_services():
    """
    初始化应用程序的所有服务

    创建并初始化所有服务的单例实例，包括配置服务、消息服务、更新服务、存储服务和视频服务。

    Returns:
        None
    """
    global config_service, message_service, update_service, store_service, video_service
    logging.info("初始化服务")

    config_service = ConfigService.get_instance()
    message_service = MessageService.get_instance()
    update_service = UpdateService.get_instance()
    store_service = StoreService.get_instance()
