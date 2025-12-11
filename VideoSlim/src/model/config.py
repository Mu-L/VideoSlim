from pydantic import BaseModel, Field


class X264ConfigModel(BaseModel):
    """
    X264配置模型类，用于定义X264编码器的配置参数。
    """

    crf: float = Field(default=23.5, gt=0, lt=51, description="CRF值，范围在0-51之间")
    preset: int = Field(default=8, gt=0, lt=9, description="编码预设值，范围在0-9之间")
    I: int = 600
    r: int = 4
    b: int = 3
    opencl_acceleration: bool = False


class ConfigModel(BaseModel):
    """
    配置模型类，用于定义配置文件的结构。
    """

    name: str = "default"
    x264: X264ConfigModel = X264ConfigModel()


class ConfigsModel(BaseModel):
    """
    多个配置
    """

    configs: list[ConfigModel] = []
