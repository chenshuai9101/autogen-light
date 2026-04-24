---
name: autogen-light
description: 轻量级多智能体协作框架 - 3行定义Agent，5行跑起群组协作。不是AutoGen替代品，而是快速体验多Agent协作的最短路径。
metadata:
  openclaw:
    emoji: 🤖
    aiFriendly: true
    plugAndPlay: true
    requires:
      minimal: true
      packages: ['python>=3.8']
    category: agent-framework
    tags: ['autogen', 'multi-agent', 'collaboration', 'lightweight', 'framework']
version: '2.0.0'
---

# AutoGen Light 🤖

## 一、概述

AutoGen Light 不是AutoGen的完整替代品，而是**快速体验多Agent协作的最短路径**。3行定义Agent，5行跑起群组协作。

### 适用场景
- ✅ 快速构建多Agent协作
- ✅ 辩论/讨论式AI应用
- ✅ 带工具的群组Agent
- ✅ 教学/演示多Agent概念

### 不适用场景
- ❌ 需要AutoGen完整生态插件
- ❌ 分布式高可用Agent集群
- ❌ 企业级生产部署

## 二、安装

```bash
pip install autogen-light
# 或使用源码
git clone https://github.com/chenshuai9101/autogen-light
cd autogen-light
pip install -e .
```

## 三、快速开始

```python
from autogen_light import AutoGenLight

ag = AutoGenLight()

# 2个Agent隔空辩论
辩论家A = ag.create_assistant("辩论家A", "你支持'技术进步应该开放'")
辩论家B = ag.create_assistant("辩论家B", "你支持'技术进步应该谨慎'")

group = ag.create_group_chat([辩论家A, 辩论家B], max_round=3)
result = group.run("讨论：AI是否应该开源")
print(result["summary"])
```

## 四、结构化输出

```json
{
  "operation": "group_chat|agent_task|parallel_exec",
  "agents": [{"name": "", "system_prompt": ""}],
  "task": "任务描述",
  "options": {
    "max_round": 3,
    "model": "deepseek-chat",
    "retry_on_fail": true
  }
}
```

## 五、边界声明

### NOT FOR
- 需要AutoGen完整生态插件的复杂场景
- 分布式高可用Agent集群
- 单一Agent即可完成的任务（使用langchain-light更简单）

### 触发词
- 用户需要多个AI协作完成任务时
- 用户提及"多Agent""群组""团队协作"时

## 安装与兼容性

### 支持的平台
- ✅ **Claude Code** (v0.7.0+) - 作为Python库调用
- ✅ **OpenClaw** (v1.0.0+) - 通过skill机制加载
- ✅ **Codex CLI** (latest)
- ✅ **Cursor** (latest)
- 🟡 **纯命令行** - pip install 直接使用

### 安装方式

```bash
# Python包方式
pip install autogen-light

# Claude Code方式
claude mcp add chenshuai9101/autogen-light

# OpenClaw方式
clawhub install chenshuai9101/autogen-light
```
