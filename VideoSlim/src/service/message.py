from queue import Queue
from typing import Optional

from model.message import IMessage


class MessageService:
    _instance: Optional["MessageService"] = None

    def __init__(self) -> None:
        if MessageService._instance is not None:
            raise ValueError("MessageService already initialized")

        self.queue = Queue()

    @staticmethod
    def get_instance() -> "MessageService":
        """
        获取消息服务实例

        Returns:
            MessageService: 消息服务实例
        """
        if MessageService._instance is None:
            MessageService._instance = MessageService()

        return MessageService._instance

    def send_message(self, message: IMessage):
        """
        发送消息到队列

        Args:
            message: 消息模型
        """
        self.queue.put(message)

    def try_receive_message(self) -> Optional[IMessage]:
        """
        从队列接收消息

        Args:
            queue: 消息队列

        Returns:
            IMessage: 消息模型
        """
        if self.queue.empty():
            return None
        return self.queue.get_nowait()
