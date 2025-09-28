#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用控制器 - 负责协调模型和视图之间的交互
"""

from PyQt5.QtWidgets import QMainWindow, QMessageBox
from views.main_window import MainWindow
from controllers.linear_controller import LinearController
from controllers.tree_controller import TreeController
from controllers.dsl_controller import DSLController


class AppController:
    """应用控制器类，负责协调整个应用程序的运行"""
    
    def __init__(self):
        """初始化应用控制器"""
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 创建子控制器
        self.linear_controller = LinearController(self.main_window.linear_view)
        self.tree_controller = TreeController(self.main_window.tree_view)
        self.dsl_controller = DSLController(self.linear_controller, self.tree_controller)
        
        # 连接信号和槽
        self._connect_signals()
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接主窗口的信号到控制器的槽函数
        self.main_window.linear_action_triggered.connect(self._handle_linear_action)
        self.main_window.tree_action_triggered.connect(self._handle_tree_action)
        self.main_window.dsl_executed.connect(self._handle_dsl_command)
        
        # 连接DSL控制器的信号
        self.dsl_controller.command_result.connect(self._handle_dsl_result)
    
    def _handle_linear_action(self, action_type, params):
        """处理线性结构操作"""
        self.linear_controller.handle_action(action_type, params)
    
    def _handle_tree_action(self, action_type, params):
        """处理树形结构操作"""
        self.tree_controller.handle_action(action_type, params)
    
    def _handle_dsl_command(self, command):
        """处理DSL命令"""
        # 使用DSL控制器处理命令
        result = self.dsl_controller.process_command(command)
        
        # 如果处理失败，在DSL输出区域显示错误信息
        if not result:
            # 错误信息已通过信号传递，不需要在这里处理
            pass
    
    def _handle_dsl_result(self, result_type, result_data):
        """处理DSL命令结果
        
        Args:
            result_type: 结果类型（success/error）
            result_data: 结果数据
        """
        if result_type == "error":
            error_message = result_data.get("message", "未知错误")
            # 在DSL输出区域显示错误信息
            self.main_window.dsl_output.append(f"错误: {error_message}")
            # 显示错误弹窗
            QMessageBox.warning(self.main_window, "DSL解析错误", error_message)
        else:
            # 处理成功结果
            message = result_data.get("message", "")
            if message:
                self.main_window.dsl_output.append(f"成功: {message}")
    
    def show_main_window(self):
        """显示主窗口"""
        self.main_window.show()