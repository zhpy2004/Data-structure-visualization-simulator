#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""二叉树实现模块。

本模块提供二叉树的链式存储结构实现，包括节点定义和树操作。
支持从列表构建二叉树以及多种遍历方式。
"""

from collections import deque


class TreeNode:
    """二叉树节点类。
    
    表示二叉树中的单个节点，包含数据和左右子节点引用。
    
    Attributes:
        data: 节点存储的数据值。
        left: 左子节点的引用，默认为None。
        right: 右子节点的引用，默认为None。
    """
    
    def __init__(self, data=None):
        """初始化二叉树节点。
        
        Args:
            data: 节点存储的数据值，默认为None。
        """
        self.data = data
        self.left = None   # 左子节点
        self.right = None  # 右子节点


class BinaryTree:
    """二叉树类，基于链式存储结构实现。
    
    提供二叉树的基本操作，包括创建、遍历和查询等功能。
    
    Attributes:
        root: 二叉树的根节点，默认为None。
        size: 二叉树的节点数量。
    """
    
    def serialize(self):
        """序列化二叉树为层序遍历数组
        
        Returns:
            list: 层序遍历数组
        """
        return self.levelorder_traversal()
        
    def deserialize(self, data):
        """从层序遍历数组反序列化二叉树
        
        Args:
            data: 层序遍历数组
        """
        if not data:
            return
            
        # 清空当前树
        self.root = None
        
        # 重建树
        for value in data:
            if value is not None:
                self.insert(value)
    
    def __init__(self):
        """初始化一个空的二叉树。"""
        self.root = None
        self.size = 0
    
    def is_empty(self):
        """判断二叉树是否为空。
        
        Returns:
            bool: 如果二叉树为空返回True，否则返回False。
        """
        return self.root is None
    
    def build_from_list(self, data_list):
        """从层序遍历列表构建二叉树。
        
        使用广度优先的方式，根据给定的层序遍历列表构建完整的二叉树。
        
        Args:
            data_list: 层序遍历的节点值列表，None表示空节点。
        """
        if not data_list:
            return
        
        # 清空现有树
        self.clear()
        
        # 创建根节点
        self.root = TreeNode(data_list[0])
        self.size = 1
        
        # 使用队列进行层序构建
        queue = deque([self.root])
        i = 1
        
        while queue and i < len(data_list):
            node = queue.popleft()
            
            # 添加左子节点
            if i < len(data_list) and data_list[i] is not None:
                node.left = TreeNode(data_list[i])
                queue.append(node.left)
                self.size += 1
            i += 1
            
            # 添加右子节点
            if i < len(data_list) and data_list[i] is not None:
                node.right = TreeNode(data_list[i])
                queue.append(node.right)
                self.size += 1
            i += 1
    
    def insert(self, value):
        """插入节点（层序插入到第一个空位置）
        
        Args:
            value: 插入的节点值
        """
        if self.is_empty():
            self.root = TreeNode(value)
            self.size = 1
            return
        
        # 使用队列进行层序遍历，找到第一个没有左子节点或右子节点的节点
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            
            # 如果没有左子节点，插入到左子节点
            if node.left is None:
                node.left = TreeNode(value)
                self.size += 1
                return
            else:
                queue.append(node.left)
            
            # 如果没有右子节点，插入到右子节点
            if node.right is None:
                node.right = TreeNode(value)
                self.size += 1
                return
            else:
                queue.append(node.right)
    
    def preorder_traversal(self):
        """前序遍历二叉树
        
        Returns:
            list: 前序遍历结果列表
        """
        result = []
        self._preorder(self.root, result)
        return result
    
    def _preorder(self, node, result):
        """前序遍历的递归辅助函数
        
        Args:
            node: 当前节点
            result: 遍历结果列表
        """
        if node:
            result.append(node.data)  # 先访问根节点
            self._preorder(node.left, result)  # 再遍历左子树
            self._preorder(node.right, result)  # 最后遍历右子树
    
    def inorder_traversal(self):
        """中序遍历二叉树
        
        Returns:
            list: 中序遍历结果列表
        """
        result = []
        self._inorder(self.root, result)
        return result
    
    def _inorder(self, node, result):
        """中序遍历的递归辅助函数
        
        Args:
            node: 当前节点
            result: 遍历结果列表
        """
        if node:
            self._inorder(node.left, result)  # 先遍历左子树
            result.append(node.data)  # 再访问根节点
            self._inorder(node.right, result)  # 最后遍历右子树
    
    def postorder_traversal(self):
        """后序遍历二叉树
        
        Returns:
            list: 后序遍历结果列表
        """
        result = []
        self._postorder(self.root, result)
        return result
    
    def _postorder(self, node, result):
        """后序遍历的递归辅助函数
        
        Args:
            node: 当前节点
            result: 遍历结果列表
        """
        if node:
            self._postorder(node.left, result)  # 先遍历左子树
            self._postorder(node.right, result)  # 再遍历右子树
            result.append(node.data)  # 最后访问根节点
    
    def levelorder_traversal(self):
        """层序遍历二叉树
        
        Returns:
            list: 层序遍历结果列表
        """
        if self.is_empty():
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            result.append(node.data)
            
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        
        return result
    
    def height(self):
        """计算二叉树的高度
        
        Returns:
            int: 二叉树的高度
        """
        return self._height(self.root)
    
    def _height(self, node):
        """计算以node为根的子树高度的递归辅助函数
        
        Args:
            node: 当前节点
            
        Returns:
            int: 子树高度
        """
        if node is None:
            return 0
        
        left_height = self._height(node.left)
        right_height = self._height(node.right)
        
        return max(left_height, right_height) + 1
    
    def clear(self):
        """清空二叉树"""
        self.root = None
        self.size = 0
    
    def __len__(self):
        """返回二叉树节点数量"""
        return self.size
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        if self.is_empty():
            return {
                'type': 'binary_tree',
                'nodes': [],
                'links': [],
                'height': 0,
                'size': 0
            }
        
        nodes = []
        links = []
        node_map = {}  # 用于映射节点到ID
        
        # 计算每个节点的层级和位置
        level_info = self._calculate_node_positions()
        
        # 使用层序遍历构建节点和链接数据
        queue = deque([(self.root, 0, 0)])  # (节点, ID, 层级)
        node_id = 0
        
        while queue:
            node, parent_id, level = queue.popleft()
            current_id = node_id
            node_id += 1
            
            # 获取节点在其层级中的位置
            position = level_info.get(node, {'level': level, 'x_pos': 0.5})
            
            # 添加节点
            nodes.append({
                'id': current_id,
                'value': node.data,  # 使用value而不是data，与TreeCanvas兼容
                'parent_id': parent_id if parent_id != current_id else None,
                'level': position['level'],
                'x_pos': position['x_pos']
            })
            
            node_map[node] = current_id
            
            # 如果不是根节点，添加与父节点的链接
            if current_id != 0:
                links.append({
                    'source': parent_id,
                    'target': current_id
                })
            
            # 添加子节点到队列
            if node.left:
                queue.append((node.left, current_id, level + 1))
            if node.right:
                queue.append((node.right, current_id, level + 1))
        
        return {
            'type': 'binary_tree',
            'nodes': nodes,
            'links': links,
            'height': self.height(),
            'size': self.size
        }
        
    def _calculate_node_positions(self):
        """计算每个节点的位置信息
        
        Returns:
            dict: 节点到位置信息的映射
        """
        if self.is_empty():
            return {}
            
        positions = {}
        max_level = self.height()
        
        def _traverse(node, level, left, right):
            if not node:
                return
                
            # 计算水平位置（0到1之间的值）
            x_pos = (left + right) / 2
            
            # 存储位置信息
            positions[node] = {
                'level': level,
                'x_pos': x_pos
            }
            
            # 递归处理子节点
            mid = (left + right) / 2
            _traverse(node.left, level + 1, left, mid)
            _traverse(node.right, level + 1, mid, right)
        
        # 从根节点开始递归计算位置
        _traverse(self.root, 0, 0, 1)
        
        return positions