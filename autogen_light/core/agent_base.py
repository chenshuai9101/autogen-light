"""智能体基类"""

import logging
from typing import List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    name: str
    system_message: str = ""
    max_consecutive_auto_reply: int = 5
    temperature: float = 0.7


class AgentBase:
    """智能体基类"""
    
    def __init__(self, name: str, system_message: str = "", bus=None):
        self.config = AgentConfig(name, system_message)
        self._bus = bus
        self._replies: List[str] = []
        logger.info(f"智能体创建: {name}")
    
    def receive(self, message: str, sender: str) -> Optional[str]:
        """接收消息，返回回复"""
        logger.info(f"{self.config.name} 收到来自 {sender} 的消息")
        reply = self._generate_reply(message, sender)
        if reply:
            self._replies.append(reply)
        return reply
    
    def _generate_reply(self, message: str, sender: str) -> Optional[str]:
        """生成回复（子类实现）"""
        raise NotImplementedError
    
    @property
    def name(self) -> str:
        return self.config.name
    
    def get_reply_count(self) -> int:
        return len(self._replies)
