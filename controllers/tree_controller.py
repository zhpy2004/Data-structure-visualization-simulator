#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
树结构控制器 - 处理树相关的操作和与视图的交互
"""

from utils.dsl_parser import parse_tree_dsl
from models.tree.bst import BST
from models.tree.avl_tree import AVLTree
from models.tree.binary_tree import BinaryTree
from models.tree.huffman_tree import HuffmanTree


class TreeController:
    """树结构控制器类"""
    def __init__(self, view):
        self.view = view
        self.current_tree = None
        self.structure_type = None
        # —— BST构建为“多个插入动画”的队列状态 ——
        self._bst_build_values_queue = []
        self._bst_build_in_progress = False
        # —— 当BST构建进行中，后续命令排队，构建完成后依次执行 ——
        self._pending_actions_after_build = []

    def _ensure_view_structure(self, structure_type):
        """确保视图的结构类型选择与控制器一致，不触发视图的切换信号。

        在通过 DSL 或控制器内部发起的构建/创建时调用，用于把视图从 AVL 页静默切到 BST 等，
        避免出现“在 AVL 页面构建了 BST”的不一致体验。
        """
        try:
            if hasattr(self.view, 'set_structure_selection'):
                self.view.set_structure_selection(structure_type)
                return
            # 兜底：直接操作下拉框（尽量阻止信号）
            combo = getattr(self.view, 'structure_combo', None)
            if combo is not None:
                idx = combo.findData(structure_type)
                if idx != -1 and combo.currentIndex() != idx:
                    try:
                        combo.blockSignals(True)
                        combo.setCurrentIndex(idx)
                        combo.blockSignals(False)
                    except Exception:
                        combo.setCurrentIndex(idx)
                # 同步视图的内部状态（避免后续使用旧类型）
                try:
                    self.view.current_structure = structure_type
                except Exception:
                    pass
        except Exception:
            pass
    
    def handle_action(self, action_type, params=None):
        """处理树的操作"""
        if params is None:
            params = {}
        
        if action_type == 'create':
            structure_type = params.get('structure_type', params.get('type'))
            values = params.get('values', params.get('data', []))
            self._create_structure(structure_type, values)
        # —— 新增：支持构建动画类动作 ——
        elif action_type == 'build_bst':
            values = params.get('values', [])
            try:
                if self.current_tree is None or not isinstance(self.current_tree, BST):
                    self.current_tree = BST()
                    self.structure_type = 'bst'
                # 同步视图到 BST
                self._ensure_view_structure('bst')
                # 以“多个插入动画”方式构建：清空并逐个插入
                self.current_tree.clear()
                self._update_view()
                self._bst_build_values_queue = list(values)
                self._bst_build_in_progress = True
                self._start_next_bst_build_insert()
                # 允许后续插入操作
                try:
                    if hasattr(self.view, 'insert_button'):
                        self.view.insert_button.setEnabled(True)
                except Exception:
                    pass
            except Exception as e:
                self.view.show_message("错误", f"BST构建失败: {str(e)}")
        elif action_type == 'build_avl':
            values = params.get('values', [])
            try:
                if self.current_tree is None or not isinstance(self.current_tree, AVLTree):
                    self.current_tree = AVLTree()
                    self.structure_type = 'avl_tree'
                # 同步视图到 AVL
                self._ensure_view_structure('avl_tree')
                # 组合每次插入的步骤以形成整体构建动画
                steps = []
                self.current_tree.clear()
                for v in values:
                    steps.extend(self.current_tree.insert_with_steps(v))
                if hasattr(self.view, 'show_avl_build_animation'):
                    self.view.show_avl_build_animation(steps)
                else:
                    self._update_view()
                # 允许后续插入操作
                try:
                    if hasattr(self.view, 'insert_button'):
                        self.view.insert_button.setEnabled(True)
                except Exception:
                    pass
            except Exception as e:
                self.view.show_message("错误", f"AVL构建失败: {str(e)}")
        elif action_type == 'build_huffman':
            frequencies = params.get('frequencies') or params.get('values', {})
            try:
                if self.current_tree is None or not isinstance(self.current_tree, HuffmanTree):
                    self.current_tree = HuffmanTree()
                    self.structure_type = 'huffman_tree'
                # 同步视图到哈夫曼树
                self._ensure_view_structure('huffman_tree')
                steps = self.current_tree.build_with_steps(frequencies)
                if hasattr(self.view, 'show_huffman_build_animation'):
                    self.view.show_huffman_build_animation(steps)
                else:
                    self._update_view()
            except Exception as e:
                self.view.show_message("错误", f"哈夫曼树构建失败: {str(e)}")
        # —— 现有动作：插入/删除/搜索/遍历/清空/切换结构 ——
        elif action_type == 'insert':
            value = params.get('value')
            position = params.get('position')
            execute_only = params.get('execute_only', False)
            self._insert_value(value, position, execute_only=execute_only)
        elif action_type == 'remove' or action_type == 'delete':
            value = params.get('value')
            position = params.get('position')
            execute_only = params.get('execute_only', False)
            self._remove_value(value, position, execute_only=execute_only)
        elif action_type == 'search' or action_type == 'find':
            value = params.get('value')
            self._search_value(value)
        elif action_type == 'traverse':
            traverse_type = params.get('traverse_type') or params.get('traversal_type')
            # 执行遍历并在视图上高亮路径
            if self.current_tree is None:
                self.view.show_message("错误", "请先创建树结构")
                return
            traverse_type = traverse_type or 'preorder'
            method_map = {
                'preorder': 'preorder_traversal',
                'inorder': 'inorder_traversal',
                'postorder': 'postorder_traversal',
                'levelorder': 'levelorder_traversal'
            }
            method_name = method_map.get(traverse_type, 'preorder_traversal')
            if not hasattr(self.current_tree, method_name):
                self.view.show_message("错误", f"当前树不支持{traverse_type}遍历")
                return
            try:
                path = getattr(self.current_tree, method_name)()
            except Exception as e:
                self.view.show_message("错误", f"遍历失败: {str(e)}")
                return
            # 先刷新视图，再播放路径
            try:
                self._update_view()
                if hasattr(self.view, 'highlight_traversal_path'):
                    self.view.highlight_traversal_path(path, traverse_type)
            except Exception:
                pass
        elif action_type == 'encode':
            # 哈夫曼编码
            text = params.get('text', '')
            if self.current_tree is None or not isinstance(self.current_tree, HuffmanTree):
                self.view.show_message("错误", "请先创建并构建哈夫曼树")
                return
            try:
                encoded = self.current_tree.encode(text)
                if hasattr(self.view, 'show_result'):
                    self.view.show_result('huffman_encode', { 'encoded': encoded })
                else:
                    self.view.show_message("结果", f"编码结果: {encoded}")
            except Exception as e:
                self.view.show_message("错误", f"编码失败: {str(e)}")
        elif action_type == 'decode':
            # 哈夫曼解码
            binary = params.get('binary') or params.get('text', '')
            if self.current_tree is None or not isinstance(self.current_tree, HuffmanTree):
                self.view.show_message("错误", "请先创建并构建哈夫曼树")
                return
            try:
                decoded = self.current_tree.decode(binary)
                if hasattr(self.view, 'show_result'):
                    self.view.show_result('huffman_decode', { 'decoded': decoded })
                else:
                    self.view.show_message("结果", f"解码结果: {decoded}")
            except Exception as e:
                self.view.show_message("错误", f"解码失败: {str(e)}")
        elif action_type == 'clear':
            self._clear_tree()
        elif action_type == 'change_structure':
            structure_type = params.get('structure_type')
            self.structure_type = structure_type
            self.current_tree = None
            if self.view:
                self.view.update_view(None)
                self.view.show_message("提示", "已切换结构类型，请点击“新建”创建树")
                # 确保视图的下拉选择也同步（若此切换来自 DSL，而非用户手动）
                self._ensure_view_structure(structure_type)
        elif action_type == 'sync_structure':
            # 静默同步结构类型到视图，不清空当前树
            structure_type = params.get('structure_type')
            self.structure_type = structure_type
            if self.view:
                self._ensure_view_structure(structure_type)
        else:
            self.view.show_message("错误", f"未知操作类型: {action_type}")
    
    def execute_dsl(self, command):
        """执行树的DSL命令"""
        try:
            action, params = parse_tree_dsl(command)
            self.handle_action(action, params)
        except Exception as e:
            self.view.show_message("错误", f"DSL命令执行错误: {str(e)}")
    
    def _create_structure(self, structure_type, initial_values=None):
        """创建树结构"""
        if initial_values is None:
            initial_values = []
        
        self.structure_type = structure_type
        # 创建前同步视图类型，避免在 AVL 页面新建了 BST 等不一致场景
        self._ensure_view_structure(structure_type)
        
        if structure_type == 'bst':
            self.current_tree = BST()
            for v in initial_values:
                self.current_tree.insert(v)
        elif structure_type == 'avl_tree':
            self.current_tree = AVLTree()
            for v in initial_values:
                self.current_tree.insert(v)
        elif structure_type == 'binary_tree':
            self.current_tree = BinaryTree()
            # 若输入框提供了初始值，按层序插入创建树
            for v in initial_values:
                self.current_tree.insert(v)
        elif structure_type == 'huffman_tree':
            # 哈夫曼树通过频率表动画构建，不走通用插入流程
            self.current_tree = HuffmanTree()
        else:
            self.view.show_message("错误", f"未知树结构类型: {structure_type}")
            return
        
        self._update_view()
        
        # 新建后启用插入按钮（BST/AVL/普通二叉树适用；哈夫曼不启用）
        try:
            if hasattr(self.view, 'insert_button') and structure_type != 'huffman_tree':
                self.view.insert_button.setEnabled(True)
        except Exception:
            pass
    
    def _insert_value(self, value, position=None, execute_only=False):
        """插入值到树中（支持二叉树路径插入与层序插入；BST/AVL触发动画）"""
        if self.current_tree is None:
            self.view.show_message("错误", "请先创建树结构")
            return
        try:
            # BST：先播放插入路径动画，动画结束后由视图回调执行插入
            if self.structure_type == 'bst' and not execute_only:
                found, path = self.current_tree.search(value)
                if hasattr(self.view, 'highlight_bst_insert_path'):
                    self.view.highlight_bst_insert_path(path, value)
                else:
                    # 回退：直接插入
                    before_state = self.current_tree.get_visualization_data()
                    self.current_tree.insert(value)
                    after_state = self.current_tree.get_visualization_data()
                    if hasattr(self.view, 'update_visualization_with_animation'):
                        self.view.update_visualization_with_animation(before_state, after_state, 'insert', value=value)
                    else:
                        self._update_view()
                return
            
            # AVL：若为单次插入且不为执行阶段，则生成并播放构建步骤
            if self.structure_type == 'avl_tree' and not execute_only:
                try:
                    steps = self.current_tree.insert_with_steps(value)
                    if hasattr(self.view, 'show_avl_build_animation'):
                        self.view.show_avl_build_animation(steps, inserted_value=value)
                    else:
                        self._update_view()
                    return
                except Exception:
                    # 回退到直接插入
                    pass
            
            # 执行实际插入（包括二叉树、哈夫曼树不支持、BST/AVL执行阶段）
            before_state = self.current_tree.get_visualization_data()
            if self.structure_type == 'binary_tree':
                if position is not None:
                    self.current_tree.insert_at_path(value, position)
                else:
                    self.current_tree.insert(value)
            elif self.structure_type == 'huffman_tree':
                raise ValueError("哈夫曼树不支持直接插入，请使用构建动画")
            else:
                # BST/AVL 执行阶段或无动画支持
                self.current_tree.insert(value)
            after_state = self.current_tree.get_visualization_data()
            if hasattr(self.view, 'update_visualization_with_animation'):
                self.view.update_visualization_with_animation(before_state, after_state, 'insert', value=value)
            else:
                self._update_view()
            # 若处于BST“新建”为多次插入的构建过程中，继续下一次插入路径动画
            try:
                if self.structure_type == 'bst' and execute_only and getattr(self, '_bst_build_in_progress', False):
                    self._start_next_bst_build_insert()
            except Exception:
                pass
        except Exception as e:
            self.view.show_message("错误", f"插入失败: {str(e)}")
    
    def _remove_value(self, value=None, position=None, execute_only=False):
        """删除节点（支持二叉树按路径删除；BST删除路径动画；AVL删除步骤动画）"""
        if self.current_tree is None:
            self.view.show_message("错误", "请先创建树结构")
            return
        try:
            # BST：先播放删除路径动画，动画结束后由视图回调执行删除
            if self.structure_type == 'bst' and not execute_only:
                found, path = self.current_tree.search(value)
                if hasattr(self.view, 'highlight_bst_delete_path'):
                    self.view.highlight_bst_delete_path(path, value)
                else:
                    # 回退：直接删除
                    before_state = self.current_tree.get_visualization_data()
                    if hasattr(self.current_tree, 'delete'):
                        self.current_tree.delete(value)
                    elif hasattr(self.current_tree, 'remove'):
                        self.current_tree.remove(value)
                    after_state = self.current_tree.get_visualization_data()
                    if hasattr(self.view, 'update_visualization_with_animation'):
                        self.view.update_visualization_with_animation(before_state, after_state, 'delete', value=value)
                    else:
                        self._update_view()
                return
            
            # AVL：生成删除步骤动画
            if self.structure_type == 'avl_tree' and not execute_only:
                try:
                    steps = self.current_tree.delete_with_steps(value)
                    if hasattr(self.view, 'show_avl_delete_animation'):
                        self.view.show_avl_delete_animation(steps, deleted_value=value)
                    else:
                        self._update_view()
                    return
                except Exception:
                    # 回退到直接删除
                    pass
            
            # 执行实际删除
            before_state = self.current_tree.get_visualization_data()
            if self.structure_type == 'binary_tree':
                if position is None:
                    self.view.show_message("错误", "普通二叉树删除需要提供路径")
                    return
                if hasattr(self.current_tree, 'delete_at_path'):
                    self.current_tree.delete_at_path(position, expected_value=value)
                else:
                    raise AttributeError('当前二叉树模型不支持按路径删除')
            elif self.structure_type == 'huffman_tree':
                raise ValueError("哈夫曼树不支持直接删除")
            else:
                if hasattr(self.current_tree, 'remove'):
                    self.current_tree.remove(value)
                elif hasattr(self.current_tree, 'delete'):
                    self.current_tree.delete(value)
                else:
                    raise AttributeError('当前树模型不支持删除')
            after_state = self.current_tree.get_visualization_data()
            if hasattr(self.view, 'update_visualization_with_animation'):
                self.view.update_visualization_with_animation(before_state, after_state, 'delete', value=value)
            else:
                self._update_view()
        except Exception as e:
            self.view.show_message("错误", f"删除失败: {str(e)}")
    
    def _search_value(self, value):
        """搜索树中的值并展示动画（BST/AVL使用模型路径；二叉树走层序路径）"""
        if self.current_tree is None:
            self.view.show_message("错误", "请先创建树结构")
            return
        
        try:
            if self.structure_type == 'binary_tree':
                # 使用层序遍历产生查找路径，直到找到目标为止
                try:
                    traversal = self.current_tree.levelorder_traversal()
                except Exception:
                    traversal = []
                path = []
                found = False
                for v in traversal:
                    path.append(v)
                    if v == value:
                        found = True
                        break
                before_state = self.current_tree.get_visualization_data()
                after_state = before_state
                if hasattr(self.view, 'update_visualization_with_animation'):
                    self.view.update_visualization_with_animation(before_state, after_state, 'search', value=value)
                else:
                    self._update_view()
                if hasattr(self.view, 'highlight_search_path'):
                    self.view.highlight_search_path(path, found, search_value=value)
                return
            
            # BST/AVL：使用模型提供的搜索路径
            result = self.current_tree.search(value)
            if isinstance(result, tuple):
                is_found, path = bool(result[0]), result[1]
            else:
                is_found, path = bool(result), []
            before_state = self.current_tree.get_visualization_data()
            after_state = before_state
            if hasattr(self.view, 'update_visualization_with_animation'):
                self.view.update_visualization_with_animation(before_state, after_state, 'search', value=value)
            else:
                self._update_view()
            if hasattr(self.view, 'highlight_search_path'):
                self.view.highlight_search_path(path, is_found, search_value=value)
            # 搜索结果弹窗交由视图在动画结束后统一处理，避免重复弹窗
        except Exception as e:
            self.view.show_message("错误", f"搜索失败: {str(e)}")
    
    def _update_view(self):
        """更新树的视图显示"""
        if self.current_tree is None:
            return
        
        data = self.current_tree.get_visualization_data()
        if 'type' not in data:
            data['type'] = self.structure_type
        self.view.update_visualization(data)
    
    def _clear_tree(self):
        """清空当前树并更新视图"""
        if self.current_tree is None:
            self.view.show_message("错误", "请先创建树结构")
            return
        
        try:
            self.current_tree.clear()
            if hasattr(self.view, 'update_view'):
                self.view.update_view(None)
            else:
                self._update_view()
            self.view.show_message("成功", "树已清空")
        except Exception as e:
            self.view.show_message("错误", f"清空失败: {str(e)}")

    def queue_action_after_bst_build(self, action_type, params=None):
        """若BST构建进行中，则排队该动作，待构建完成后自动执行。
        返回True表示已入队；返回False表示当前不在构建流程中，请直接执行。
        """
        if params is None:
            params = {}
        if getattr(self, '_bst_build_in_progress', False):
            try:
                self._pending_actions_after_build.append((action_type, params))
            except Exception:
                # 兜底：若追加失败，不影响主流程
                pass
            return True
        return False
    
    def _start_next_bst_build_insert(self):
        """开始下一个BST插入路径动画（用于“新建”为多个插入动画的构建）"""
        # 若未处于构建流程或队列为空，结束
        if not getattr(self, '_bst_build_in_progress', False):
            return
        if not self._bst_build_values_queue:
            self._bst_build_in_progress = False
            try:
                if hasattr(self.view, 'status_label'):
                    self.view.status_label.setText("BST构建完成")
            except Exception:
                pass
            # 构建完成后，若存在排队的动作，依次执行
            try:
                pending = getattr(self, '_pending_actions_after_build', [])
                self._pending_actions_after_build = []
                for act, par in pending:
                    try:
                        self.handle_action(act, par)
                    except Exception:
                        # 不阻塞后续动作
                        pass
            except Exception:
                pass
            return
        # 取下一个值并播放插入路径
        value = self._bst_build_values_queue.pop(0)
        try:
            result = self.current_tree.search(value)
            if isinstance(result, tuple):
                _, path = result
            else:
                path = []
        except Exception:
            path = []
        try:
            if hasattr(self.view, 'highlight_bst_insert_path'):
                self.view.highlight_bst_insert_path(path, value)
            else:
                # 视图不支持路径动画时，直接执行插入并继续
                self._insert_value(value, execute_only=True)
        except Exception:
            self._insert_value(value, execute_only=True)