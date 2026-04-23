"""用户代理智能体 v2 - 支持实时终端输入 + AI驱动"""

import logging, sys
from ..core.agent_base import AgentBase

logger = logging.getLogger(__name__)


class UserProxyAgent(AgentBase):
    """用户代理 v2 - 支持实时终端交互 或 AI自动回复"""

    def __init__(self, name: str = "用户", bus=None, interactive: bool = False):
        super().__init__(name, "用户代理 - 人类交互", bus)
        self._auto_reply = "收到，继续推进。"
        self._interactive = interactive
        self._interaction_count = 0
        self._max_interactions = 3
        self._use_llm = False  # 如果设为True，调用DeepSeek生成用户回复
        self._llm_key = ""
        self._response_keywords = {
            "提问": "这个问题很好，请进一步分析",
            "确认": "好的，确认收到",
            "质疑": "这个结论的依据是什么？",
            "扩展": "请从另一个角度再分析",
        }
        logger.info(f"用户代理v2创建: {name}, 交互模式={interactive}")

    def set_auto_reply(self, reply: str) -> None:
        self._auto_reply = reply

    def enable_real_user(self, enabled: bool = True):
        """启用终端真实输入"""
        self._interactive = enabled

    def enable_llm_user(self, api_key: str = ""):
        """启用AI驱动用户（模拟真实用户行为）"""
        self._use_llm = True
        self._llm_key = api_key

    def _generate_llm_reply(self, message: str) -> str:
        """用AI生成拟人回复"""
        import json, urllib.request
        api_key = self._llm_key or __import__("os").environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            return False

        prompt = f"""你是模拟人类用户的AI。你在参与一个多Agent协作系统。
收到的消息: {message}

请以人类用户的身份回复。要求：
1. 保持真实感，像一个真实用户一样反馈
2. 如果你觉得结果满意就说"可以了"或"继续"
3. 如果有疑问就追问
4. 回复不超过30字"""

        req_body = {
            "model": "deepseek-chat",
            "messages": [{"role": "system", "content": "你模拟真实人类用户"}, {"role": "user", "content": prompt}],
            "temperature": 0.9,
            "max_tokens": 100,
        }
        try:
            req = urllib.request.Request(
                "https://api.deepseek.com/v1/chat/completions",
                data=json.dumps(req_body).encode("utf-8"),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except:
            return False

    def _generate_reply(self, message: str, sender: str) -> str:
        # 模式1: AI驱动用户
        if self._use_llm and self._interaction_count < self._max_interactions:
            llm_reply = self._generate_llm_reply(message)
            if llm_reply:
                self._interaction_count += 1
                return f"[{self.name}] {llm_reply}"

        # 模式2: 终端实时输入
        if self._interactive and self._interaction_count < self._max_interactions:
            print(f"\n>>> [{self.name}] 收到({sender}) - 请输入你的回复 (或回车使用自动回复):")
            try:
                user_input = input("  你的输入: ").strip()
                self._interaction_count += 1
                if user_input:
                    return f"[{self.name}] {user_input}"
            except (EOFError, KeyboardInterrupt):
                pass

        # 模式3: 智能自动回复（根据消息内容自适应）
        message_lower = message.lower()
        if any(w in message_lower for w in ["请确认", "确认收到", "是否正确", "同意吗"]):
            response = "确认收到，继续推进。"
        elif any(w in message_lower for w in ["问题", "疑问", "不确定", "追问"]):
            response = "好的，请进一步分析。"
        elif any(w in message_lower for w in ["完成", "结果", "总结", "最终"]):
            response = "收到结果，请继续。"
        else:
            response = self._auto_reply

        feedback = f"[{self.name}] {response}"
        logger.info(f"用户代理自动回复: {feedback[:50]}")
        return feedback
