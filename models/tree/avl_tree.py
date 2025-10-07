#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AVL树实现 - 自平衡二叉搜索树
"""

from collections import deque


class AVLNode:
    """AVL树节点类"""
    
    def __init__(self, data=None):
        """初始化AVL树节点
        
        Args:
            data: 节点数据
        """
        self.data = data
        self.left = None   # 左子节点
        self.right = None  # 右子节点
        self.height = 1    # 节点高度，叶子节点高度为1
        self.node_id = None  # 用于动画的唯一标识


class AVLTree:
    """AVL树类，自平衡二叉搜索树"""
    
    def __init__(self):
        """初始化AVL树"""
        self.root = None
        self.size = 0
        self.node_id_counter = 0
        
    def is_empty(self):
        """判断AVL树是否为空
        
        Returns:
            bool: 如果AVL树为空返回True，否则返回False
        """
        return self.root is None
    
    def get_height(self, node):
        """获取节点高度
        
        Args:
            node: 节点
            
        Returns:
            int: 节点高度，空节点高度为0
        """
        if node is None:
            return 0
        return node.height
    
    def get_balance(self, node):
        """获取节点的平衡因子
        
        Args:
            node: 节点
            
        Returns:
            int: 平衡因子（左子树高度 - 右子树高度）
        """
        if node is None:
            return 0
        return self.get_height(node.left) - self.get_height(node.right)
    
    def height(self):
        """获取AVL树的高度
        
        Returns:
            int: AVL树的高度
        """
        return self.get_height(self.root)
    
    def update_height(self, node):
        """更新节点高度
        
        Args:
            node: 节点
        """
        if node is not None:
            node.height = 1 + max(self.get_height(node.left), self.get_height(node.right))
    
    def rotate_right(self, y):
        """右旋转
        
        Args:
            y: 需要旋转的节点
            
        Returns:
            AVLNode: 旋转后的根节点
        """
        x = y.left
        T2 = x.right
        
        # 执行旋转
        x.right = y
        y.left = T2
        
        # 更新高度
        self.update_height(y)
        self.update_height(x)
        
        return x
    
    def rotate_left(self, x):
        """左旋转
        
        Args:
            x: 需要旋转的节点
            
        Returns:
            AVLNode: 旋转后的根节点
        """
        y = x.right
        T2 = y.left
        
        # 执行旋转
        y.left = x
        x.right = T2
        
        # 更新高度
        self.update_height(x)
        self.update_height(y)
        
        return y
    
    def insert(self, value):
        """插入节点
        
        Args:
            value: 插入的节点值
        """
        # 检查值是否已存在
        if not self._search(self.root, value):
            self.root = self._insert(self.root, value)
            self.size += 1
    
    def insert_with_steps(self, value):
        """插入单个节点并记录动画步骤
        
        Args:
            value: 要插入的节点值
            
        Returns:
            list: 插入过程中的每一步状态
        """
        steps = []
        
        # 记录插入前的状态
        pre_insert_tree = self._get_tree_data(self.root) if self.root else None
        
        # 创建待插入节点信息
        pending_node = {
            'id': 'pending_insert',
            'value': value,
            'level': 0,
            'x_pos': 0.85,  # 在树的右边显示
            'is_pending': True,  # 标记为待插入节点
            'parent_id': None
        }
        
        steps.append({
            'step': 0,
            'description': f'准备插入值 {value}',
            'action': 'initialize',
            'current_tree': pre_insert_tree,
            'highlight_nodes': [],
            'inserted_value': value,
            'rotation_info': None,
            'pending_node': pending_node  # 添加待插入节点信息
        })
        
        # 检查值是否已存在
        if self._search(self.root, value):
            steps.append({
                'step': 1,
                'description': f'值 {value} 已存在，不重复插入',
                'action': 'complete',
                'current_tree': pre_insert_tree,
                'highlight_nodes': [],
                'inserted_value': value,
                'rotation_info': None
            })
            return steps
        
        # 执行插入并记录旋转信息
        rotation_info = []
        old_size = self.size
        self.root = self._insert_with_rotation_tracking(self.root, value, rotation_info)
        
        # 手动增加size（因为_insert_with_rotation_tracking不会自动增加）
        self.size += 1
        
        # 记录插入后的状态（高亮插入的节点）
        post_insert_tree = self._get_tree_data(self.root)
        steps.append({
            'step': 1,
            'description': f'插入值 {value}完成' + (f'，执行旋转: {rotation_info[0]}' if rotation_info else ''),
            'action': 'insert',
            'current_tree': post_insert_tree,
            'highlight_nodes': [self._find_node_id_by_value(value)],
            'inserted_value': value,
            'rotation_info': rotation_info[0] if rotation_info else None
        })
        
        # 增加最终步骤：显示无高亮的最终结果
        steps.append({
            'step': 2,
            'description': f'插入操作完成，显示最终结果',
            'action': 'complete',
            'current_tree': post_insert_tree,
            'highlight_nodes': [],  # 无高亮节点
            'inserted_value': value,
            'rotation_info': None
        })
        
        # 调试信息：显示生成的步骤
        print(f"insert_with_steps生成了{len(steps)}个步骤:")
        for i, step in enumerate(steps):
            tree_nodes = step.get('current_tree', {}).get('nodes', []) if step.get('current_tree') else []
            print(f"  步骤{i}: action={step.get('action')}, 节点数={len(tree_nodes)}, description={step.get('description')}")
        
        return steps
    
    def _insert(self, node, value):
        """插入节点的递归辅助函数
        
        Args:
            node: 当前节点
            value: 插入的节点值
            
        Returns:
            AVLNode: 插入后的子树根节点
        """
        # 1. 执行标准BST插入
        if node is None:
            new_node = AVLNode(value)
            new_node.node_id = self.node_id_counter
            self.node_id_counter += 1
            return new_node
        
        if value < node.data:
            node.left = self._insert(node.left, value)
        elif value > node.data:
            node.right = self._insert(node.right, value)
        else:
            # 相等的值不插入
            return node
        
        # 2. 更新当前节点的高度
        self.update_height(node)
        
        # 3. 获取平衡因子
        balance = self.get_balance(node)
        
        # 4. 如果节点不平衡，执行相应的旋转
        # 左左情况
        if balance > 1 and value < node.left.data:
            return self.rotate_right(node)
        
        # 右右情况
        if balance < -1 and value > node.right.data:
            return self.rotate_left(node)
        
        # 左右情况
        if balance > 1 and value > node.left.data:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        
        # 右左情况
        if balance < -1 and value < node.right.data:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        
        # 返回未改变的节点
        return node
    
    def build_with_steps(self, values):
        """构建AVL树并记录每一步的状态
        
        Args:
            values: 要插入的值列表
            
        Returns:
            list: 构建过程中的每一步状态
        """
        if not values:
            return []
        
        # 清空现有树
        self.clear()
        
        # 记录构建过程中的每一步状态
        steps = []
        
        # 记录初始状态
        steps.append({
            'step': 0,
            'description': f'初始化：准备插入值 {values}',
            'action': 'initialize',
            'values_to_insert': values,
            'current_tree': None,
            'highlight_nodes': [],
            'inserted_value': None,
            'rotation_info': None
        })
        
        step_count = 1
        
        # 逐个插入值
        for value in values:
            # 记录插入前的状态
            pre_insert_tree = self._get_tree_data(self.root) if self.root else None
            
            # 执行插入并记录旋转信息
            rotation_info = []
            self.root = self._insert_with_rotation_tracking(self.root, value, rotation_info)
            self.size += 1
            
            # 记录插入后的状态
            post_insert_tree = self._get_tree_data(self.root)
            
            steps.append({
                'step': step_count,
                'description': f'插入值 {value}' + (f'，执行旋转: {rotation_info[0]}' if rotation_info else ''),
                'action': 'insert',
                'values_to_insert': values,
                'current_tree': post_insert_tree,
                'highlight_nodes': [self._find_node_id_by_value(value)],
                'inserted_value': value,
                'rotation_info': rotation_info[0] if rotation_info else None
            })
            step_count += 1
        
        # 记录最终状态
        final_tree_data = self._get_tree_data(self.root)
        steps.append({
            'step': step_count,
            'description': 'AVL树构建完成',
            'action': 'complete',
            'values_to_insert': values,
            'current_tree': final_tree_data,
            'highlight_nodes': [],
            'inserted_value': None,
            'rotation_info': None
        })
        
        return steps
    
    def _insert_with_rotation_tracking(self, node, value, rotation_info):
        """插入节点并跟踪旋转信息
        
        Args:
            node: 当前节点
            value: 插入的节点值
            rotation_info: 旋转信息列表
            
        Returns:
            AVLNode: 插入后的子树根节点
        """
        # 1. 执行标准BST插入
        if node is None:
            new_node = AVLNode(value)
            new_node.node_id = self.node_id_counter
            self.node_id_counter += 1
            return new_node
        
        if value < node.data:
            node.left = self._insert_with_rotation_tracking(node.left, value, rotation_info)
        elif value > node.data:
            node.right = self._insert_with_rotation_tracking(node.right, value, rotation_info)
        else:
            # 相等的值不插入
            return node
        
        # 2. 更新当前节点的高度
        self.update_height(node)
        
        # 3. 获取平衡因子
        balance = self.get_balance(node)
        
        # 4. 如果节点不平衡，执行相应的旋转
        # 左左情况
        if balance > 1 and value < node.left.data:
            rotation_info.append(f'右旋转节点 {node.data}')
            return self.rotate_right(node)
        
        # 右右情况
        if balance < -1 and value > node.right.data:
            rotation_info.append(f'左旋转节点 {node.data}')
            return self.rotate_left(node)
        
        # 左右情况
        if balance > 1 and value > node.left.data:
            rotation_info.append(f'左右旋转：先左旋转节点 {node.left.data}，再右旋转节点 {node.data}')
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        
        # 右左情况
        if balance < -1 and value < node.right.data:
            rotation_info.append(f'右左旋转：先右旋转节点 {node.right.data}，再左旋转节点 {node.data}')
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        
        # 返回未改变的节点
        return node
    
    def _find_node_id_by_value(self, value):
        """根据值查找节点ID
        
        Args:
            value: 节点值
            
        Returns:
            int: 节点ID，如果未找到返回None
        """
        return self._find_node_id_recursive(self.root, value)
    
    def _find_node_id_recursive(self, node, value):
        """递归查找节点ID
        
        Args:
            node: 当前节点
            value: 要查找的值
            
        Returns:
            int: 节点ID，如果未找到返回None
        """
        if node is None:
            return None
        
        if node.data == value:
            return node.node_id
        elif value < node.data:
            return self._find_node_id_recursive(node.left, value)
        else:
            return self._find_node_id_recursive(node.right, value)
    
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
        
        # 使用层序遍历构建节点和链接数据
        queue = deque([(root, None)])  # (节点, 父节点ID)
        
        while queue:
            node, parent_id = queue.popleft()
            
            current_id = node.node_id
            
            # 添加节点
            node_data = {
                'id': current_id,
                'value': node.data,
                'height': node.height,
                'balance': self.get_balance(node),
                'parent_id': parent_id,
                'is_leaf': node.left is None and node.right is None
            }
            nodes.append(node_data)
            
            # 调试信息
            print(f"添加节点: ID={current_id}, 值={node.data}, 父节点ID={parent_id}")
            
            # 如果有父节点，添加与父节点的链接
            if parent_id is not None:
                links.append({
                    'source': parent_id,
                    'target': current_id
                })
            
            # 添加子节点到队列
            if node.left:
                queue.append((node.left, current_id))
            
            if node.right:
                queue.append((node.right, current_id))
        
        result = {
            'nodes': nodes,
            'links': links
        }
        
        # 调试信息
        print(f"生成树数据: 节点数={len(nodes)}, 边数={len(links)}")
        for node in nodes:
            print(f"  节点: {node}")
        
        return result
    
    def search(self, value):
        """搜索节点
        
        Args:
            value: 搜索的节点值
            
        Returns:
            bool: 如果找到节点返回True，否则返回False
        """
        return self._search(self.root, value)
    
    def _search(self, node, value):
        """搜索节点的递归辅助函数
        
        Args:
            node: 当前节点
            value: 搜索的节点值
            
        Returns:
            bool: 如果找到节点返回True，否则返回False
        """
        if node is None:
            return False
        
        if value == node.data:
            return True
        elif value < node.data:
            return self._search(node.left, value)
        else:
            return self._search(node.right, value)
    
    def _find_node_id(self, node, value):
        """查找指定值的节点ID
        
        Args:
            node: 当前节点
            value: 搜索的节点值
            
        Returns:
            int: 如果找到节点返回节点ID，否则返回None
        """
        if node is None:
            return None
        
        if value == node.data:
            return node.node_id
        elif value < node.data:
            return self._find_node_id(node.left, value)
        else:
            return self._find_node_id(node.right, value)
    
    def inorder_traversal(self):
        """中序遍历AVL树
        
        Returns:
            list: 中序遍历结果列表
        """
        result = []
        self._inorder_traversal(self.root, result)
        return result
    
    def _inorder_traversal(self, node, result):
        """中序遍历的递归辅助函数
        
        Args:
            node: 当前节点
            result: 结果列表
        """
        if node:
            self._inorder_traversal(node.left, result)
            result.append(node.data)
            self._inorder_traversal(node.right, result)
    
    def preorder_traversal(self):
        """前序遍历AVL树
        
        Returns:
            list: 前序遍历结果列表
        """
        result = []
        self._preorder_traversal(self.root, result)
        return result
    
    def _preorder_traversal(self, node, result):
        """前序遍历的递归辅助函数
        
        Args:
            node: 当前节点
            result: 结果列表
        """
        if node:
            result.append(node.data)
            self._preorder_traversal(node.left, result)
            self._preorder_traversal(node.right, result)
    
    def postorder_traversal(self):
        """后序遍历AVL树
        
        Returns:
            list: 后序遍历结果列表
        """
        result = []
        self._postorder_traversal(self.root, result)
        return result
    
    def _postorder_traversal(self, node, result):
        """后序遍历的递归辅助函数
        
        Args:
            node: 当前节点
            result: 结果列表
        """
        if node:
            self._postorder_traversal(node.left, result)
            self._postorder_traversal(node.right, result)
            result.append(node.data)
    
    def levelorder_traversal(self):
        """层序遍历AVL树
        
        Returns:
            list: 层序遍历结果列表
        """
        if not self.root:
            return []
            
        result = []
        queue = deque([self.root])
        
        while queue:
            node = queue.popleft()
            if node:
                result.append(node.data)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            else:
                result.append(None)
                
        return result
    
    def clear(self):
        """清空AVL树"""
        self.root = None
        self.size = 0
        self.node_id_counter = 0
    
    def _count_nodes(self, node):
        """计算节点数量
        
        Args:
            node: 根节点
            
        Returns:
            int: 节点数量
        """
        if node is None:
            return 0
        return 1 + self._count_nodes(node.left) + self._count_nodes(node.right)
    
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
    
    def get_visualization_data(self):
        """获取用于可视化的数据
        
        Returns:
            dict: 包含可视化所需的数据
        """
        if self.is_empty():
            return {
                'type': 'avl_tree',
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
        queue = deque([(self.root, None, 0)])  # (节点, 父节点ID, 层级)
        
        while queue:
            node, parent_id, level = queue.popleft()
            current_id = node.node_id  # 使用节点的实际node_id
            
            # 获取节点在其层级中的位置
            position = level_info.get(node, {'level': level, 'x_pos': 0.5})
            
            # 添加节点
            nodes.append({
                'id': current_id,
                'data': node.data,
                'value': node.data,  # 添加value字段，与TreeCanvas兼容
                'height': node.height,  # AVL树特有的高度信息
                'parent_id': parent_id,
                'level': position['level'],
                'x_pos': position['x_pos']
            })
            
            node_map[node] = current_id
            
            # 如果不是根节点，添加与父节点的链接
            if parent_id is not None:
                links.append({
                    'source': parent_id,
                    'target': current_id
                })
            
            # 添加子节点到队列
            if node.left:
                queue.append((node.left, current_id, level + 1))
            if node.right:
                queue.append((node.right, current_id, level + 1))
        
        result = {
            'type': 'avl_tree',
            'nodes': nodes,
            'links': links,
            'height': self.height(),
            'size': self.size
        }
        
        # 调试信息
        print(f"get_visualization_data返回: 节点数={len(nodes)}, size={self.size}")
        for node in nodes:
            print(f"  可视化节点: ID={node['id']}, 值={node['value']}")
        
        return result
    
    def delete(self, value):
        """删除节点
        
        Args:
            value: 删除的节点值
            
        Returns:
            bool: 是否成功删除节点
        """
        if self.is_empty():
            return False
        
        # 检查节点是否存在
        if not self._search(self.root, value):
            return False
        
        # 记录原始大小
        original_size = self.size
        
        # 删除节点
        self.root = self._delete(self.root, value)
        
        # 如果大小变化，说明删除成功
        return self.size < original_size
    
    def _delete(self, node, value):
        """删除节点的递归辅助函数（AVL树版本）
        
        Args:
            node: 当前节点
            value: 删除的节点值
            
        Returns:
            AVLNode: 删除后的子树根节点
        """
        # 步骤1: 执行标准BST删除
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
        
        # 步骤2: 更新当前节点的高度
        self.update_height(node)
        
        # 步骤3: 获取平衡因子
        balance = self.get_balance(node)
        
        # 步骤4: 如果节点不平衡，执行旋转
        # 左左情况
        if balance > 1 and self.get_balance(node.left) >= 0:
            return self.rotate_right(node)
        
        # 左右情况
        if balance > 1 and self.get_balance(node.left) < 0:
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        
        # 右右情况
        if balance < -1 and self.get_balance(node.right) <= 0:
            return self.rotate_left(node)
        
        # 右左情况
        if balance < -1 and self.get_balance(node.right) > 0:
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        
        # 返回未改变的节点指针
        return node
    
    def get_tree_data(self):
        """获取树的数据结构（公共接口）
        
        Returns:
            dict: 树的数据结构，如果树为空则返回空结构
        """
        if self.is_empty():
            return {
                'type': 'avl_tree',
                'nodes': [],
                'links': [],
                'height': 0,
                'size': 0
            }
        
        tree_data = self._get_tree_data(self.root)
        if tree_data:
            tree_data['type'] = 'avl_tree'
            tree_data['height'] = self.height()
            actual_node_count = len(tree_data['nodes']) if 'nodes' in tree_data else 0
            print(f"调试信息: self.size={self.size}, 实际节点数={actual_node_count}")
            tree_data['size'] = actual_node_count  # 使用实际节点数而不是self.size
        
        return tree_data
    
    def _find_min(self, node):
        """查找以node为根的子树中的最小节点
        
        Args:
            node: 当前节点
            
        Returns:
            AVLNode: 最小节点
        """
        current = node
        while current.left is not None:
            current = current.left
        return current
    
    def delete_with_steps(self, value):
        """删除单个节点并记录动画步骤
        
        Args:
            value: 要删除的节点值
            
        Returns:
            list: 删除过程中的每一步状态
        """
        steps = []
        
        # 记录删除前的状态
        pre_delete_tree = self._get_tree_data(self.root) if self.root else None
        
        # 查找要删除的节点ID用于高亮显示
        target_node_id = self._find_node_id(self.root, value) if self.root else None
        highlight_nodes = [target_node_id] if target_node_id is not None else []
        
        steps.append({
            'step': 0,
            'description': f'准备删除值 {value}',
            'action': 'initialize',
            'current_tree': pre_delete_tree,
            'highlight_nodes': highlight_nodes,
            'deleted_value': value,
            'rotation_info': None
        })
        
        # 检查值是否存在
        if not self._search(self.root, value):
            steps.append({
                'step': 1,
                'description': f'值 {value} 不存在，无法删除',
                'action': 'complete',
                'current_tree': pre_delete_tree,
                'highlight_nodes': [],
                'deleted_value': value,
                'rotation_info': None
            })
            return steps
        
        # 执行删除并记录旋转信息
        rotation_info = []
        old_size = self.size
        self.root = self._delete_with_rotation_tracking(self.root, value, rotation_info)
        
        # 记录删除后的状态（同时作为完成状态）
        post_delete_tree = self._get_tree_data(self.root) if self.root else None
        steps.append({
            'step': 1,
            'description': f'删除值 {value}完成' + (f'，执行旋转: {rotation_info[0]}' if rotation_info else ''),
            'action': 'complete',
            'current_tree': post_delete_tree,
            'highlight_nodes': [],
            'deleted_value': value,
            'rotation_info': rotation_info[0] if rotation_info else None
        })
        
        return steps
    
    def _delete_with_rotation_tracking(self, node, value, rotation_info):
        """删除节点并跟踪旋转信息
        
        Args:
            node: 当前节点
            value: 删除的节点值
            rotation_info: 用于记录旋转信息的列表
            
        Returns:
            AVLNode: 删除后的子树根节点
        """
        # 步骤1: 执行标准BST删除
        if node is None:
            return None
        
        # 如果删除值小于当前节点值，在左子树中删除
        if value < node.data:
            node.left = self._delete_with_rotation_tracking(node.left, value, rotation_info)
        # 如果删除值大于当前节点值，在右子树中删除
        elif value > node.data:
            node.right = self._delete_with_rotation_tracking(node.right, value, rotation_info)
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
            node.right = self._delete_with_rotation_tracking(node.right, successor.data, rotation_info)
        
        # 步骤2: 更新当前节点的高度
        self.update_height(node)
        
        # 步骤3: 获取平衡因子
        balance = self.get_balance(node)
        
        # 步骤4: 如果节点不平衡，执行旋转
        # 左左情况
        if balance > 1 and self.get_balance(node.left) >= 0:
            rotation_info.append('LL')
            return self.rotate_right(node)
        
        # 左右情况
        if balance > 1 and self.get_balance(node.left) < 0:
            rotation_info.append('LR')
            node.left = self.rotate_left(node.left)
            return self.rotate_right(node)
        
        # 右右情况
        if balance < -1 and self.get_balance(node.right) <= 0:
            rotation_info.append('RR')
            return self.rotate_left(node)
        
        # 右左情况
        if balance < -1 and self.get_balance(node.right) > 0:
            rotation_info.append('RL')
            node.right = self.rotate_right(node.right)
            return self.rotate_left(node)
        
        # 返回未改变的节点指针
        return node