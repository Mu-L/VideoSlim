import logging

from . import config, message


def init_services():
    """初始化服务"""
    logging.info("初始化服务")
    config.init_service()
    message.init_service()
