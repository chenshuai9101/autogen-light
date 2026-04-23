"""助手智能体 v2 - 真实Function Calling + 工具调用"""

import logging, json, urllib.request, inspect, re
from ..core.agent_base import AgentBase

logger = logging.getLogger(__name__)


class AssistantAgent(AgentBase):
    """助手智能体 v2 - 原生Function Calling"""

    def __init__(self, name: str, system_message: str = "", bus=None, api_key: str = None):
        super().__init__(name, system_message or f"你是{name}，一个有帮助的AI助手", bus)
        self.tools: dict = {}
        self.tool_schemas: list = []
        self.api_key = api_key or ""
        self.model = "deepseek-chat"
        self.base_url = "https://api.deepseek.com/v1"
        self.conversation_history: list = []  # 对话历史管理
        self.max_history = 20
        logger.info(f"助手v2创建: {name}")

    def register_tool(self, name: str, func, description: str = ""):
        self.tools[name] = func
        # 自动推断参数schema
        sig = inspect.signature(func)
        params = {}
        required = []
        for p_name, p_param in sig.parameters.items():
            p_type = "string"
            if p_param.annotation is not inspect.Parameter.empty:
                if p_param.annotation in (int, float): p_type = "number"
                elif p_param.annotation == bool: p_type = "boolean"
            params[p_name] = {"type": p_type, "description": p_name}
            if p_param.default is inspect.Parameter.empty:
                required.append(p_name)

        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        self.tool_schemas.append({
            "type": "function",
            "function": {
                "name": safe_name,
                "description": (description or name)[:200],
                "parameters": {
                    "type": "object",
                    "properties": params if params else {"input": {"type": "string", "description": "输入"}},
                    "required": required if required else ["input"],
                },
            },
        })
        logger.info(f"  工具注册(Function Calling): {name}")

    def _call_tool(self, name: str, args: dict) -> str:
        func = self.tools.get(name)
        if not func:
            return f"工具不存在: {name}"
        try:
            return str(func(**args) if args else func())
        except TypeError:
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())
            try:
                if not params: return str(func())
                return str(func(next(iter(args.values())) if args else ""))
            except Exception as e:
                return f"工具失败: {e}"
        except Exception as e:
            return f"工具失败: {e}"

    def _call_llm(self, message: str, sender: str) -> str:
        """真实AI调用 + Function Calling"""

        # 管理对话历史：滑动窗口
        self.conversation_history.append({"role": "user", "content": f"来自{sender}: {message}"})
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

        messages = [{"role": "system", "content": self.config.system_message}]
        messages.extend(self.conversation_history)

        if not self.api_key:
            return f"[{self.name}] 错误: 未设置API Key"

        # 构建请求
        req_body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 256,
        }

        if self.tool_schemas:
            req_body["tools"] = self.tool_schemas
            req_body["tool_choice"] = "auto"

        try:
            req = urllib.request.Request(
                f"{self.base_url}/chat/completions",
                data=json.dumps(req_body).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            msg = data["choices"][0]["message"]
            content = msg.get("content", "")

            # 处理Function Calling
            if "tool_calls" in msg:
                results = []
                for tc in msg["tool_calls"]:
                    fn_name = tc["function"]["name"]
                    try:
                        fn_args = json.loads(tc["function"]["arguments"]) if tc["function"]["arguments"] else {}
                    except:
                        fn_args = {}

                    # 查找工具
                    actual_name = fn_name
                    for n in self.tools:
                        if re.sub(r'[^a-zA-Z0-9_]', '_', n) == fn_name:
                            actual_name = n
                            break

                    tool_result = self._call_tool(actual_name, fn_args)
                    results.append(f"[调用工具: {actual_name}] → {tool_result}")

                reply = "\n".join(results) if results else (content or "分析完毕")
            else:
                reply = content or "处理完毕"

            # 保存助手回复到历史
            self.conversation_history.append({"role": "assistant", "content": reply})
            if len(self.conversation_history) > self.max_history:
                self.conversation_history = self.conversation_history[-self.max_history:]

            return f"[{self.name}] {reply}"

        except Exception as e:
            return f"[{self.name}] 调用失败: {e}"

    def _generate_reply(self, message: str, sender: str) -> str:
        return self._call_llm(message, sender)

    def list_tools(self) -> dict:
        return {k: v.__name__ if hasattr(v, '__name__') else type(v).__name__ for k, v in self.tools.items()}
