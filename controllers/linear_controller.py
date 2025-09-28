#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
线性结构控制器 - 负责处理线性数据结构的操作
"""

from models.linear.array_list import ArrayList
from models.linear.linked_list import LinkedList
from models.linear.stack import Stack
from utils.dsl_parser import parse_linear_dsl


class LinearController:
    """线性结构控制器类，负责处理线性数据结构的操作"""
    
    def __init__(self, view):
        """初始化线性结构控制器
        
        Args:
            view: 线性结构视图对象
        """
        self.view = view
        self.current_structure = None
        self.structure_type = None
    
    def handle_action(self, action_type, params=None):
        """处理线性结构操作
        
        Args:
            action_type: 操作类型，如'create', 'insert', 'delete', 'push', 'pop', 'change_structure', 'clear'
            params: 操作参数
        """
        if action_type == 'create':
            structure_type = params.get('structure_type', params.get('type'))
            values = params.get('values', params.get('data', []))
            self._create_structure(structure_type, values)
        elif action_type == 'insert':
            position = params.get('position', params.get('index'))
            value = params.get('value')
            self._insert_element(position, value)
        elif action_type == 'delete' or action_type == 'remove':
            position = params.get('position', params.get('index'))
            self._delete_element(position)
        elif action_type == 'push':
            value = params.get('value')
            self._push_element(value)
        elif action_type == 'pop':
            self._pop_element()
        elif action_type == 'clear':
            self._clear_structure()
        elif action_type == 'change_structure':
            structure_type = params.get('structure_type')
            # 当切换数据结构类型时，清空当前结构并创建新的空结构
            self._create_structure(structure_type, [])
        else:
            self.view.show_message("错误", f"未知操作类型: {action_type}")
    
    def execute_dsl(self, command):
        """执行DSL命令
        
        Args:
            command: DSL命令字符串
        """
        try:
            action, params = parse_linear_dsl(command)
            self.handle_action(action, params)
        except Exception as e:
            self.view.show_message("错误", f"DSL命令执行错误: {str(e)}")
    
    def _create_structure(self, structure_type, initial_data=None):
        """创建线性结构
        
        Args:
            structure_type: 结构类型，'array_list', 'linked_list', 或 'stack'
            initial_data: 初始数据列表
        """
        if initial_data is None:
            initial_data = []
        
        self.structure_type = structure_type
        
        if structure_type == 'array_list':
            self.current_structure = ArrayList()
            for item in initial_data:
                self.current_structure.append(item)
        elif structure_type == 'linked_list':
            self.current_structure = LinkedList()
            for item in initial_data:
                self.current_structure.append(item)
        elif structure_type == 'stack':
            self.current_structure = Stack()
            for item in initial_data:
                self.current_structure.push(item)
        else:
            self.view.show_message("错误", f"未知结构类型: {structure_type}")
            return
        
        # 更新视图
        self._update_view()
    
    def _insert_element(self, index, value):
        """插入元素
        
        Args:
            index: 插入位置
            value: 插入值
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return
        
        if self.structure_type == 'stack':
            self.view.show_message("错误", "栈不支持插入操作，请使用入栈操作")
            return
        
        try:
            self.current_structure.insert(index, value)
            self._update_view()
        except Exception as e:
            self.view.show_message("错误", f"插入失败: {str(e)}")
    
    def _delete_element(self, index):
        """删除元素
        
        Args:
            index: 删除位置
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return
        
        if self.structure_type == 'stack':
            self.view.show_message("错误", "栈不支持删除操作，请使用出栈操作")
            return
        
        try:
            self.current_structure.delete(index)
            self._update_view()
        except Exception as e:
            self.view.show_message("错误", f"删除失败: {str(e)}")
    
    def _push_element(self, value):
        """入栈操作
        
        Args:
            value: 入栈值
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建栈结构")
            return
        
        if self.structure_type != 'stack':
            self.view.show_message("错误", "当前结构不是栈，不支持入栈操作")
            return
        
        try:
            self.current_structure.push(value)
            self._update_view()
        except Exception as e:
            self.view.show_message("错误", f"入栈失败: {str(e)}")
    
    def _pop_element(self):
        """出栈操作"""
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建栈结构")
            return
        
        if self.structure_type != 'stack':
            self.view.show_message("错误", "当前结构不是栈，不支持出栈操作")
            return
        
        try:
            value = self.current_structure.pop()
            self.view.show_message("出栈结果", f"出栈元素: {value}")
            self._update_view()
        except Exception as e:
            self.view.show_message("错误", f"出栈失败: {str(e)}")
    
    def _update_view(self):
        """更新视图显示"""
        if self.current_structure is None:
            return
        
        # 获取当前结构的可视化数据
        data = self.current_structure.get_visualization_data()
        
        # 确保数据包含结构类型
        if 'type' not in data:
            data['type'] = self.structure_type
        
        # 更新视图
        self.view.update_visualization(data)
        
    def _clear_structure(self):
        """清空当前数据结构"""
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return
        
        try:
            # 清空当前结构
            self.current_structure.clear()
            self._update_view()
            self.view.show_message("成功", "数据结构已清空")
        except Exception as e:
            self.view.show_message("错误", f"清空失败: {str(e)}")