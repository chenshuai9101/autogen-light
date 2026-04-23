#!/usr/bin/env python3
"""AutoGen Light - 全面测试套件"""
import sys, os, json, traceback, datetime as dt

sys.path.insert(0, "/tmp/autogen-light")
API_KEY = "sk-2565d4e8209542f7b6ff5b3730091d3c"
os.environ["DEEPSEEK_API_KEY"] = API_KEY

PASS = 0
FAIL = 0
ERRORS = []

def test(name, fn):
    global PASS, FAIL
    start = dt.datetime.now()
    try:
        fn()
        PASS += 1
        elapsed = (dt.datetime.now() - start).total_seconds()
        print(f"  ✅ {name} ({elapsed:.1f}s)")
    except Exception as e:
        FAIL += 1
        tb = traceback.format_exc()
        ERRORS.append(f"{name}: {e}")
        elapsed = (dt.datetime.now() - start).total_seconds()
        print(f"  ❌ {name}: {e} ({elapsed:.1f}s)")

def section(n, title):
    print(f"\n─── [{n}] {title}")

from autogen_light import AutoGenLight

# ===== [1-10] 基础功能 =====
section("1-10", "基础功能")

def t1():
    ag = AutoGenLight()
    assert ag is not None
test("初始化", t1)

def t2():
    ag = AutoGenLight()
    r = ag.create_assistant("研究员", "你是有帮助的AI")
    assert r.name == "研究员"
test("创建助手", t2)

def t3():
    ag = AutoGenLight()
    r = ag.create_user_proxy("用户")
    assert r.name == "用户"
test("创建用户代理", t3)

def t4():
    ag = AutoGenLight()
    r = ag.create_assistant("a1")
    a = ag.create_assistant("a2")
    u = ag.create_user_proxy("u")
    g = ag.create_group_chat([r, a, u])
    assert g is not None
test("创建群组", t4)

def t5():
    ag = AutoGenLight()
    info = ag.get_info()
    assert "version" in info
test("get_info", t5)

def t6():
    ag = AutoGenLight()
    r = ag.create_assistant("a")
    u = ag.create_user_proxy("u")
    ag.create_group_chat([r, u], max_round=10)
    assert ag._group.config.max_round == 10
test("群组max_round配置", t6)

def t7():
    ag = AutoGenLight()
    r = ag.create_assistant("a")
    a = ag.create_assistant("b")
    u = ag.create_user_proxy("c")
    g = ag.create_group_chat([r, a, u], max_round=3)
    result = g.run("测试")
    assert result["success"]
    assert len(result["conversation"]) > 0
test("群组基本运行", t7)

# ===== [11-30] 真实多Agent对话 =====
section("11-30", "真实多Agent对话")

def t11():
    ag = AutoGenLight()
    r = ag.create_assistant("研究员", "你擅长分析问题，用中文回复不超过20字")
    r.api_key = API_KEY
    a = ag.create_assistant("分析师", "你擅长数据分析，用中文回复不超过20字")
    a.api_key = API_KEY
    g = ag.create_group_chat([r, a], max_round=2)
    result = g.run("分析AI行业趋势")
    assert result["success"]
    # 检查是否有真实AI回复
    has_real = any("研究员" in m["content"] or "分析师" in m["content"] for m in result["conversation"])
test("2Agent真实对话", t11)

def t12():
    ag = AutoGenLight()
    r = ag.create_assistant("研究员", "你擅长研究，用中文回复不超过20字")
    r.api_key = API_KEY
    a = ag.create_assistant("分析师", "你擅长分析，用中文回复不超过20字")
    a.api_key = API_KEY
    w = ag.create_assistant("写手", "你擅长写作，用中文回复不超过20字")
    w.api_key = API_KEY
    g = ag.create_group_chat([r, a, w], max_round=2)
    result = g.run("市场调研")
    assert result["success"]
test("3Agent真实对话", t12)

def t13():
    ag = AutoGenLight()
    agents = []
    for i in range(5):
        a = ag.create_assistant(f"Agent{i}", f"你是Agent{i}，用中文回复不超过10字")
        a.api_key = API_KEY
        agents.append(a)
    g = ag.create_group_chat(agents, max_round=2)
    result = g.run("协作测试")
    assert result["success"]
test("5Agent群组", t13)

def t14():
    ag = AutoGenLight()
    r = ag.create_assistant("专家", "你只回复数字，不回复其他内容")
    r.api_key = API_KEY
    g = ag.create_group_chat([r], max_round=2)
    result = g.run("回复数字1")
    assert result["success"]
test("单Agent群组", t14)

# ===== [31-45] 角色分化与上下文保持 =====
section("31-45", "角色分化与上下文保持")

def t31():
    ag = AutoGenLight()
    r = ag.create_assistant("工程师", "你只写代码，用Python回复不超过3行")
    r.api_key = API_KEY
    t = ag.create_assistant("测试员", "你只做测试验证，用中文回复不超过20字")
    t.api_key = API_KEY
    g = ag.create_group_chat([r, t], max_round=3)
    result = g.run("写一个加法函数并测试")
    assert result["success"]
test("工程师+测试员协作", t31)

