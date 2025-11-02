#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL控制器 - 用于处理DSL命令并连接UI与数据结构模型
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from models.tree.bst import BST
from models.tree.avl_tree import AVLTree
from models.tree.binary_tree import BinaryTree
from models.tree.huffman_tree import HuffmanTree
from utils.dsl_parser import parse_dsl_command


class DSLController(QObject):
    """DSL控制器类，用于处理DSL命令并连接UI与数据结构模型"""
    
    # 自定义信号
    command_result = pyqtSignal(str, dict)  # 命令结果信号
    
    def __init__(self, linear_controller=None, tree_controller=None):
        """初始化DSL控制器
        
        Args:
            linear_controller: 线性结构控制器
            tree_controller: 树形结构控制器
        """
        super().__init__()
        
        self.linear_controller = linear_controller
        self.tree_controller = tree_controller
        # 上下文目标：根据当前选项卡过滤命令类型（'linear' 或 'tree'）
        self.context_target = None
        # —— 脚本执行的异步队列与轮询 ——
        self._script_running = False
        self._script_pending_commands = []
        self._script_success_count = 0
        self._script_fail_count = 0
        self._script_timer = QTimer(self)
        self._script_timer.setInterval(100)
        self._script_timer.timeout.connect(self._process_next_script_command)
    
    def set_context_target(self, target):
        """设置上下文目标，用于按当前选项卡筛选命令类型"""
        self.context_target = target if target in ("linear", "tree") else None
    
    def process_command(self, command_str):
        """处理DSL命令
        
        Args:
            command_str: DSL命令字符串
            
        Returns:
            处理结果
        """
        # 解析命令
        command, command_type = parse_dsl_command(command_str)
        
        # 兼容解析结果为元组的情况：('command', {payload})
        if isinstance(command, tuple) and len(command) == 2 and isinstance(command[0], str) and isinstance(command[1], dict):
            command = {"command": command[0], **command[1]}
        
        # 检查是否有解析错误
        if isinstance(command, dict) and command.get("command") == "error":
            self.command_result.emit("error", {
                "message": command.get("error", "未知错误"),
                "target": None
            })
            return False
        
        # 全局命令：不受视图上下文限制
        if command_type == "global":
            if command.get("command") == "clear_all":
                # 清除线性结构（如已创建）
                if self.linear_controller and getattr(self.linear_controller, "current_structure", None) is not None:
                    try:
                        self.linear_controller.handle_action('clear', {})
                    except Exception:
                        pass
                # 清除树形结构（如已创建）
                if self.tree_controller and getattr(self.tree_controller, "current_tree", None) is not None:
                    try:
                        self.tree_controller.handle_action('clear', {})
                    except Exception:
                        pass
                self.command_result.emit("success", {
                    "message": "已清除所有数据结构",
                    "result": None,
                    "target": None
                })
                return True
        
        # 上下文类型过滤：当前在某个视图时，仅允许该类型命令
        if self.context_target and command_type and self.context_target != command_type:
            self.command_result.emit("error", {
                "message": f"当前为{self.context_target}视图，只能执行{self.context_target}命令",
                "target": self.context_target
            })
            return False
        
        # 根据命令类型分发到相应的控制器
        if command_type == "linear":
            return self._process_linear_command(command)
        elif command_type == "tree":
            return self._process_tree_command(command)
        else:
            self.command_result.emit("error", {
                "message": "无法识别的命令类型",
                "target": None
            })
            return False
    
    def _ensure_linear_structure(self, structure_name):
        """准备线性结构类型（仅切换类型，不自动新建）。
        若未新建则发出错误提示并返回 None。
        """
        mapping = {
            "arraylist": "array_list",
            "linkedlist": "linked_list",
            "stack": "stack"
        }
        normalized = mapping.get(structure_name, structure_name)

        # 先联动视图下拉框，确保 UI 切换到对应页面
        try:
            view = getattr(self.linear_controller, 'view', None)
            combo = getattr(view, 'structure_combo', None)
            if combo is not None:
                # 根据 itemData 查找匹配索引
                target_index = None
                for i in range(combo.count()):
                    try:
                        if combo.itemData(i) == normalized:
                            target_index = i
                            break
                    except Exception:
                        pass
                if target_index is not None and combo.currentIndex() != target_index:
                    combo.setCurrentIndex(target_index)  # 触发视图的 _structure_changed，从而切换按钮/状态
        except Exception:
            # 视图联动失败不影响后续逻辑
            pass

        # 若结构类型不同，仅切换类型（控制器状态），不自动创建
        if self.linear_controller.structure_type != normalized:
            self.linear_controller.handle_action('change_structure', {'structure_type': normalized})

        # 未新建则报错并返回 None
        if self.linear_controller.current_structure is None:
            self.command_result.emit("error", {
                "message": "当前未新建线性数据结构，请先执行 create 命令或点击“新建”",
                "target": "linear"
            })
            return None

        return normalized
    
    def _process_linear_command(self, command):
        """处理线性结构命令"""
        if not self.linear_controller:
            self.command_result.emit("error", {
                "message": "线性结构控制器未初始化",
                "target": "linear"
            })
            return False
        
        cmd_type = command.get("command")
        
        try:
            if cmd_type == "create":
                structure_type = command.get("structure_type")
                values = command.get("values", [])
                capacity = command.get("capacity")
                # 名称转换后直接创建（不依赖 _ensure_linear_structure）
                mapping = {
                    "arraylist": "array_list",
                    "linkedlist": "linked_list",
                    "stack": "stack"
                }
                normalized = mapping.get(structure_type, structure_type)
                # 执行创建前，同步视图至目标类型页面，避免在错误页面上执行
                try:
                    view = getattr(self.linear_controller, 'view', None)
                    combo = getattr(view, 'structure_combo', None)
                    if combo is not None:
                        target_index = None
                        for i in range(combo.count()):
                            try:
                                if combo.itemData(i) == normalized:
                                    target_index = i
                                    break
                            except Exception:
                                pass
                        if target_index is not None and combo.currentIndex() != target_index:
                            combo.setCurrentIndex(target_index)
                except Exception:
                    pass
                self.linear_controller.handle_action('create', {
                    'structure_type': normalized,
                    'values': values,
                    'capacity': capacity
                })
                self.command_result.emit("success", {
                    "message": f"成功创建{normalized}",
                    "result": None,
                    "target": "linear"
                })
            
            elif cmd_type == "insert":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                normalized = self._ensure_linear_structure(structure_name)
                if normalized is None:
                    return False
                self.linear_controller.handle_action('insert', {
                    'position': position,
                    'value': value
                })
                self.command_result.emit("success", {
                    "message": f"成功在{normalized}的位置{position}插入值{value}",
                    "result": None,
                    "target": "linear"
                })
            
            elif cmd_type == "delete":
                structure_name = command.get("structure_name")
                target = command.get("target")  # {type: 'position'|'value', value: X}
                # 兼容线性DSL解析器新增的显式字段，优先按位置删除
                explicit_position = command.get("position")
                explicit_value = command.get("value")
                normalized = self._ensure_linear_structure(structure_name)
                if normalized is None:
                    return False
                
                if explicit_position is not None:
                    position = explicit_position
                    self.linear_controller.handle_action('delete', {
                        'position': position
                    })
                    self.command_result.emit("success", {
                        "message": f"成功从{normalized}的位置{position}删除元素",
                        "result": None,
                        "target": "linear"
                    })
                elif target and target.get('type') == 'position':
                    position = target.get('value')
                    self.linear_controller.handle_action('delete', {
                        'position': position
                    })
                    self.command_result.emit("success", {
                        "message": f"成功从{normalized}的位置{position}删除元素",
                        "result": None,
                        "target": "linear"
                    })
                else:
                    # 通过值删除：仅当明确指定按值删除时才进入该分支
                    # 避免将 'delete at X' 误判为按值删除
                    if not (explicit_value is not None or (target and target.get('type') == 'value')):
                        self.command_result.emit("error", {
                            "message": "删除参数缺失：请使用 delete VALUE 或 delete at POSITION",
                            "target": "linear"
                        })
                        return False
                    # 线性控制器未提供直接按值删除，尝试查找索引再删除
                    value = explicit_value if explicit_value is not None else (target.get('value') if target else None)
                    # 仅在非栈结构支持
                    if self.linear_controller.structure_type == 'array_list':
                        data = self.linear_controller.current_structure.data[:self.linear_controller.current_structure.size]
                        try:
                            idx = data.index(value)
                        except ValueError:
                            idx = None
                    elif self.linear_controller.structure_type == 'linked_list':
                        lst = self.linear_controller.current_structure.to_list()
                        try:
                            idx = lst.index(value)
                        except ValueError:
                            idx = None
                    else:
                        idx = None
                    if idx is None:
                        self.command_result.emit("error", {
                            "message": f"在{normalized}中未找到值{value}",
                            "target": "linear"
                        })
                        return False
                    self.linear_controller.handle_action('delete', { 'position': idx })
                    self.command_result.emit("success", {
                        "message": f"成功从{normalized}中删除值{value}",
                        "result": None,
                        "target": "linear"
                    })
            
            elif cmd_type == "get":
                structure_name = command.get("structure_name")
                target = command.get("target")
                normalized = self._ensure_linear_structure(structure_name)
                if normalized is None:
                    return False
                if target and target.get('type') == 'position':
                    position = target.get('value')
                    self.linear_controller.handle_action('get', { 'position': position })
                    self.command_result.emit("success", {
                        "message": f"成功获取{normalized}的位置{position}的元素",
                        "result": None,
                        "target": "linear"
                    })
                else:
                    value = target.get('value') if target else None
                    # 通过值查找位置并执行 get 动画
                    if self.linear_controller.structure_type == 'array_list':
                        data = self.linear_controller.current_structure.data[:self.linear_controller.current_structure.size]
                        try:
                            idx = data.index(value)
                        except ValueError:
                            idx = None
                    elif self.linear_controller.structure_type == 'linked_list':
                        lst = self.linear_controller.current_structure.to_list()
                        try:
                            idx = lst.index(value)
                        except ValueError:
                            idx = None
                    else:
                        idx = None
                    if idx is None:
                        self.command_result.emit("error", {
                            "message": f"在{normalized}中未找到值{value}",
                            "target": "linear"
                        })
                        return False
                    self.linear_controller.handle_action('get', { 'position': idx })
                    self.command_result.emit("success", {
                        "message": f"成功在{normalized}中查找值{value}",
                        "result": None,
                        "target": "linear"
                    })
            
            elif cmd_type == "push":
                structure_name = command.get("structure_name")
                value = command.get("value")
                # 强制切换为栈类型，但不自动新建
                normalized = self._ensure_linear_structure('stack')
                if normalized is None:
                    return False
                self.linear_controller.handle_action('push', { 'value': value })
                self.command_result.emit("success", {
                    "message": f"成功将值{value}压入{normalized}",
                    "result": None,
                    "target": "linear"
                })
            
            elif cmd_type == "pop":
                structure_name = command.get("structure_name")
                normalized = self._ensure_linear_structure('stack')
                if normalized is None:
                    return False
                self.linear_controller.handle_action('pop', {})
                self.command_result.emit("success", {
                    "message": f"成功从{normalized}弹出元素",
                    "result": None,
                    "target": "linear"
                })
            
            elif cmd_type == "peek":
                structure_name = command.get("structure_name")
                normalized = self._ensure_linear_structure('stack')
                if normalized is None:
                    return False
                self.linear_controller.handle_action('peek', {})
                self.command_result.emit("success", {
                    "message": f"成功查看{normalized}栈顶元素",
                    "result": None,
                    "target": "linear"
                })
            
            elif cmd_type == "clear":
                structure_name = command.get("structure_name")
                normalized = self._ensure_linear_structure(structure_name)
                if normalized is None:
                    return False
                self.linear_controller.handle_action('clear', {})
                self.command_result.emit("success", {
                    "message": f"成功清空{normalized}",
                    "result": None,
                    "target": "linear"
                })
            
            else:
                self.command_result.emit("error", {
                    "message": f"未知的线性结构命令: {cmd_type}",
                    "target": "linear"
                })
                return False
            
            return True
            
        except Exception as e:
            self.command_result.emit("error", {
                "message": f"处理线性结构命令出错: {str(e)}",
                "target": "linear"
            })
            return False
    
    def _process_tree_command(self, command):
        """处理树形结构命令"""
        if not self.tree_controller:
            self.command_result.emit("error", {
                "message": "树形结构控制器未初始化",
                "target": "tree"
            })
            return False
        
        cmd_type = command.get("command")
        
        try:
            if cmd_type == "create":
                structure_type = command.get("structure_type")
                values = command.get("values", [])
                # 名称转换
                normalized = self._normalize_tree_structure(structure_type)
                self.tree_controller.handle_action('create', {
                    'structure_type': normalized,
                    'values': values
                })
                self.command_result.emit("success", {
                    "message": f"成功创建{normalized}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "insert":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                normalized = self._normalize_tree_structure(structure_name)
                # 先准备结构类型（仅同步，不清空）
                prep = self._prepare_tree_structure(normalized)
                if prep is None:
                    return False
                # 若BST正在批量构建，插入动作入队，待构建完成后自动执行
                if normalized == 'bst' and getattr(self.tree_controller, '_bst_build_in_progress', False):
                    queued = False
                    try:
                        queued = self.tree_controller.queue_action_after_bst_build('insert', {
                            'value': value,
                            'position': position
                        })
                    except Exception:
                        queued = False
                    if queued:
                        self.command_result.emit("success", {
                            "message": f"BST构建中，已排队插入值{value}",
                            "result": None,
                            "target": "tree"
                        })
                        return True
                # 未新建则报错
                if self.tree_controller.current_tree is None:
                    self.command_result.emit("error", {
                        "message": "当前未新建树结构，请先执行 create 命令或点击“新建”",
                        "target": "tree"
                    })
                    return False
                self.tree_controller.handle_action('insert', {
                    'value': value,
                    'position': position
                })
                self.command_result.emit("success", {
                    "message": f"成功在{normalized}中插入值{value}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "delete":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                normalized = self._normalize_tree_structure(structure_name)
                prep = self._prepare_tree_structure(normalized)
                if prep is None:
                    return False
                # 若BST正在批量构建，删除动作入队
                if normalized == 'bst' and getattr(self.tree_controller, '_bst_build_in_progress', False):
                    queued = False
                    try:
                        queued = self.tree_controller.queue_action_after_bst_build('delete', {
                            'value': value,
                            'position': position
                        })
                    except Exception:
                        queued = False
                    if queued:
                        self.command_result.emit("success", {
                            "message": f"BST构建中，已排队删除值{value}",
                            "result": None,
                            "target": "tree"
                        })
                        return True
                if self.tree_controller.current_tree is None:
                    self.command_result.emit("error", {
                        "message": "当前未新建树结构，请先执行 create 命令或点击“新建”",
                        "target": "tree"
                    })
                    return False
                self.tree_controller.handle_action('delete', {
                    'value': value,
                    'position': position
                })
                self.command_result.emit("success", {
                    "message": f"成功从{normalized}中删除值{value}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "search":
                structure_name = command.get("structure_name")
                value = command.get("value")
                normalized = self._normalize_tree_structure(structure_name)
                prep = self._prepare_tree_structure(normalized)
                if prep is None:
                    return False
                # 若BST正在批量构建，搜索动作入队
                if normalized == 'bst' and getattr(self.tree_controller, '_bst_build_in_progress', False):
                    queued = False
                    try:
                        queued = self.tree_controller.queue_action_after_bst_build('search', { 'value': value })
                    except Exception:
                        queued = False
                    if queued:
                        self.command_result.emit("success", {
                            "message": f"BST构建中，已排队搜索值{value}",
                            "result": None,
                            "target": "tree"
                        })
                        return True
                if self.tree_controller.current_tree is None:
                    self.command_result.emit("error", {
                        "message": "当前未新建树结构，请先执行 create 命令或点击“新建”",
                        "target": "tree"
                    })
                    return False
                self.tree_controller.handle_action('search', { 'value': value })
                self.command_result.emit("success", {
                    "message": f"成功在{normalized}中搜索值{value}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "traverse":
                structure_name = command.get("structure_name")
                traverse_type = command.get("traverse_type")
                normalized = 'binary_tree' if structure_name else self.tree_controller.structure_type
                # 仅支持普通二叉树的遍历
                if normalized != 'binary_tree':
                    self.command_result.emit("error", {
                        "message": "遍历命令仅支持普通二叉树（binarytree）",
                        "target": "tree"
                    })
                    return False
                if structure_name:
                    prep = self._prepare_tree_structure('binary_tree')
                    if prep is None:
                        return False
                if not self.tree_controller.current_tree:
                    self.command_result.emit("error", {
                        "message": "当前未新建树结构，请先执行 create 命令或点击“新建”",
                        "target": "tree"
                    })
                    return False
                self.tree_controller.handle_action('traverse', { 'traverse_type': traverse_type })
                self.command_result.emit("success", {
                    "message": f"成功以{traverse_type}方式遍历{normalized}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "build_huffman":
                values = command.get("values", {})
                self.tree_controller.handle_action('build_huffman', { 'values': values })
                self.command_result.emit("success", {
                    "message": "成功构建哈夫曼树",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "build_bst":
                values = command.get("values", [])
                self.tree_controller.handle_action('build_bst', { 'values': values })
                self.command_result.emit("success", {
                    "message": "成功构建二叉搜索树",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "build_avl":
                values = command.get("values", [])
                self.tree_controller.handle_action('build_avl', { 'values': values })
                self.command_result.emit("success", {
                    "message": "成功构建AVL树",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "encode":
                text = command.get("text")
                self.tree_controller.handle_action('encode', { 'text': text })
                self.command_result.emit("success", {
                    "message": f"成功编码文本: {text}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "decode":
                binary = command.get("binary")
                self.tree_controller.handle_action('decode', { 'binary': binary })
                self.command_result.emit("success", {
                    "message": f"成功解码: {binary}",
                    "result": None,
                    "target": "tree"
                })
            
            elif cmd_type == "clear":
                structure_name = command.get("structure_name")
                normalized = self._normalize_tree_structure(structure_name) if structure_name else self.tree_controller.structure_type
                if structure_name:
                    prep = self._prepare_tree_structure(normalized)
                    if prep is None:
                        return False
                if not self.tree_controller.current_tree:
                    self.command_result.emit("error", {
                        "message": "当前未新建树结构，请先执行 create 命令或点击“新建”",
                        "target": "tree"
                    })
                    return False
                self.tree_controller.handle_action('clear', {})
                self.command_result.emit("success", {
                    "message": f"成功清空{normalized}",
                    "result": None,
                    "target": "tree"
                })
            
            else:
                self.command_result.emit("error", {
                    "message": f"未知的树形结构命令: {cmd_type}",
                    "target": "tree"
                })
                return False
            
            return True
            
        except Exception as e:
            self.command_result.emit("error", {
                "message": f"处理树形结构命令出错: {str(e)}",
                "target": "tree"
            })
            return False

    def _normalize_tree_structure(self, name):
        """标准化树结构名称"""
        mapping = {
            'binarytree': 'binary_tree',
            'avl': 'avl_tree',
            'bst': 'bst',
            'huffman': 'huffman_tree'
        }
        # 若未指定名称，则回退到当前控制器记录的类型
        if name is None:
            return self.tree_controller.structure_type
        return mapping.get(name, name)

    def _current_tree_type_str(self):
        """返回当前树实例的类型字符串（用于错误提示与比对）"""
        if not self.tree_controller or not self.tree_controller.current_tree:
            return None
        t = self.tree_controller.current_tree
        if isinstance(t, BST):
            return 'bst'
        if isinstance(t, AVLTree):
            return 'avl_tree'
        if isinstance(t, BinaryTree):
            return 'binary_tree'
        if isinstance(t, HuffmanTree):
            return 'huffman_tree'
        # 回退为控制器记录的类型
        return self.tree_controller.structure_type or 'unknown'

    def _prepare_tree_structure(self, normalized):
        """若存在树则在类型匹配时静默同步；若类型不匹配则报错。
        若尚未新建树，仅同步类型到视图，并由后续逻辑提示需要 create。
        返回 normalized；若失败返回 None。
        """
        try:
            # 未显式指定目标类型：使用当前控制器类型（表示不请求切换）
            if normalized is None:
                return self.tree_controller.structure_type
            # 已是目标类型则无需操作
            if self.tree_controller.structure_type == normalized:
                return normalized
            # 若已有树实例
            if self.tree_controller.current_tree is not None:
                current_type = self._current_tree_type_str()
                if current_type == normalized:
                    # 仅静默同步控制器与视图，不清空
                    self.tree_controller.handle_action('sync_structure', { 'structure_type': normalized })
                    return normalized
                else:
                    # 类型不匹配：保留现有树，提示用户先清空或新建
                    self.command_result.emit("error", {
                        "message": f"当前结构类型为{current_type or '未指定'}，请先清空或新建{normalized or '未指定'}",
                        "target": "tree"
                    })
                    return None
            else:
                # 未新建：仅同步结构类型到视图，后续命令会提示需要 create
                self.tree_controller.handle_action('sync_structure', { 'structure_type': normalized })
                return normalized
        except Exception as e:
            self.command_result.emit("error", {
                "message": f"准备树结构类型失败: {str(e)}",
                "target": "tree"
            })
            return None

    def process_script(self, script_str):
        """按脚本执行多条DSL命令（换行或分号分隔；支持#和//注释），改为异步逐条执行，避免并发动画冲突"""
        # 若已有脚本在执行，拒绝并提示
        if self._script_running:
            self.command_result.emit("error", {
                "message": "已有脚本正在执行，请稍后再试",
                "target": self.context_target
            })
            return False
        # 拆分为逐条命令
        lines = script_str.replace('\r\n', '\n').split('\n')
        commands = []
        for raw in lines:
            line = raw.strip()
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            parts = [p.strip() for p in line.split(';') if p.strip()]
            commands.extend(parts)
        if not commands:
            self.command_result.emit("error", {
                "message": "脚本为空或仅包含注释",
                "target": self.context_target
            })
            return False
        # 初始化脚本异步状态
        self._script_running = True
        self._script_pending_commands = commands
        self._script_success_count = 0
        self._script_fail_count = 0
        # 启动轮询并立即尝试处理首条命令
        if not self._script_timer.isActive():
            self._script_timer.start()
        self._process_next_script_command()
        return True

    def _is_tree_animation_active(self):
        """检查树视图是否存在任意动画正在播放（包括遍历/搜索、BST/AVL/Huffman）。"""
        try:
            v = getattr(self.tree_controller, 'view', None)
            if v is None:
                return getattr(self.tree_controller, '_bst_build_in_progress', False)
            if hasattr(v, 'traversal_play_timer') and v.traversal_play_timer.isActive():
                return True
            if hasattr(v, 'bst_animation_timer') and v.bst_animation_timer.isActive():
                return True
            if hasattr(v, 'avl_animation_timer') and v.avl_animation_timer.isActive():
                return True
            if hasattr(v, 'huffman_animation_timer') and v.huffman_animation_timer.isActive():
                return True
            return getattr(self.tree_controller, '_bst_build_in_progress', False)
        except Exception:
            return getattr(self.tree_controller, '_bst_build_in_progress', False)

    def _process_next_script_command(self):
        """在无动画冲突时，逐条处理挂起的脚本命令；否则等待动画结束后继续。"""
        if not self._script_running:
            if self._script_timer.isActive():
                self._script_timer.stop()
            return
        # 若树动画仍在播放，暂缓执行
        if self._is_tree_animation_active():
            if not self._script_timer.isActive():
                self._script_timer.start()
            return
        # 无动画冲突，停止轮询以避免忙等待
        if self._script_timer.isActive():
            self._script_timer.stop()
        # 若队列已空，发出完成信号并结束脚本
        if not self._script_pending_commands:
            self.command_result.emit("success", {
                "message": f"脚本执行完成：成功 {self._script_success_count} 条，失败 {self._script_fail_count} 条",
                "result": None,
                "target": self.context_target
            })
            self._script_running = False
            return
        # 取下一条命令执行
        cmd = self._script_pending_commands.pop(0)
        ok = False
        try:
            ok = self.process_command(cmd)
        except Exception:
            ok = False
        if ok:
            self._script_success_count += 1
        else:
            self._script_fail_count += 1
        # 继续轮询执行后续命令（动画开始后将等待其结束）
        if not self._script_timer.isActive():
            self._script_timer.start()