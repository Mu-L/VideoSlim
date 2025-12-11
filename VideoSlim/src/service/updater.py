import logging
from typing import Optional

import requests
from model.message import UpdateMessage
from service.message import MessageService

from src import meta


class UpdateService:
    _instance: Optional["UpdateService"] = None

    def __init__(self):
        if UpdateService._instance is not None:
            raise ValueError("UpdateService already initialized")
        UpdateService._instance = self

    @staticmethod
    def get_instance() -> "UpdateService":
        if UpdateService._instance is None:
            UpdateService._instance = UpdateService()

        return UpdateService._instance

    @staticmethod
    def check_for_updates():
        """
        检测是否有新版本
        """
        message_service = MessageService.get_instance()
        try:
            response = requests.get(meta.CHECK_UPDATE_URL, timeout=10)
            data = response.json()

            if data and len(data) > 0:
                latest_release = data[0]
                if latest_release["tag_name"] != meta.VERSION:
                    message_service.send_message(UpdateMessage())
        except Exception as e:
            logging.warning(f"检查更新失败: {e}")
