#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
顺序表实现 - 基于数组的线性表
"""


class ArrayList:
    """顺序表类，基于数组实现的线性表"""
    
    def __init__(self, capacity=10):
        """初始化顺序表
        
        Args:
            capacity: 初始容量，默认为10
        """
        self.capacity = capacity
        self.size = 0
        self.data = [None] * capacity
    
    def is_empty(self):
        """判断顺序表是否为空
        
        Returns:
            bool: 如果顺序表为空返回True，否则返回False
        """
        return self.size == 0
    
    def is_full(self):
        """判断顺序表是否已满
        
        Returns:
            bool: 如果顺序表已满返回True，否则返回False
        """
        return self.size == self.capacity
    
    def _resize(self, new_capacity):
        """调整顺序表容量
        
        Args:
            new_capacity: 新的容量大小
        """
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity
    
    def get(self, index):
        """获取指定位置的元素
        
        Args:
            index: 元素位置，从0开始
            
        Returns:
            元素值
            
        Raises:
            IndexError: 如果索引越界
        """
        if index < 0 or index >= self.size:
            raise IndexError("索引越界")
        return self.data[index]
    
    def set(self, index, value):
        """设置指定位置的元素值
        
        Args:
            index: 元素位置，从0开始
            value: 新的元素值
            
        Raises:
            IndexError: 如果索引越界
        """
        if index < 0 or index >= self.size:
            raise IndexError("索引越界")
        self.data[index] = value
    
    def insert(self, index, value):
        """在指定位置插入元素
        
        Args:
            index: 插入位置，从0开始
            value: 插入的元素值
            
        Raises:
            IndexError: 如果索引越界
        """
        if index < 0 or index > self.size:
            raise IndexError("索引越界")
        
        # 如果顺序表已满，扩容
        if self.is_full():
            self._resize(self.capacity * 2)
        
        # 将插入位置及之后的元素后移一位
        for i in range(self.size, index, -1):
            self.data[i] = self.data[i - 1]
        
        # 在指定位置插入新元素
        self.data[index] = value
        self.size += 1
    
    def append(self, value):
        """在顺序表末尾添加元素
        
        Args:
            value: 添加的元素值
        """
        self.insert(self.size, value)
    
    def delete(self, index):
        """删除指定位置的元素
        
        Args:
            index: 删除位置，从0开始
            
        Returns:
            被删除的元素值
            
        Raises:
            IndexError: 如果索引越界
        """
        if index < 0 or index >= self.size:
            raise IndexError("索引越界")
        
        # 保存要删除的元素
        removed_value = self.data[index]
        
        # 将删除位置之后的元素前移一位
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i + 1]
        
        # 清空最后一个元素并减小size
        self.data[self.size - 1] = None
        self.size -= 1
        
        return removed_value
    
    def index_of(self, value):
        """查找元素在顺序表中的位置
        
        Args:
            value: 要查找的元素值
            
        Returns:
            int: 元素在顺序表中的位置，如果不存在返回-1
        """
        for i in range(self.size):
            if self.data[i] == value:
                return i
        return -1
    
    def clear(self):
        """清空顺序表"""
        self.data = [None] * self.capacity
        self.size = 0
    
    def __len__(self):
        """返回顺序表长度"""
        return self.size
    
    def __str__(self):
        """返回顺序表的字符串表示"""
        return str([self.data[i] for i in range(self.size)])
    
    def __iter__(self):
        """返回顺序表的迭代器"""
        for i in range(self.size):
            yield self.data[i]
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        return {
            'type': 'array_list',
            'data': [self.data[i] for i in range(self.size)],
            'capacity': self.capacity,
            'size': self.size
        }