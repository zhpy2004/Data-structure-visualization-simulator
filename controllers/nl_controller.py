#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
NLController

负责将自然语言请求转换为 DSL 文本，并可在需要时交由 DSLController 执行。
当前实现不直接操作视图，仅返回生成的 DSL，以便 AppController 统一路由和展示。
"""

from typing import Optional, Tuple

from services.llm_agent import LLMAgent


class NLController:
    def __init__(self, dsl_controller=None):
        self.dsl_controller = dsl_controller
        self.agent = LLMAgent()

    def to_dsl(self, nl_text: str, context_target: Optional[str] = None) -> Optional[str]:
        """将自然语言转换为 DSL 文本。失败返回 None。"""
        return self.agent.generate_dsl(nl_text, context_target=context_target)

    def handle_nl_command(self, nl_text: str, context_target: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """生成 DSL 并返回，执行留给上层。

        Returns:
            (ok, dsl_text) 其中 ok 表示转换成功，dsl_text 为生成的 DSL 或 None
        """
        dsl_text = self.to_dsl(nl_text, context_target=context_target)
        if not dsl_text:
            return False, None
        return True, dsl_text