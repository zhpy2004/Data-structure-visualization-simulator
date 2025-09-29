#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用控制器 - 负责协调模型和视图之间的交互
"""

import json
import pickle
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
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
        
        # 连接保存和加载信号
        self.main_window.save_structure_requested.connect(self.save_structure)
        self.main_window.load_structure_requested.connect(self.load_structure)
        
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
        
    def save_structure(self):
        """保存当前数据结构到文件"""
        # 获取当前选项卡索引
        current_tab = self.main_window.tab_widget.currentIndex()
        
        # 准备要保存的数据
        data = {
            'tab_index': current_tab,
            'data': None
        }
        
        # 根据当前选项卡获取相应的数据
        if current_tab == 0:  # 线性结构
            structure_type = self.linear_controller.structure_type
            structure_data = self.linear_controller.get_structure_data()
            data['data'] = {
                'type': structure_type,
                'content': structure_data
            }
        elif current_tab == 1:  # 树形结构
            structure_type = self.tree_controller.structure_type
            structure_data = self.tree_controller.get_structure_data()
            data['data'] = {
                'type': structure_type,
                'content': structure_data
            }
        
        # 如果没有数据可保存
        if not data['data']:
            QMessageBox.warning(self.main_window, "保存失败", "当前没有可保存的数据结构")
            return
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "保存数据结构",
            "",
            "数据结构文件 (*.dsv);;所有文件 (*)"
        )
        
        if not file_path:
            return  # 用户取消了保存
        
        # 确保文件扩展名为.dsv
        if not file_path.endswith('.dsv'):
            file_path += '.dsv'
        
        try:
            # 保存数据到文件
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            QMessageBox.information(self.main_window, "保存成功", f"数据结构已保存到: {file_path}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "保存失败", f"保存数据时出错: {str(e)}")
    
    def load_structure(self):
        """从文件加载数据结构"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "加载数据结构",
            "",
            "数据结构文件 (*.dsv);;所有文件 (*)"
        )
        
        if not file_path:
            return  # 用户取消了加载
        
        try:
            # 从文件加载数据
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 切换到相应的选项卡
            tab_index = data.get('tab_index', 0)
            self.main_window.tab_widget.setCurrentIndex(tab_index)
            
            # 加载数据到相应的结构
            structure_data = data.get('data')
            if not structure_data:
                raise ValueError("文件中没有有效的数据结构")
            
            structure_type = structure_data.get('type')
            content = structure_data.get('content')
            
            print(f"加载数据: tab_index={tab_index}, structure_type={structure_type}, content={content}")
            
            if tab_index == 0:  # 线性结构
                # 设置当前结构类型
                self.linear_controller.structure_type = structure_type
                self.linear_controller.load_structure(structure_type, content)
            elif tab_index == 1:  # 树形结构
                # 设置当前结构类型
                self.tree_controller.structure_type = structure_type
                self.tree_controller.load_structure(structure_type, content)
            
            QMessageBox.information(self.main_window, "加载成功", f"数据结构已从文件加载: {file_path}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "加载失败", f"加载数据时出错: {str(e)}")