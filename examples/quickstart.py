#!/usr/bin/env python3
"""
AutoGen Light 快速上手
=====================
使用方法:
  1. 设置API Key: export DEEPSEEK_API_KEY=your_key_here
  2. 运行: python3 quickstart.py

不需要理解框架概念，改Key就能跑。
"""

import os, sys

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "替换为你的Key")
if API_KEY == "替换为你的Key":
    print("⚠️  请先设置API Key")
    print("    export DEEPSEEK_API_KEY=sk-xxx")
    exit(1)

sys.path.insert(0, ".")
from autogen_light import AutoGenLight

print("=" * 50)
print("  AutoGen Light v2.0 - 快速上手")
print("=" * 50)

# ===== 示例1：2个Agent对话 =====
print("\n📝 示例1: 2个Agent聊一个话题")
ag1 = AutoGenLight()

助手A = ag1.create_assistant("乐观派", "你总是看到事情好的一面，回答不超过15字")
助手A.api_key = API_KEY

助手B = ag1.create_assistant("务实派", "你总是关注潜在风险，回答不超过15字")
助手B.api_key = API_KEY

g1 = ag1.create_group_chat([助手A, 助手B], max_round=3)
r1 = g1.run("讨论：AI会给人类带来什么")

for m in r1["conversation"]:
    if m["speaker"] not in ("system",):
        print(f'  [{m["round"]}] {m["speaker"]}: {m["content"][:60]}')

print(f"  共{r1['rounds']}轮, {len(r1['conversation'])}条消息")

# ===== 示例2：带工具的Agent =====
print("\n🔧 示例2: Agent使用工具搜索+分析")
ag2 = AutoGenLight()

研究员 = ag2.create_assistant("研究员", "你负责搜索和分析信息，回答不超过20字")
研究员.api_key = API_KEY
研究员.register_tool("search_news", lambda q: f"【新闻】{q}最新动态", "搜索新闻")

分析师 = ag2.create_assistant("分析师", "你负责总结分析，回答不超过20字")
分析师.api_key = API_KEY

g2 = ag2.create_group_chat([研究员, 分析师], max_round=2)
r2 = g2.run("分析2025年AI行业趋势")

for m in r2["conversation"]:
    if m["speaker"] not in ("system",):
        print(f'  [{m["round"]}] {m["speaker"]}: {m["content"][:60]}')

# ===== 示例3：AutoGen AutoReply =====
print("\n👥 示例3: 4人产品开发团队")
ag3 = AutoGenLight()

pm = ag3.create_assistant("产品经理", "你负责提需求，不超过15字")
pm.api_key = API_KEY
dev = ag3.create_assistant("开发者", "你负责技术方案，不超过15字")
dev.api_key = API_KEY
tester = ag3.create_assistant("测试", "你负责验证，不超过15字")
tester.api_key = API_KEY

g3 = ag3.create_group_chat([pm, dev, tester], max_round=2)
r3 = g3.run("设计一个登录功能")

for m in r3["conversation"]:
    if m["speaker"] not in ("system",):
        print(f'  [{m["round"]}] {m["speaker"]}: {m["content"][:60]}')

# ===== 示例4：AI驱动的用户 =====
print("\n🤖 示例4: AI驱动的用户交互")
ag4 = AutoGenLight()

专家 = ag4.create_assistant("AI专家", "你回答用户问题，不超过20字")
专家.api_key = API_KEY
用户 = ag4.create_user_proxy("用户")
用户._use_llm = True  # AI模拟真实用户

g4 = ag4.create_group_chat([用户, 专家], max_round=2)
r4 = g4.run("帮我推荐一个好的学习AI的路径")

for m in r4["conversation"]:
    if m["speaker"] not in ("system",):
        print(f'  [{m["round"]}] {m["speaker"]}: {m["content"][:60]}')

# ===== 汇总 =====
print("\n" + "=" * 50)
info = ag1.get_info()
print(f"  AutoGen Light v{info['version']}")
print("  全部示例通过 ✅")
print("  开始构建你的多Agent团队吧！")
print("=" * 50)
