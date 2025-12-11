import json
import logging
from typing import Optional

import meta
from model.config import ConfigModel, ConfigsModel


class _ConfigService:
    def __init__(self) -> None:
        config_file_path = meta.CONFIG_FILE_PATH

        with open(config_file_path, "r") as f:
            configs = json.load(f)

        self.configs_model = ConfigsModel(*configs)

    def get_config(self, name: str) -> Optional[ConfigModel]:
        """
        获取指定名称的配置

        Args:
            name (str): 配置名称

        Returns:
            Optional[ConfigsModel]: 配置模型对象，如果不存在则返回None
        """

        for config in self.configs_model.configs:
            if config.name == name:
                return config
        return None

    def get_config_name_list(self) -> list[str]:
        return [c.name for c in self.configs_model.configs]


def init_service():
    """初始化服务"""
    global config_service
    logging.info("初始化服务")
    if config_service is None:
        config_service = _ConfigService()


config_service = _ConfigService()
