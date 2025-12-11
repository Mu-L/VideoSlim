from abc import ABC

__all__ = [
    "IMessage",
    "WarningMessage",
    "UpdateMessage",
    "ErrorMessage",
    "ExitMessage",
    "ConfigLoadMessage",
    "CompressionErrorMessage",
    "CompressionFinishedMessage",
    "CompressionStartMessage",
    "CompressionProgressMessage",
]


class IMessage(ABC):
    pass


class WarningMessage(IMessage):
    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message


class UpdateMessage(IMessage):
    def __init__(self):
        pass


class ErrorMessage(IMessage):
    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message


class ExitMessage(IMessage):
    def __init__(self):
        pass


class ConfigLoadMessage(IMessage):
    def __init__(self, config_names: list[str]):
        self.config_names = config_names


class CompressionErrorMessage(IMessage):
    def __init__(self, title: str, message: str):
        self.title = title
        self.message = message


class CompressionFinishedMessage(IMessage):
    def __init__(self, total: int):
        self.total = total


class CompressionStartMessage(IMessage):
    def __init__(self, total: int):
        self.total = total


class CompressionProgressMessage(IMessage):
    def __init__(self, current: int, total: int, file_name: str):
        self.current = current
        self.total = total
        self.file_name = file_name
