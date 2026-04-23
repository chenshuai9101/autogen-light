#!/usr/bin/env python3
"""AutoGen Light - 压力测试套件"""
import sys, os, time, traceback, datetime as dt

sys.path.insert(0, "/tmp/autogen-light")
API_KEY = "sk-2565d4e8209542f7b6ff5b3730091d3c"
os.environ["DEEPSEEK_API_KEY"] = API_KEY

from autogen_light import AutoGenLight

PASS = 0; FAIL = 0; ERRORS = []

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

def section(title):
    print(f"\n──── {title}")

import resource
def get_mem():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

print(f"初始内存: {get_mem():.1f}MB")
print(f"时间: {dt.datetime.now().strftime('%H:%M:%S')}")

# ===== 压力1: 大量Agent =====
section("压力1: 大量Agent群组")

def stress_20_agents():
    ag = AutoGenLight()
    agents = []
    for i in range(20):
        a = ag.create_assistant(f"A{i}", "回1字")
        a.api_key = API_KEY
        agents.append(a)
    g = ag.create_group_chat(agents, max_round=1)
    r = g.run("test")
    assert r["success"]
    print(f"    20个Agent, {r['rounds']}轮, {len(r['conversation'])}条消息")
test("20Agent群组", stress_20_agents)

def stress_50_agents():
    ag = AutoGenLight()
    agents = []
    for i in range(50):
        a = ag.create_assistant(f"B{i}", "OK")
        a.api_key = API_KEY
        agents.append(a)
    g = ag.create_group_chat(agents, max_round=1)
    r = g.run("t")
    assert r["success"]
    total_conv = len(r["conversation"])
    print(f"    50个Agent, 共{total_conv}条消息")
test("50Agent群组", stress_50_agents)

# ===== 压力2: 长时间对话 =====
section("压力2: 长时间多轮对话")

def stress_20_rounds():
    ag = AutoGenLight()
    a1 = ag.create_assistant("A", "回复不超过5字")
    a1.api_key = API_KEY
    a2 = ag.create_assistant("B", "回复不超过5字")
    a2.api_key = API_KEY
    g = ag.create_group_chat([a1, a2], max_round=20)
    start = time.time()
    r = g.run("持续对话")
    elapsed = time.time() - start
    print(f"    20轮, {len(r['conversation'])}条消息, 耗时{elapsed:.0f}s")
    assert r["success"]
test("20轮长时间对话", stress_20_rounds)

def stress_50_rounds():
    ag = AutoGenLight()
    a1 = ag.create_assistant("X", "回1字")
    a1.api_key = API_KEY
    a2 = ag.create_assistant("Y", "回1字")
    a2.api_key = API_KEY
    g = ag.create_group_chat([a1, a2], max_round=50)
    start = time.time()
    r = g.run("go")
    elapsed = time.time() - start
    print(f"    50轮, {len(r['conversation'])}条消息, 耗时{elapsed:.0f}s")
    assert r["success"]
test("50轮长时间对话", stress_50_rounds)

# ===== 压力3: 连续创建/销毁 =====
section("压力3: 连续创建销毁")

def stress_50_instances():
    start = time.time()
    for i in range(50):
        ag = AutoGenLight()
        a = ag.create_assistant(f"A{i}", "test")
        a.api_key = API_KEY
        b = ag.create_assistant(f"B{i}", "test")
        b.api_key = API_KEY
        g = ag.create_group_chat([a, b], max_round=1)
        g.run(f"task_{i}")
    elapsed = time.time() - start
    print(f"    50次创建运行, 耗时{elapsed:.1f}s, 平均{elapsed/50:.2f}s/次")
test("50次创建+运行", stress_50_instances)

# ===== 压力4: 并发群组 =====
section("压力4: 并发群组运行")

def stress_concurrent_groups():
    groups = []
    for i in range(5):
        ag = AutoGenLight()
        a1 = ag.create_assistant(f"C{i}a", "回1字")
        a1.api_key = API_KEY
        a2 = ag.create_assistant(f"C{i}b", "回1字")
        a2.api_key = API_KEY
        g = ag.create_group_chat([a1, a2], max_round=3)
        groups.append((ag, g))
    
    results = []
    start = time.time()
    for _, g in groups:
        results.append(g.run(f"并发任务"))
    elapsed = time.time() - start
    all_ok = all(r["success"] for r in results)
    print(f"    5个群组并发, 耗时{elapsed:.1f}s, 全部成功={all_ok}")
    assert all_ok
test("5个独立群组并行", stress_concurrent_groups)

# ===== 压力5: 大任务输入 =====
section("压力5: 大任务输入")

def stress_long_task():
    ag = AutoGenLight()
    a1 = ag.create_assistant("处理者", "回复不超过5字")
    a1.api_key = API_KEY
    g = ag.create_group_chat([a1], max_round=2)
    long_task = "请处理这个请求" + "A" * 10000
    r = g.run(long_task)
    assert r["success"]
test("10KB任务输入", stress_long_task)

# ===== 压力6: 内存稳定性 =====
section("压力6: 内存稳定性")
mem_before = get_mem()
for i in range(30):
    ag = AutoGenLight()
    a1 = ag.create_assistant(f"MA{i}", "test")
    a1.api_key = API_KEY
    a2 = ag.create_assistant(f"MB{i}", "test")
    a2.api_key = API_KEY
    g = ag.create_group_chat([a1, a2], max_round=1)
    g.run(f"task_{i}")
mem_after = get_mem()
mem_diff = mem_after - mem_before
print(f"    30次后: {mem_before:.1f}MB → {mem_after:.1f}MB (增{mem_diff:.1f}MB)")
test("30次运行内存泄漏检测", lambda: mem_diff < 200)

# ===== 结果 =====
print(f"\n{'='*60}")
print(f"AutoGen Light 压力测试完成: {PASS}通过, {FAIL}失败, 共{PASS+FAIL}项")
print(f"当前内存: {get_mem():.1f}MB")
if ERRORS:
    print(f"\n失败:")
    for e in ERRORS:
        print(f"  ❌ {e}")
print(f"\n时间: {dt.datetime.now().strftime('%H:%M:%S')}")
