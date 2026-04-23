"""快速开始"""

from autogen_light import AutoGenLight

ag = AutoGenLight()
researcher = ag.create_assistant("研究员", "你负责研究")
reviewer = ag.create_assistant("审查员", "你负责审查")
user = ag.create_user_proxy("用户")

group = ag.create_group_chat([researcher, reviewer, user], max_round=4)
result = group.run("市场调研任务")
print(f"完成: {result['summary']}")
