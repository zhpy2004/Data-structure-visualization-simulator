#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
栈实现 - 基于数组的后进先出(LIFO)数据结构
"""


class Stack:
    """栈类，基于数组实现的后进先出(LIFO)数据结构"""
    
    def __init__(self, capacity=10):
        """初始化栈
        
        Args:
            capacity: 初始容量，默认为10
        """
        self.capacity = capacity
        self.data = [None] * capacity
        self.top = -1  # 栈顶指针，-1表示空栈
        
    def to_list(self):
        """将栈转换为列表
        
        Returns:
            list: 包含栈中所有元素的列表（从栈底到栈顶）
        """
        if self.is_empty():
            return []
        return [self.data[i] for i in range(self.top + 1)]
    
    def is_empty(self):
        """判断栈是否为空
        
        Returns:
            bool: 如果栈为空返回True，否则返回False
        """
        return self.top == -1
    
    def is_full(self):
        """判断栈是否已满
        
        Returns:
            bool: 如果栈已满返回True，否则返回False
        """
        return self.top == self.capacity - 1
    
    def _resize(self, new_capacity):
        """调整栈容量
        
        Args:
            new_capacity: 新的容量大小
        """
        new_data = [None] * new_capacity
        for i in range(self.top + 1):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity
    
    def push(self, value):
        """入栈操作
        
        Args:
            value: 入栈的元素值
        """
        # 如果栈已满，扩容
        if self.is_full():
            self._resize(self.capacity * 2)
        
        # 栈顶指针加1，并存入新元素
        self.top += 1
        self.data[self.top] = value
    
    def pop(self):
        """出栈操作
        
        Returns:
            栈顶元素值
            
        Raises:
            IndexError: 如果栈为空
        """
        if self.is_empty():
            raise IndexError("栈为空")
        
        # 取出栈顶元素
        value = self.data[self.top]
        
        # 清空栈顶元素并减小栈顶指针
        self.data[self.top] = None
        self.top -= 1
        
        # 如果元素数量减少到容量的1/4，缩小容量
        if self.top >= 0 and self.top < self.capacity // 4:
            self._resize(self.capacity // 2)
        
        return value
    
    def peek(self):
        """查看栈顶元素但不移除
        
        Returns:
            栈顶元素值
            
        Raises:
            IndexError: 如果栈为空
        """
        if self.is_empty():
            raise IndexError("栈为空")
        
        return self.data[self.top]
    
    def size(self):
        """返回栈中元素个数
        
        Returns:
            int: 栈中元素个数
        """
        return self.top + 1
    
    def clear(self):
        """清空栈"""
        self.data = [None] * self.capacity
        self.top = -1
    
    def __len__(self):
        """返回栈长度"""
        return self.top + 1
    
    def __str__(self):
        """返回栈的字符串表示"""
        return str([self.data[i] for i in range(self.top + 1)])
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        return {
            'type': 'stack',
            'data': [self.data[i] for i in range(self.top + 1)],
            'capacity': self.capacity,
            'top': self.top
        }