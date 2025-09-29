#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
链表实现 - 基于节点的线性表
"""


class Node:
    """链表节点类"""
    
    def __init__(self, data=None):
        """初始化节点
        
        Args:
            data: 节点数据
        """
        self.data = data
        self.next = None


class LinkedList:
    """链表类，基于节点实现的线性表"""
    
    def __init__(self):
        """初始化链表"""
        self.head = None
        self.size = 0
        
    def to_list(self):
        """将链表转换为列表
        
        Returns:
            list: 包含链表所有元素的列表
        """
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def is_empty(self):
        """判断链表是否为空
        
        Returns:
            bool: 如果链表为空返回True，否则返回False
        """
        return self.head is None
    
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
        
        current = self.head
        for _ in range(index):
            current = current.next
        
        return current.data
    
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
        
        current = self.head
        for _ in range(index):
            current = current.next
        
        current.data = value
    
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
        
        # 创建新节点
        new_node = Node(value)
        
        # 如果在链表头插入
        if index == 0:
            new_node.next = self.head
            self.head = new_node
        else:
            # 找到插入位置的前一个节点
            current = self.head
            for _ in range(index - 1):
                current = current.next
            
            # 插入新节点
            new_node.next = current.next
            current.next = new_node
        
        self.size += 1
    
    def append(self, value):
        """在链表末尾添加元素
        
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
        
        # 如果删除链表头
        if index == 0:
            removed_value = self.head.data
            self.head = self.head.next
        else:
            # 找到删除位置的前一个节点
            current = self.head
            for _ in range(index - 1):
                current = current.next
            
            # 删除节点
            removed_value = current.next.data
            current.next = current.next.next
        
        self.size -= 1
        return removed_value
    
    def index_of(self, value):
        """查找元素在链表中的位置
        
        Args:
            value: 要查找的元素值
            
        Returns:
            int: 元素在链表中的位置，如果不存在返回-1
        """
        current = self.head
        index = 0
        
        while current:
            if current.data == value:
                return index
            current = current.next
            index += 1
        
        return -1
    
    def clear(self):
        """清空链表"""
        self.head = None
        self.size = 0
    
    def __len__(self):
        """返回链表长度"""
        return self.size
    
    def __str__(self):
        """返回链表的字符串表示"""
        values = []
        current = self.head
        
        while current:
            values.append(str(current.data))
            current = current.next
        
        return '[' + ', '.join(values) + ']'
    
    def __iter__(self):
        """返回链表的迭代器"""
        current = self.head
        while current:
            yield current.data
            current = current.next
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        nodes = []
        links = []
        
        current = self.head
        index = 0
        
        while current:
            # 添加节点
            nodes.append({
                'id': index,
                'data': current.data
            })
            
            # 添加链接
            if current.next:
                links.append({
                    'source': index,
                    'target': index + 1
                })
            
            current = current.next
            index += 1
        
        return {
            'type': 'linked_list',
            'nodes': nodes,
            'links': links,
            'size': self.size
        }