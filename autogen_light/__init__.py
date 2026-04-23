"""AutoGen Light - 轻量级多智能体协作框架"""

__version__ = "1.0.0"
__author__ = "牧云野"

from .core.agent_base import AgentBase, AgentConfig
from .core.group_chat import GroupChat, GroupChatConfig
from .core.message_bus import Message, MessageBus
from .agents.assistant import AssistantAgent
from .agents.user_proxy import UserProxyAgent


class AutoGenLight:
    """AutoGen Light 主类"""
    
    def __init__(self):
        self._agents = {}
        self._bus = MessageBus()
        self._group = None
        print(f"AutoGen Light v{__version__} 初始化完成")
    
    def create_assistant(self, name: str, system_message: str = "") -> "AssistantAgent":
        agent = AssistantAgent(name, system_message, self._bus)
        self._agents[name] = agent
        print(f"  ✅ 创建助手: {name}")
        return agent
    
    def create_user_proxy(self, name: str = "用户", interactive: bool = False) -> "UserProxyAgent":
        agent = UserProxyAgent(name, self._bus, interactive)
        self._agents[name] = agent
        print(f"  ✅ 创建用户代理: {name}")
        return agent
    
    def create_group_chat(self, agents: list, max_round: int = 10):
        """创建群组聊天"""
        self._group = GroupChat(agents, max_round, self._bus)
        print(f"  ✅ 创建群组: {len(agents)}个智能体, 最大{max_round}轮")
        return self._group
    
    def run(self, task: str) -> dict:
        """运行协作"""
        if not self._group:
            return {"error": "请先创建群组"}
        return self._group.run(task)
    
    def get_info(self) -> dict:
        return {
            "version": __version__,
            "agents": list(self._agents.keys()),
            "group_active": self._group is not None,
        }
