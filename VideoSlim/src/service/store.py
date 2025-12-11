import logging

from model.store import JSONStore

global_store = JSONStore("status.json")


def init_service():
    """初始化服务"""
    logging.info("初始化服务")
    global global_store
    if global_store is None:
        global_store = JSONStore("status.json")
