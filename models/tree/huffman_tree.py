#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
哈夫曼树实现 - 用于构建最优前缀编码
"""

import heapq
from collections import deque


class HuffmanNode:
    """哈夫曼树节点类"""
    
    def __init__(self, char=None, freq=0):
        """初始化哈夫曼树节点
        
        Args:
            char: 字符
            freq: 频率
        """
        self.char = char  # 字符
        self.freq = freq  # 频率
        self.left = None  # 左子节点
        self.right = None  # 右子节点
    
    def __lt__(self, other):
        """重载小于运算符，用于优先队列比较
        
        Args:
            other: 另一个节点
            
        Returns:
            bool: 如果当前节点频率小于另一个节点频率返回True，否则返回False
        """
        return self.freq < other.freq


class HuffmanTree:
    """哈夫曼树类"""
    
    def __init__(self):
        """初始化哈夫曼树"""
        self.root = None
        self.codes = {}  # 哈夫曼编码表 {字符: 编码}
        self.size = 0
    
    def is_empty(self):
        """判断哈夫曼树是否为空
        
        Returns:
            bool: 如果哈夫曼树为空返回True，否则返回False
        """
        return self.root is None
    
    def build(self, frequencies):
        """构建哈夫曼树
        
        Args:
            frequencies: 字符频率字典，格式为 {字符: 频率}
        """
        if not frequencies:
            return
        
        # 清空现有树
        self.clear()
        
        # 创建叶子节点并加入优先队列
        pq = []
        for char, freq in frequencies.items():
            heapq.heappush(pq, HuffmanNode(char, freq))
        
        # 构建哈夫曼树
        while len(pq) > 1:
            # 取出两个频率最小的节点
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            
            # 创建新的内部节点，频率为两个子节点的频率之和
            internal = HuffmanNode(None, left.freq + right.freq)
            internal.left = left
            internal.right = right
            
            # 将新节点加入优先队列
            heapq.heappush(pq, internal)
        
        # 最后剩下的节点即为根节点
        if pq:
            self.root = heapq.heappop(pq)
            self.size = self._count_nodes(self.root)
            
            # 生成哈夫曼编码
            self._generate_codes()
    
    def build_with_steps(self, frequencies):
        """构建哈夫曼树并记录每一步的状态
        
        Args:
            frequencies: 字符频率字典，格式为 {字符: 频率}
            
        Returns:
            list: 构建过程中的每一步状态
        """
        if not frequencies:
            return []
        
        # 清空现有树
        self.clear()
        
        # 记录构建过程中的每一步状态
        steps = []
        
        # 创建叶子节点并加入优先队列
        pq = []
        for char, freq in frequencies.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(pq, node)
        
        # 记录初始状态
        initial_nodes = list(pq)  # 复制一份，因为pq会被修改
        steps.append({
            'step': 0,
            'description': '初始叶子节点',
            'nodes': [{'char': node.char, 'freq': node.freq} for node in initial_nodes],
            'tree': None
        })
        
        step_count = 1
        # 构建哈夫曼树
        while len(pq) > 1:
            # 取出两个频率最小的节点
            left = heapq.heappop(pq)
            right = heapq.heappop(pq)
            
            # 创建新的内部节点，频率为两个子节点的频率之和
            internal = HuffmanNode(None, left.freq + right.freq)
            internal.left = left
            internal.right = right
            
            # 将新节点加入优先队列
            heapq.heappush(pq, internal)
            
            # 记录当前状态
            current_tree = self._clone_tree(internal)
            steps.append({
                'step': step_count,
                'description': f'合并节点 {left.char if left.char else "内部节点"} ({left.freq}) 和 {right.char if right.char else "内部节点"} ({right.freq})',
                'nodes': [{'char': node.char, 'freq': node.freq} for node in pq],
                'tree': self._get_tree_data(current_tree)
            })
            step_count += 1
        
        # 最后剩下的节点即为根节点
        if pq:
            self.root = heapq.heappop(pq)
            self.size = self._count_nodes(self.root)
            
            # 生成哈夫曼编码
            self._generate_codes()
            
            # 记录最终状态
            steps.append({
                'step': step_count,
                'description': '最终哈夫曼树',
                'nodes': [],
                'tree': self._get_tree_data(self.root),
                'codes': self.codes
            })
        
        return steps
    
    def _clone_tree(self, node):
        """克隆树结构
        
        Args:
            node: 要克隆的节点
            
        Returns:
            HuffmanNode: 克隆后的节点
        """
        if node is None:
            return None
        
        clone = HuffmanNode(node.char, node.freq)
        clone.left = self._clone_tree(node.left)
        clone.right = self._clone_tree(node.right)
        
        return clone
    
    def _get_tree_data(self, root):
        """获取树的数据结构
        
        Args:
            root: 树的根节点
            
        Returns:
            dict: 树的数据结构
        """
        if root is None:
            return None
        
        nodes = []
        links = []
        node_map = {}  # 用于映射节点到ID
        
        # 使用层序遍历构建节点和链接数据
        queue = deque([(root, 0, None)])  # (节点, ID, 父节点ID)
        node_id = 0
        
        while queue:
            node, current_id, parent_id = queue.popleft()
            
            # 添加节点
            nodes.append({
                'id': current_id,
                'char': node.char,
                'freq': node.freq,
                'parent_id': parent_id
            })
            
            node_map[node] = current_id
            
            # 如果有父节点，添加与父节点的链接
            if parent_id is not None:
                links.append({
                    'source': parent_id,
                    'target': current_id
                })
            
            # 添加子节点到队列
            if node.left:
                child_id = node_id + 1
                node_id += 1
                queue.append((node.left, child_id, current_id))
            
            if node.right:
                child_id = node_id + 1
                node_id += 1
                queue.append((node.right, child_id, current_id))
        
        return {
            'nodes': nodes,
            'links': links
        }
    
    def _generate_codes(self):
        """生成哈夫曼编码"""
        self.codes = {}
        self._generate_codes_recursive(self.root, "")
    
    def _generate_codes_recursive(self, node, code):
        """递归生成哈夫曼编码
        
        Args:
            node: 当前节点
            code: 当前编码
        """
        if node is None:
            return
        
        # 如果是叶子节点，保存编码
        if node.char is not None:
            self.codes[node.char] = code
        
        # 递归生成左子树编码（添加0）
        self._generate_codes_recursive(node.left, code + "0")
        # 递归生成右子树编码（添加1）
        self._generate_codes_recursive(node.right, code + "1")
    
    def encode(self, text):
        """使用哈夫曼编码对文本进行编码
        
        Args:
            text: 要编码的文本
            
        Returns:
            str: 编码后的二进制字符串
        """
        if self.is_empty() or not self.codes:
            return ""
        
        encoded = ""
        for char in text:
            if char in self.codes:
                encoded += self.codes[char]
            else:
                # 对于不在编码表中的字符，可以选择忽略或使用特殊编码
                pass
        
        return encoded
    
    def decode(self, encoded):
        """使用哈夫曼编码对二进制字符串进行解码
        
        Args:
            encoded: 要解码的二进制字符串
            
        Returns:
            str: 解码后的文本
        """
        if self.is_empty() or not encoded:
            return ""
        
        # 构建反向编码表 {编码: 字符}
        reverse_codes = {code: char for char, code in self.codes.items()}
        
        decoded = ""
        current_code = ""
        
        for bit in encoded:
            current_code += bit
            if current_code in reverse_codes:
                decoded += reverse_codes[current_code]
                current_code = ""
        
        return decoded
    
    def _count_nodes(self, node):
        """计算以node为根的子树中的节点数量
        
        Args:
            node: 当前节点
            
        Returns:
            int: 节点数量
        """
        if node is None:
            return 0
        
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)
    
    def height(self):
        """计算哈夫曼树的高度
        
        Returns:
            int: 哈夫曼树的高度
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
        """清空哈夫曼树"""
        self.root = None
        self.codes = {}
        self.size = 0
    
    def __len__(self):
        """返回哈夫曼树节点数量"""
        return self.size
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        data = self._get_tree_data(self.root)
        
        if data is None:
            return {
                'type': 'huffman_tree',
                'nodes': [],
                'links': [],
                'height': 0,
                'size': 0,
                'codes': {}
            }
        
        # 计算每个节点的层级和位置
        if 'nodes' in data:
            self._add_visualization_positions(data['nodes'])
        
        # 添加额外的可视化数据
        data['type'] = 'huffman_tree'
        data['height'] = self.height()
        data['size'] = self.size
        data['codes'] = self.codes
        
        return data
        
    def _add_visualization_positions(self, nodes):
        """为节点添加可视化位置信息
        
        Args:
            nodes: 节点列表
        """
        if not nodes:
            return
            
        # 构建节点ID到节点的映射
        node_map = {node['id']: node for node in nodes}
        
        # 构建父子关系映射
        children_map = {}
        for node in nodes:
            parent_id = node.get('parent_id')
            if parent_id is not None:
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(node['id'])
        
        # 计算每个节点的层级
        for node in nodes:
            # 添加value字段，与TreeCanvas兼容
            if 'char' in node and node['char'] is not None:
                node['value'] = node['char']
            elif 'freq' in node:
                node['value'] = str(node['freq'])
            else:
                node['value'] = ''
                
            # 计算节点层级
            level = 0
            current = node
            parent_id = current.get('parent_id')
            
            while parent_id is not None and parent_id in node_map:
                level += 1
                current = node_map[parent_id]
                parent_id = current.get('parent_id')
                
            node['level'] = level
        
        # 找出根节点
        root_nodes = [node for node in nodes if node.get('parent_id') is None]
        if not root_nodes:
            return
        
        # 计算树的宽度
        max_level = max(node['level'] for node in nodes)
        width = 2 ** max_level
        
        # 使用改进的算法计算节点位置
        def calculate_positions(node_id, left, right, level):
            node = node_map[node_id]
            # 计算当前节点的水平位置
            node['x_pos'] = (left + right) / 2
            
            # 处理子节点
            if node_id in children_map:
                children = children_map[node_id]
                if len(children) == 2:
                    # 哈夫曼树的节点通常有0或2个子节点
                    mid = (left + right) / 2
                    calculate_positions(children[0], left, mid, level + 1)
                    calculate_positions(children[1], mid, right, level + 1)
                elif len(children) == 1:
                    # 处理只有一个子节点的情况
                    calculate_positions(children[0], (left + right - 0.5) / 2, (left + right + 0.5) / 2, level + 1)
        
        # 从根节点开始计算位置
        for i, root_node in enumerate(root_nodes):
            segment_width = 1.0 / len(root_nodes)
            left = i * segment_width
            right = (i + 1) * segment_width
            calculate_positions(root_node['id'], left, right, 0)