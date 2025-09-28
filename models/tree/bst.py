#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
二叉搜索树(BST)实现 - 基于链式存储结构的二叉搜索树
"""

from collections import deque


class TreeNode:
    """二叉搜索树节点类"""
    
    def __init__(self, data=None):
        """初始化二叉搜索树节点
        
        Args:
            data: 节点数据
        """
        self.data = data
        self.left = None   # 左子节点
        self.right = None  # 右子节点


class BST:
    """二叉搜索树类，基于链式存储结构"""
    
    def __init__(self):
        """初始化二叉搜索树"""
        self.root = None
        self.size = 0
    
    def is_empty(self):
        """判断二叉搜索树是否为空
        
        Returns:
            bool: 如果二叉搜索树为空返回True，否则返回False
        """
        return self.root is None
    
    def insert(self, value):
        """插入节点
        
        Args:
            value: 插入的节点值
        """
        self.root = self._insert(self.root, value)
        self.size += 1
    
    def _insert(self, node, value):
        """插入节点的递归辅助函数
        
        Args:
            node: 当前节点
            value: 插入的节点值
            
        Returns:
            TreeNode: 插入后的子树根节点
        """
        # 如果当前节点为空，创建新节点
        if node is None:
            return TreeNode(value)
        
        # 如果插入值小于当前节点值，插入到左子树
        if value < node.data:
            node.left = self._insert(node.left, value)
        # 如果插入值大于当前节点值，插入到右子树
        elif value > node.data:
            node.right = self._insert(node.right, value)
        # 如果插入值等于当前节点值，不做任何操作（BST通常不允许重复值）
        
        return node
    
    def search(self, value):
        """搜索节点
        
        Args:
            value: 搜索的节点值
            
        Returns:
            tuple: (是否找到, 搜索路径)
        """
        path = []
        found = self._search(self.root, value, path)
        return found, path
    
    def _search(self, node, value, path):
        """搜索节点的递归辅助函数
        
        Args:
            node: 当前节点
            value: 搜索的节点值
            path: 搜索路径列表
            
        Returns:
            bool: 是否找到节点
        """
        # 如果当前节点为空，未找到
        if node is None:
            return False
        
        # 将当前节点添加到路径
        path.append(node.data)
        
        # 如果找到节点
        if node.data == value:
            return True
        
        # 如果搜索值小于当前节点值，搜索左子树
        if value < node.data:
            return self._search(node.left, value, path)
        # 如果搜索值大于当前节点值，搜索右子树
        else:
            return self._search(node.right, value, path)
    
    def delete(self, value):
        """删除节点
        
        Args:
            value: 删除的节点值
            
        Returns:
            bool: 是否成功删除节点
        """
        if self.is_empty():
            return False
        
        # 记录原始大小
        original_size = self.size
        
        # 删除节点
        self.root = self._delete(self.root, value)
        
        # 如果大小变化，说明删除成功
        if self.size < original_size:
            return True
        return False
    
    def _delete(self, node, value):
        """删除节点的递归辅助函数
        
        Args:
            node: 当前节点
            value: 删除的节点值
            
        Returns:
            TreeNode: 删除后的子树根节点
        """
        # 如果当前节点为空，未找到要删除的节点
        if node is None:
            return None
        
        # 如果删除值小于当前节点值，在左子树中删除
        if value < node.data:
            node.left = self._delete(node.left, value)
        # 如果删除值大于当前节点值，在右子树中删除
        elif value > node.data:
            node.right = self._delete(node.right, value)
        # 如果找到要删除的节点
        else:
            # 情况1: 叶子节点（没有子节点）
            if node.left is None and node.right is None:
                self.size -= 1
                return None
            
            # 情况2: 只有一个子节点
            if node.left is None:
                self.size -= 1
                return node.right
            if node.right is None:
                self.size -= 1
                return node.left
            
            # 情况3: 有两个子节点
            # 找到右子树中的最小节点（中序后继）
            successor = self._find_min(node.right)
            # 用后继节点的值替换当前节点的值
            node.data = successor.data
            # 在右子树中删除后继节点
            node.right = self._delete(node.right, successor.data)
        
        return node
    
    def _find_min(self, node):
        """查找以node为根的子树中的最小节点
        
        Args:
            node: 当前节点
            
        Returns:
            TreeNode: 最小节点
        """
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def inorder_traversal(self):
        """中序遍历二叉搜索树
        
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
    
    def height(self):
        """计算二叉搜索树的高度
        
        Returns:
            int: 二叉搜索树的高度
        """
        return self._height(self.root)
    
    def _height(self, node):
        """计算以node为根的子树高度的递归辅助函数
        
        Args:
            node: 当前节点
            
        Returns:
            int: 子树的高度
        """
        if node is None:
            return 0
        
        left_height = self._height(node.left)
        right_height = self._height(node.right)
        
        return max(left_height, right_height) + 1
        
    def _calculate_node_positions(self):
        """计算每个节点的层级和水平位置
        
        Returns:
            dict: 节点到其位置信息的映射
        """
        if self.is_empty():
            return {}
            
        # 节点位置信息: {node: {'level': level, 'x_pos': x_pos}}
        positions = {}
        
        # 计算树的总宽度
        width = 2 ** self.height() - 1
        
        # 递归计算每个节点的位置
        self._calculate_position(self.root, 0, 0, width, positions)
        
        return positions
    
    def _calculate_position(self, node, level, left, right, positions):
        """递归计算节点位置
        
        Args:
            node: 当前节点
            level: 当前层级
            left: 左边界
            right: 右边界
            positions: 位置信息字典
        """
        if node is None:
            return
            
        # 计算当前节点的水平位置（0-1之间的相对位置）
        mid = (left + right) / 2
        x_pos = mid / max(1, right)  # 确保分母不为0，并且结果在0-1之间
        
        # 存储位置信息
        positions[node] = {
            'level': level,
            'x_pos': x_pos
        }
        
        # 递归计算左右子树的位置
        self._calculate_position(node.left, level + 1, left, mid - 1, positions)
        self._calculate_position(node.right, level + 1, mid + 1, right, positions)
    
    def clear(self):
        """清空二叉搜索树"""
        self.root = None
        self.size = 0
    
    def __len__(self):
        """返回二叉搜索树节点数量"""
        return self.size
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        if self.is_empty():
            return {
                'type': 'bst',
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
                'data': node.data,
                'value': node.data,  # 添加value字段，与TreeCanvas兼容
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
            'type': 'bst',
            'nodes': nodes,
            'links': links,
            'height': self.height(),
            'size': self.size
        }