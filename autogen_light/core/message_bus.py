"""消息总线 - 智能体间通信"""

import logging
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Message:
    sender: str
    receiver: str  # "*" for broadcast
    content: str
    msg_type: str = "text"
    round: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class MessageBus:
    """消息总线"""
    
    def __init__(self):
        self._history: List[Message] = []
        self._handlers: dict = {}
        self._round = 0
        logger.info("消息总线初始化")
    
    def send(self, msg: Message) -> None:
        """发送消息"""
        msg.round = self._round
        self._history.append(msg)
        logger.debug(f"消息: {msg.sender} → {msg.receiver}: {msg.content[:50]}")
    
    def broadcast(self, sender: str, content: str, msg_type: str = "text") -> None:
        """广播消息"""
        msg = Message(sender, "*", content, msg_type, self._round)
        self.send(msg)
    
    def get_history(self, agent_name: str = None, limit: int = 50) -> List[Message]:
        """获取对话历史"""
        if not agent_name:
            return self._history[-limit:]
        return [m for m in self._history[-limit:] 
                if m.sender == agent_name or m.receiver == agent_name or m.receiver == "*"]
    
    def next_round(self) -> int:
        """进入下一轮"""
        self._round += 1
        return self._round
    
    @property
    def current_round(self) -> int:
        return self._round
    
    def clear(self) -> None:
        self._history.clear()
        self._round = 0
