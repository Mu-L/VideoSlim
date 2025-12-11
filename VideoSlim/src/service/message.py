from queue import Queue
from typing import Optional

from model.message import IMessage


class _MessageService:
    def __init__(self) -> None:
        self.queue = Queue()

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


def init_service():
    """初始化服务"""
    global message_service
    if message_service is None:
        message_service = _MessageService()


message_service = _MessageService()
