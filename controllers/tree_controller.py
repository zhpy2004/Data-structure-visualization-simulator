#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
树形结构控制器 - 负责处理树形数据结构的操作
"""

from models.tree.binary_tree import BinaryTree
from models.tree.bst import BST
from models.tree.huffman_tree import HuffmanTree
from models.tree.avl_tree import AVLTree
from utils.dsl_parser import parse_tree_dsl


class TreeController:
    """树形结构控制器类，负责处理树形数据结构的操作"""
    
    def __init__(self, view):
        """初始化树形结构控制器
        
        Args:
            view: 树形结构视图对象
        """
        self.view = view
        self.current_structure = None
        self.structure_type = None
    
    def handle_action(self, action_type, params=None):
        """处理树形结构操作
        
        Args:
            action_type: 操作类型，如'create', 'insert', 'delete', 'search', 'traverse', 'build_huffman', 'encode', 'decode', 'clear'
            params: 操作参数
        """
        if action_type == 'create':
            structure_type = params.get('structure_type') or params.get('type')
            values = params.get('values') or params.get('data', [])
            self._create_structure(structure_type, values)
        elif action_type == 'insert':
            value = params.get('value')
            position = params.get('position') if 'position' in params else params.get('path')
            execute_only = bool(params.get('execute_only'))
            self._insert_node(value, position, execute_only)
        elif action_type == 'delete' or action_type == 'remove':
            value = params.get('value')
            position = params.get('position') if 'position' in params else params.get('path')
            execute_only = bool(params.get('execute_only'))
            self._delete_node(value, position, execute_only)
        elif action_type == 'search':
            value = params.get('value')
            self._search_node(value)
        elif action_type == 'traverse':
            traverse_type = params.get('traversal_type') or params.get('traverse_type')
            self._traverse(traverse_type)
        elif action_type == 'build_huffman':
            frequencies = params.get('frequencies') or params.get('values')
            self._build_huffman_tree(frequencies)
        elif action_type == 'build_avl':
            values = params.get('values')
            self._build_avl_tree(values)
        elif action_type == 'encode':
            text = params.get('text')
            self._encode_text(text)
        elif action_type == 'decode':
            binary = params.get('binary')
            self._decode_binary(binary)
        elif action_type == 'clear':
            self._clear_structure()
        elif action_type == 'change_structure':
            structure_type = params.get('structure_type')
            # 当切换数据结构类型时，清空当前结构并创建新的空结构
            self._create_structure(structure_type, [])
        elif action_type == 'save':
            # 保存当前数据结构
            return self.get_structure_data()
        elif action_type == 'load':
            # 加载数据结构
            structure_type = params.get('structure_type')
            data = params.get('data')
            self.load_structure(structure_type, data)
        else:
            self.view.show_message("错误", f"未知操作类型: {action_type}")
            
    def get_structure_data(self):
        """获取当前数据结构的数据，用于保存
        
        Returns:
            dict: 包含数据结构状态的字典
        """
        if not self.current_structure:
            return None
            
        # 根据不同的数据结构类型，获取其数据
        data = {
            'structure_type': self.structure_type
        }
        
        if self.structure_type == 'binary_tree':
            # 二叉树序列化为层序遍历数组
            data['tree_data'] = self.current_structure.levelorder_traversal()
        elif self.structure_type == 'bst':
            # BST序列化为层序遍历数组
            data['tree_data'] = self.current_structure.levelorder_traversal()
        elif self.structure_type == 'huffman_tree':
            # 哈夫曼树保存原始频率数据
            data['frequency_data'] = self.current_structure.get_frequency_data()
        elif self.structure_type == 'avl_tree':
            # AVL树序列化为层序遍历数组
            data['tree_data'] = self.current_structure.levelorder_traversal()
        
        return data
        
    def load_structure(self, structure_type, data):
        """从保存的数据加载数据结构
        
        Args:
            structure_type: 数据结构类型
            data: 保存的数据
        """
        if not data:
            return
        
        # 首先切换到对应的数据结构类型
        # 在视图中查找对应的数据结构类型索引并切换
        structure_index = -1
        for i in range(self.view.structure_combo.count()):
            if self.view.structure_combo.itemData(i) == structure_type:
                structure_index = i
                break
        
        # 如果找到了对应的数据结构类型，切换到该类型
        if structure_index >= 0:
            self.view.structure_combo.setCurrentIndex(structure_index)
            # 这会触发_structure_changed方法，更新UI和当前结构类型
        else:
            # 如果未找到对应的数据结构类型，显示错误信息
            self.view.show_message("错误", f"未找到数据结构类型: {structure_type}")
            
        # 根据不同的数据结构类型，加载数据
        if structure_type == 'binary_tree':
            tree_data = data.get('tree_data')
            if tree_data:
                self._create_structure(structure_type, tree_data)
        elif structure_type == 'bst':
            tree_data = data.get('tree_data')
            if tree_data:
                self._create_structure(structure_type, tree_data)
        elif structure_type == 'avl_tree':
            tree_data = data.get('tree_data')
            if tree_data:
                self._create_structure(structure_type, tree_data)
        elif structure_type == 'huffman_tree':
            frequency_data = data.get('frequency_data')
            if frequency_data:
                self._build_huffman_tree(frequency_data)
                
        # 更新视图
        self.view.update_view(self.current_structure)
    
    def execute_dsl(self, command):
        """执行DSL命令
        
        Args:
            command: DSL命令字符串
        """
        try:
            result = parse_tree_dsl(command)
            if isinstance(result, tuple) and len(result) == 2:
                action, params = result
                self.handle_action(action, params)
            else:
                self.view.show_message("错误", "DSL命令解析结果格式错误")
        except Exception as e:
            self.view.show_message("错误", f"DSL命令执行错误: {str(e)}")
    
    def _create_structure(self, structure_type, initial_data=None):
        """创建树形结构
        
        Args:
            structure_type: 结构类型，'binary_tree', 'bst', 'huffman_tree', 或 'avl_tree'
            initial_data: 初始数据列表
        """
        if initial_data is None:
            initial_data = []
        
        self.structure_type = structure_type
        
        if structure_type == 'binary_tree':
            self.current_structure = BinaryTree()
            if initial_data:
                self.current_structure.build_from_list(initial_data)
        elif structure_type == 'bst':
            self.current_structure = BST()
            for item in initial_data:
                self.current_structure.insert(item)
        elif structure_type == 'huffman_tree':
            self.current_structure = HuffmanTree()
            if initial_data:
                self.current_structure.build(initial_data)
            # 如果没有初始数据，仅创建空的哈夫曼树结构，不进行构建
        elif structure_type == 'avl_tree':
            self.current_structure = AVLTree()
            for item in initial_data:
                self.current_structure.insert(item)
        else:
            self.view.show_message("错误", f"未知结构类型: {structure_type}")
            return
        
        # 更新视图
        self._update_view()
    
    def _insert_node(self, value, position=None, execute_only=False):
        """插入节点（支持路径位置）
        
        Args:
            value: 节点值
            position: 路径位置（列表），如二叉树为[0,1,...]
            execute_only: 若为True，直接执行插入；否则先播放路径动画
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return
        
        if self.structure_type == 'huffman_tree':
            self.view.show_message("错误", "哈夫曼树不支持单独插入节点")
            return
        
        try:
            if self.structure_type == 'avl_tree':
                # AVL树使用特殊的插入方法，生成动画步骤
                build_steps = self.current_structure.insert_with_steps(value)
                # 显示AVL树插入动画，弹窗将在动画完成后显示
                self.view.show_avl_build_animation(build_steps, value)
            elif self.structure_type == 'bst' and not execute_only:
                # BST：先播放插入路径动画，动画结束后再执行插入
                found, path = self.current_structure.search(value)
                self.view.highlight_bst_insert_path(path, value)
            else:
                # 其他树类型或执行阶段：直接插入
                before_state = self.current_structure.get_visualization_data()
                if self.structure_type == 'binary_tree' and position:
                    self.current_structure.insert_at_path(value, position)
                else:
                    self.current_structure.insert(value)
                after_state = self.current_structure.get_visualization_data()
                self.view.update_visualization_with_animation(before_state, after_state, 'insert', value)
        except Exception as e:
            self.view.show_message("错误", f"插入失败: {str(e)}")
    
    def _get_tree_values(self, node):
        """获取树中所有节点的值（中序遍历）
        
        Args:
            node: 当前节点
            
        Returns:
            list: 节点值列表
        """
        if node is None:
            return []
        
        values = []
        values.extend(self._get_tree_values(node.left))
        values.append(node.data)
        values.extend(self._get_tree_values(node.right))
        return values
    
    def _delete_node(self, value, position=None, execute_only=False):
        """删除节点
        
        Args:
            value: 节点值（BST/AVL 按值删除；BinaryTree 可选用于校验）
            position: 路径列表（仅 BinaryTree 支持，0=左，1=右）
            execute_only: 若为True，直接执行删除；否则先播放路径动画
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return

        # 支持的删除类型：binary_tree（按路径），bst / avl_tree（按值）
        if self.structure_type not in ['binary_tree', 'bst', 'avl_tree']:
            self.view.show_message("错误", f"{self.structure_type}不支持删除操作")
            return

        try:
            # 尝试解析数值（对 BinaryTree 不是必需）
            parsed_value = None
            if value is not None:
                try:
                    parsed_value = int(value)
                except (ValueError, TypeError):
                    self.view.show_message("错误", "请输入有效的整数值")
                    return
            
            if self.structure_type == 'binary_tree':
                # 二叉树支持按路径删除
                if position is None:
                    self.view.show_message("错误", "二叉树删除需要提供路径（如 0,1,0）")
                    return
                if any(d not in (0, 1) for d in position):
                    self.view.show_message("错误", "路径仅允许 0 或 1")
                    return
                
                # 记录删除前的状态
                before_state = self.current_structure.get_visualization_data()
                
                # 计算将要删除的节点值用于动画展示
                node = self.current_structure.root
                for d in position:
                    node = node.left if d == 0 else node.right
                    if node is None:
                        self.view.show_message("错误", "路径指向的节点不存在")
                        return
                report_value = node.data
                
                # 执行按路径删除（可选校验值）
                success = self.current_structure.delete_at_path(position, expected_value=parsed_value)
                if success:
                    after_state = self.current_structure.get_visualization_data()
                    self.view.update_visualization_with_animation(before_state, after_state, 'delete', report_value)
                else:
                    self.view.show_message("提示", "删除失败：未知原因")
            elif self.structure_type == 'avl_tree':
                # AVL树：按值删除并播放删除动画
                if parsed_value is None:
                    self.view.show_message("错误", "AVL树删除需要提供整数值")
                    return
                delete_steps = self.current_structure.delete_with_steps(parsed_value)
                if delete_steps:
                    self.view.show_avl_delete_animation(delete_steps, parsed_value)
                else:
                    self.view.show_message("提示", f"值 {parsed_value} 不存在，无法删除")
            else:
                # BST：先播放删除路径动画，动画结束后执行删除
                if parsed_value is None:
                    self.view.show_message("错误", "BST删除需要提供整数值")
                    return
                if not execute_only:
                    found, path = self.current_structure.search(parsed_value)
                    self.view.highlight_bst_delete_path(path, parsed_value)
                else:
                    before_state = self.current_structure.get_visualization_data()
                    success = self.current_structure.delete(parsed_value)
                    if success:
                        after_state = self.current_structure.get_visualization_data()
                        self.view.update_visualization_with_animation(before_state, after_state, 'delete', parsed_value)
                    else:
                        self.view.show_message("提示", f"值 {parsed_value} 不存在，无法删除")
                    
        except Exception as e:
            self.view.show_message("错误", f"删除失败: {str(e)}")
    
    def _search_node(self, value):
        """搜索节点
        
        Args:
            value: 节点值
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return
        
        if self.structure_type not in ['bst']:
            self.view.show_message("错误", f"{self.structure_type}不支持搜索操作")
            return
        
        try:
            # 执行搜索操作，获取搜索路径
            found, path = self.current_structure.search(value)
            
            # 更新视图，显示搜索路径
            self.view.highlight_search_path(path, found, value)
            
            # 不再立即显示结果弹窗，而是在动画结束后显示
            # 结果弹窗将在动画完成后由视图类显示
        except Exception as e:
            self.view.show_message("错误", f"搜索失败: {str(e)}")
    
    def _build_huffman_tree(self, frequencies):
        """构建哈夫曼树
        
        Args:
            frequencies: 字符频率字典，格式为 {字符: 频率}
        """
        if not frequencies:
            self.view.show_message("错误", "请提供频率数据")
            return
        
        try:
            # 创建哈夫曼树
            self.structure_type = 'huffman_tree'
            self.current_structure = HuffmanTree()
            
            # 保存频率数据，用于后续保存和加载
            self.current_structure.frequencies = dict(frequencies)
            
            # 记录构建过程中的每一步状态
            build_steps = self.current_structure.build_with_steps(frequencies)
            
            # 更新视图，显示哈夫曼树构建过程的动画
            self.view.show_huffman_build_animation(build_steps)
        except Exception as e:
            self.view.show_message("错误", f"构建哈夫曼树失败: {str(e)}")
    
    def _build_avl_tree(self, values):
        """构建AVL树
        
        Args:
            values: 要插入的值列表
        """
        if not values:
            self.view.show_message("错误", "请提供要插入的值")
            return
        
        try:
            # 创建AVL树
            self.structure_type = 'avl_tree'
            self.current_structure = AVLTree()
            
            # 记录构建过程中的每一步状态
            build_steps = self.current_structure.build_with_steps(values)
            
            # 更新视图，显示AVL树构建过程的动画
            self.view.show_avl_build_animation(build_steps)
        except Exception as e:
            self.view.show_message("错误", f"构建AVL树失败: {str(e)}")
    
    def _encode_text(self, text):
        """使用哈夫曼编码对文本进行编码
        
        Args:
            text: 要编码的文本
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建哈夫曼树")
            return
        
        if self.structure_type != 'huffman_tree':
            self.view.show_message("错误", "当前结构不是哈夫曼树，不支持编码操作")
            return
        
        try:
            # 执行编码操作
            encoded = self.current_structure.encode(text)
            
            # 显示编码结果
            self.view.show_message("编码结果", f"原文本: {text}\n编码结果: {encoded}")
            
            # 添加编码可视化效果
            # 保存编码表到视图对象
            self.view.huffman_codes = self.current_structure.codes
            self.view.highlight_huffman_codes(text, self.current_structure.codes)
        except Exception as e:
            self.view.show_message("错误", f"编码失败: {str(e)}")
    
    def _decode_binary(self, binary):
        """使用哈夫曼编码对二进制字符串进行解码
        
        Args:
            binary: 要解码的二进制字符串
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建哈夫曼树")
            return
        
        if self.structure_type != 'huffman_tree':
            self.view.show_message("错误", "当前结构不是哈夫曼树，不支持解码操作")
            return
        
        try:
            # 执行解码操作
            decoded = self.current_structure.decode(binary)
            
            # 显示解码结果
            self.view.show_message("解码结果", f"二进制编码: {binary}\n解码结果: {decoded}")
            
            # 添加解码可视化效果
            # 保存编码表到视图对象
            self.view.huffman_codes = self.current_structure.codes
            self.view.highlight_huffman_decode_path(binary, decoded)
        except Exception as e:
            self.view.show_message("错误", f"解码失败: {str(e)}")
    
    def _update_view(self):
        """更新视图显示"""
        if self.current_structure is None:
            return
        
        # 获取当前结构的可视化数据
        data = self.current_structure.get_visualization_data()
        
        # 更新视图
        self.view.update_visualization(data, self.structure_type)
        
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
        
    def _traverse(self, traverse_type):
        """遍历树结构
        
        Args:
            traverse_type: 遍历类型，'preorder', 'inorder', 'postorder', 或 'levelorder'
        """
        if self.current_structure is None:
            self.view.show_message("错误", "请先创建数据结构")
            return
        
        # 确保遍历类型有效
        if traverse_type is None:
            traverse_type = 'preorder'  # 设置默认值为前序遍历
        elif traverse_type.lower() not in ['preorder', 'inorder', 'postorder', 'levelorder']:
            traverse_type = 'preorder'  # 设置默认值为前序遍历
        else:
            # 标准化遍历类型（转为小写）
            traverse_type = traverse_type.lower()
        
        try:
            result = []
            if traverse_type == 'preorder':
                result = self.current_structure.preorder_traversal()
            elif traverse_type == 'inorder':
                result = self.current_structure.inorder_traversal()
            elif traverse_type == 'postorder':
                result = self.current_structure.postorder_traversal()
            elif traverse_type == 'levelorder':
                result = self.current_structure.levelorder_traversal()
            else:
                # 这个分支理论上不会执行到，因为我们已经在上面验证了遍历类型
                self.view.show_message("错误", f"未知遍历类型: {traverse_type}")
                return
            
            # 高亮显示遍历路径（动画会在结束时显示结果）
            self.view.highlight_traversal_path(result, traverse_type)
            
            # 注意：遍历结果将在动画结束后由视图类显示
        except Exception as e:
            self.view.show_message("错误", f"遍历失败: {str(e)}")

    def insert_node(self, structure_name, value, position=None):
        """公共封装：面向DSL的插入接口。
        Args:
            structure_name (str): 结构名，如 'binarytree'/'binary_tree'
            value (int): 节点值
            position (list[int]|None): 路径，如 [0,1,0]
        """
        return self.handle_action('insert', {
            'structure_name': structure_name,
            'value': value,
            'position': position,
        })

    def remove_node(self, structure_name, value=None, position=None):
        """公共封装：面向DSL的删除接口。
        支持按路径删除（binary_tree），或按值删除（BST/AVL）。
        Args:
            structure_name (str): 结构名
            value (int|None): 对BST/AVL有意义；对binary_tree可为None或用于校验
            position (list[int]|None): 路径
        """
        return self.handle_action('delete', {
            'structure_name': structure_name,
            'value': value,
            'position': position,
        })

    def create_structure(self, structure_type, values=None):
        """公共封装：创建树形结构。
        Args:
            structure_type (str): 'binary_tree' | 'bst' | 'huffman_tree' | 'avl_tree'
            values (list|dict|None): 初始数据
        """
        return self.handle_action('create', {
            'structure_type': structure_type,
            'values': values or [],
        })

    def search_node(self, structure_name, value):
        """公共封装：搜索节点。"""
        return self.handle_action('search', {
            'structure_name': structure_name,
            'value': value,
        })

    def traverse_tree(self, structure_name, traverse_type):
        """公共封装：遍历树结构。"""
        return self.handle_action('traverse', {
            'structure_name': structure_name,
            'traverse_type': traverse_type,
        })

    def clear_structure(self, structure_name):
        """公共封装：清空当前结构。"""
        return self.handle_action('clear', {
            'structure_name': structure_name,
        })

    def encode_text(self, text):
        """公共封装：哈夫曼编码文本。"""
        return self.handle_action('encode', {
            'text': text,
        })

    def decode_text(self, binary):
        """公共封装：哈夫曼解码二进制。"""
        return self.handle_action('decode', {
            'binary': binary,
        })