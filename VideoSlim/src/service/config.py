import json
from typing import Optional

import meta
from model.config import ConfigModel, ConfigsModel


class ConfigService:
    _instance: Optional["ConfigService"] = None

    def __init__(self) -> None:
        if ConfigService._instance is not None:
            raise ValueError("ConfigService already initialized")

        config_file_path = meta.CONFIG_FILE_PATH

        with open(config_file_path, "r") as f:
            configs = json.load(f)

        self.configs_model = ConfigsModel(*configs)

    @staticmethod
    def get_instance() -> "ConfigService":
        """
        获取配置服务实例

        Returns:
            ConfigService: 配置服务实例
        """
        if ConfigService._instance is None:
            ConfigService._instance = ConfigService()

        return ConfigService._instance

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
