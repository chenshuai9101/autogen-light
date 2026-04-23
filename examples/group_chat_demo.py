"""群组聊天演示"""

import sys
sys.path.insert(0, "/tmp/autogen-light")

from autogen_light import AutoGenLight

# 1. 创建框架
ag = AutoGenLight()
print("=" * 50)

# 2. 创建智能体
researcher = ag.create_assistant("研究员", "你是研究员，负责分析问题")
analyst = ag.create_assistant("分析师", "你是分析师，负责数据分析")
writer = ag.create_assistant("写手", "你是写手，负责生成报告")
manager = ag.create_user_proxy("经理")

# 3. 为研究员注册工具
def search_topic(query):
    return f"【搜索结果】关于'{query}'找到15条相关分析"

researcher.register_tool("搜索", search_topic)

# 4. 创建群组
group = ag.create_group_chat(
    [researcher, analyst, writer, manager],
    max_round=6
)

# 5. 运行
print(f"\n🚀 开始群组协作...")
result = group.run("分析AI行业趋势并生成报告")

print(f"\n📊 结果:")
print(f"  任务: {result['task']}")
print(f"  对话轮次: {result['rounds']}")
print(f"  参与智能体: {', '.join(result['agents'])}")
print(f"\n💬 对话记录:")
for msg in result['conversation']:
    print(f"  [{msg['speaker']}]: {msg['content'][:60]}")

print(f"\n📝 总结: {result['summary']}")
print("=" * 50)
print("✅ AutoGen Light 运行成功!")