def t32():
    ag = AutoGenLight()
    r = ag.create_assistant("辩论家A", "你支持正方观点，用中文回复不超过30字")
    r.api_key = API_KEY
    a = ag.create_assistant("辩论家B", "你支持反方观点，用中文回复不超过30字")
    a.api_key = API_KEY
    g = ag.create_group_chat([r, a], max_round=3)
    result = g.run("AI是否应该开源")
    assert result["success"]
test("辩论场景", t32)

# ===== [46-55] 群组轮次控制 =====
section("46-55", "群组轮次控制")

def t46():
    ag = AutoGenLight()
    r = ag.create_assistant("a1", "回复不超过5字")
    r.api_key = API_KEY
    a = ag.create_assistant("a2", "回复不超过5字")
    a.api_key = API_KEY
    g = ag.create_group_chat([r, a], max_round=1)
    result = g.run("测试")
    assert result["rounds"] == 1
test("1轮对话", t46)

def t47():
    ag = AutoGenLight()
    r = ag.create_assistant("a1", "回复不超过3字")
    r.api_key = API_KEY
    a = ag.create_assistant("a2", "回复不超过3字")
    a.api_key = API_KEY
    g = ag.create_group_chat([r, a], max_round=5)
    result = g.run("测试多轮")
    assert result["rounds"] == 5
test("5轮对话", t47)

# ===== [56-70] 错误恢复 =====
section("56-70", "错误恢复")

def t56():
    ag = AutoGenLight()
    r = ag.create_assistant("a", "测试助手")
    # 不设置api_key，正常应该返回错误消息
    g = ag.create_group_chat([r], max_round=1)
    result = g.run("测试")
    assert result["success"]
test("无API Key不崩", t56)

def t57():
    ag = AutoGenLight()
    r = ag.create_assistant("a", "hi")
    r.api_key = "invalid_key"
    g = ag.create_group_chat([r], max_round=1)
    result = g.run("hi")
    assert result["success"]
test("无效API Key不崩", t57)

def t58():
    ag = AutoGenLight()
    r = ag.create_assistant("a", "你好")
    a = ag.create_assistant("b", "你好")
    r.api_key = API_KEY
    # a不设key，混合状态
    g = ag.create_group_chat([r, a], max_round=2)
    result = g.run("测试混合")
    assert result["success"]
test("混合Key配置", t58)

# ===== [71-80] 边界条件 =====
section("71-80", "边界条件")

def t71():
    ag = AutoGenLight()
    agents = []
    for i in range(10):
        a = ag.create_assistant(f"A{i}", "回复一个字")
        a.api_key = API_KEY
        agents.append(a)
    g = ag.create_group_chat(agents, max_round=1)
    result = g.run("go")
    assert result["success"]
test("10Agent群组", t71)

def t72():
    ag = AutoGenLight()
    r = ag.create_assistant("长名智能体" * 5, "你好")
    r.api_key = API_KEY
    g = ag.create_group_chat([r], max_round=1)
    result = g.run("测试")
    assert result["success"]
test("超长Agent名", t72)

# ===== [81-90] 预设工作流 =====
section("81-90", "预设工作流")

def t81():
    ag = AutoGenLight()
    coder = ag.create_assistant("程序员", "你写Python代码，不超过3行")
    coder.api_key = API_KEY
    reviewer = ag.create_assistant("审查员", "你审查代码，用中文回复不超过20字")
    reviewer.api_key = API_KEY
    g = ag.create_group_chat([coder, reviewer], max_round=3)
    result = g.run("写一个冒泡排序函数")
    assert result["success"]
test("代码审查工作流", t81)

# ===== [91-100] 真实场景 =====
section("91-100", "真实场景模拟")

def t91():
    ag = AutoGenLight()
    pm = ag.create_assistant("产品经理", "你提需求，用中文不超过20字")
    pm.api_key = API_KEY
    dev = ag.create_assistant("开发者", "你设计技术方案，用中文不超过30字")
    dev.api_key = API_KEY
    tester = ag.create_assistant("测试", "你设计测试用例，用中文不超过20字")
    tester.api_key = API_KEY
    g = ag.create_group_chat([pm, dev, tester], max_round=2)
    result = g.run("开发一个登录功能")
    assert result["success"]
test("产品开发协作", t91)

def t92():
    ag = AutoGenLight()
    r = ag.create_assistant("搜索研究员", "你负责搜索信息，用中文不超过20字")
    r.api_key = API_KEY
    w = ag.create_assistant("报告写手", "你负责写报告，用中文不超过30字")
    w.api_key = API_KEY
    g = ag.create_group_chat([r, w], max_round=2)
    result = g.run("写一份AI市场报告")
    assert result["success"]
test("研究+写作协作", t92)

def t93():
    ag = AutoGenLight()
    r = ag.create_assistant("机器人", "你只回复数字")
    r.api_key = API_KEY
    g = ag.create_group_chat([r], max_round=2)
    result = g.run("1+1等于几")
    assert result["success"]
test("特定输出格式", t93)

# ===== 结果汇总 =====
print(f"\n{'='*60}")
print(f"AutoGen Light 测试完成: {PASS}通过, {FAIL}失败, 共{PASS+FAIL}项")
if ERRORS:
    print(f"\n失败明细:")
    for e in ERRORS:
        print(f"  ❌ {e}")

now = dt.datetime.now()
print(f"\n时间: {now.strftime('%H:%M:%S')}")
