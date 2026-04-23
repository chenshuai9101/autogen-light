"""代码审查工作流"""

from .. import AutoGenLight


def create_code_review_workflow():
    """创建代码审查工作流"""
    ag = AutoGenLight()
    coder = ag.create_assistant("程序员", "你是一个资深程序员，负责编写代码。")
    reviewer = ag.create_assistant("审查员", "你是一个严谨的代码审查员，负责审查代码质量。")
    tester = ag.create_assistant("测试员", "你是一个专业的测试员，负责测试代码功能。")
    manager = ag.create_user_proxy("项目经理")
    return ag
