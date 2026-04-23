"""群组聊天 v2 - 上下文压缩 + 角色分化"""

import logging
from typing import List
from dataclasses import dataclass, field
from .message_bus import Message

logger = logging.getLogger(__name__)


@dataclass
class GroupChatConfig:
    agents: list = field(default_factory=list)
    max_round: int = 10


class GroupChat:
    """群组聊天 v2 - 上下文摘要 + 角色差异化"""

    def __init__(self, agents: list, max_round: int = 10, bus=None):
        self.agents = agents
        self.config = GroupChatConfig(agents, max_round)
        self._bus = bus
        self._conversation = []
        logger.info(f"群组v2创建: {len(agents)}个成员, 最大{max_round}轮")

    def _summarize_context(self, agent_name: str, round_num: int) -> str:
        """生成当前Agent的上下文摘要"""
        if not self._conversation:
            return ""

        # 取最近N条消息
        recent = self._conversation[-6:] if len(self._conversation) > 6 else self._conversation

        context_lines = []
        for m in recent:
            if m["speaker"] == "system":
                continue
            # 排除当前Agent自己的上一条发言（减少回声）
            if m["speaker"] == agent_name and m.get("round", 0) == round_num - 1:
                continue
            context_lines.append(f"[{m['speaker']}]: {m['content'][:100]}")

        if not context_lines:
            return ""

        return "对话上下文:\n" + "\n".join(context_lines[-4:])

    def run(self, task: str) -> dict:
        logger.info(f"群组v2任务: {task[:80]}...")
        self._conversation.append({"speaker": "system", "content": f"任务: {task}"})

        for round_num in range(self.config.max_round):
            self._round = round_num + 1

            for agent in self.agents:
                context = self._summarize_context(agent.name, self._round)

                # 第一轮每个人的提示不同
                if self._round == 1:
                    prompt = f"任务: {task}"
                elif context:
                    prompt = f"{context}\n\n请根据之前的讨论继续。"
                else:
                    prompt = f"继续讨论: {task}"

                # 给多个Agent不同的差异化提示
                if self._round > 1:
                    other_agents = [a.name for a in self.agents if a.name != agent.name]
                    if other_agents:
                        prompt += f"\n参考其他成员的意见: {', '.join(other_agents)}。"

                try:
                    reply = agent.receive(prompt, self._conversation[-1]["speaker"] if len(self._conversation) > 1 else "system")
                except Exception as e:
                    reply = f"[{agent.name}] 回复失败: {e}"

                if reply:
                    self._conversation.append({
                        "speaker": agent.name,
                        "content": reply,
                        "round": self._round,
                    })
                    if self._bus:
                        self._bus.send(Message(agent.name, "*", reply))

            if self._bus:
                self._bus.next_round()

            # 检查是否所有Agent都说一样的
            last_round_msgs = [m for m in self._conversation if m.get("round") == self._round]
            if len(last_round_msgs) >= 2:
                contents = set(m["content"][:30] for m in last_round_msgs)
                if len(contents) == 1 and self._round >= 3:
                    logger.info(f"第{self._round}轮所有Agent回复相同，提前结束")
                    break

            if self._round >= self.config.max_round:
                break

        summary = f"群组协作完成: {len(self._conversation)}条消息, {self._round}轮"
        self._conversation.append({"speaker": "system", "content": summary})
        return {
            "success": True,
            "task": task,
            "rounds": self._round,
            "agents": [a.name for a in self.agents],
            "conversation": self._conversation,
            "summary": summary,
        }
