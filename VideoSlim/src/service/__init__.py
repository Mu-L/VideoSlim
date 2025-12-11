import logging

from .config import ConfigService
from .message import MessageService
from .store import StoreService
from .updater import UpdateService


def init_services():
    global config_service, message_service, update_service, store_service
    """初始化服务"""
    logging.info("初始化服务")

    config_service = ConfigService.get_instance()
    message_service = MessageService.get_instance()
    update_service = UpdateService.get_instance()
    store_service = StoreService.get_instance()
