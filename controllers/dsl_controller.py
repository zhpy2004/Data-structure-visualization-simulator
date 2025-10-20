#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL控制器 - 用于处理DSL命令并连接UI与数据结构模型
"""

from PyQt5.QtCore import QObject, pyqtSignal
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
    
    def process_command(self, command_str):
        """处理DSL命令
        
        Args:
            command_str: DSL命令字符串
            
        Returns:
            处理结果
        """
        # 解析命令
        command, command_type = parse_dsl_command(command_str)
        
        # 检查是否有解析错误
        if command.get("command") == "error":
            self.command_result.emit("error", {
                "message": command.get("error", "未知错误")
            })
            return False
        
        # 根据命令类型分发到相应的控制器
        if command_type == "linear":
            return self._process_linear_command(command)
        elif command_type == "tree":
            return self._process_tree_command(command)
        else:
            self.command_result.emit("error", {
                "message": "无法识别的命令类型"
            })
            return False
    
    def _process_linear_command(self, command):
        """处理线性结构命令
        
        Args:
            command: 解析后的命令对象
            
        Returns:
            处理结果
        """
        if not self.linear_controller:
            self.command_result.emit("error", {
                "message": "线性结构控制器未初始化"
            })
            return False
        
        cmd_type = command.get("command")
        
        try:
            if cmd_type == "create":
                structure_type = command.get("structure_type")
                values = command.get("values", [])
                
                # 转换结构类型
                if structure_type == "arraylist":
                    structure_type = "array_list"
                elif structure_type == "linkedlist":
                    structure_type = "linked_list"
                
                result = self.linear_controller.create_structure(structure_type, values)
                self.command_result.emit("success", {
                    "message": f"成功创建{structure_type}",
                    "result": result
                })
                
            elif cmd_type == "insert":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                
                # 转换结构类型
                if structure_name == "arraylist":
                    structure_name = "array_list"
                elif structure_name == "linkedlist":
                    structure_name = "linked_list"
                
                result = self.linear_controller.insert_item(structure_name, value, position)
                self.command_result.emit("success", {
                    "message": f"成功在{structure_name}的位置{position}插入值{value}",
                    "result": result
                })
                
            elif cmd_type == "delete":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                
                # 转换结构类型
                if structure_name == "arraylist":
                    structure_name = "array_list"
                elif structure_name == "linkedlist":
                    structure_name = "linked_list"
                
                if position is not None:
                    result = self.linear_controller.remove_at(structure_name, position)
                    self.command_result.emit("success", {
                        "message": f"成功从{structure_name}的位置{position}删除元素",
                        "result": result
                    })
                else:
                    result = self.linear_controller.remove_item(structure_name, value)
                    self.command_result.emit("success", {
                        "message": f"成功从{structure_name}中删除值{value}",
                        "result": result
                    })
                
            elif cmd_type == "get":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                
                # 转换结构类型
                if structure_name == "arraylist":
                    structure_name = "array_list"
                elif structure_name == "linkedlist":
                    structure_name = "linked_list"
                
                if position is not None:
                    result = self.linear_controller.get_at(structure_name, position)
                    self.command_result.emit("success", {
                        "message": f"成功获取{structure_name}的位置{position}的元素",
                        "result": result
                    })
                else:
                    result = self.linear_controller.find_item(structure_name, value)
                    self.command_result.emit("success", {
                        "message": f"成功在{structure_name}中查找值{value}",
                        "result": result
                    })
                
            elif cmd_type == "push":
                structure_name = command.get("structure_name")
                value = command.get("value")
                
                result = self.linear_controller.push_item(structure_name, value)
                self.command_result.emit("success", {
                    "message": f"成功将值{value}压入{structure_name}",
                    "result": result
                })
                
            elif cmd_type == "pop":
                structure_name = command.get("structure_name")
                
                result = self.linear_controller.pop_item(structure_name)
                self.command_result.emit("success", {
                    "message": f"成功从{structure_name}弹出元素",
                    "result": result
                })
                
            elif cmd_type == "clear":
                structure_name = command.get("structure_name")
                
                # 转换结构类型
                if structure_name == "arraylist":
                    structure_name = "array_list"
                elif structure_name == "linkedlist":
                    structure_name = "linked_list"
                
                result = self.linear_controller.clear_structure(structure_name)
                self.command_result.emit("success", {
                    "message": f"成功清空{structure_name}",
                    "result": result
                })
                
            else:
                self.command_result.emit("error", {
                    "message": f"未知的线性结构命令: {cmd_type}"
                })
                return False
            
            return True
            
        except Exception as e:
            self.command_result.emit("error", {
                "message": f"处理线性结构命令出错: {str(e)}"
            })
            return False
    
    def _process_tree_command(self, command):
        """处理树形结构命令
        
        Args:
            command: 解析后的命令对象
            
        Returns:
            处理结果
        """
        if not self.tree_controller:
            self.command_result.emit("error", {
                "message": "树形结构控制器未初始化"
            })
            return False
        
        cmd_type = command.get("command")
        
        try:
            if cmd_type == "create":
                structure_type = command.get("structure_type")
                values = command.get("values", [])
                
                # 转换结构类型
                if structure_type == "binarytree":
                    structure_type = "binary_tree"
                
                result = self.tree_controller.create_structure(structure_type, values)
                self.command_result.emit("success", {
                    "message": f"成功创建{structure_type}",
                    "result": result
                })
                
            elif cmd_type == "insert":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                
                # 转换结构类型
                if structure_name == "binarytree":
                    structure_name = "binary_tree"
                
                result = self.tree_controller.insert_node(structure_name, value, position)
                self.command_result.emit("success", {
                    "message": f"成功在{structure_name}中插入值{value}",
                    "result": result
                })
                
            elif cmd_type == "delete":
                structure_name = command.get("structure_name")
                value = command.get("value")
                position = command.get("position")
                
                # 转换结构类型
                if structure_name == "binarytree":
                    structure_name = "binary_tree"
                
                result = self.tree_controller.remove_node(structure_name, value, position)
                self.command_result.emit("success", {
                    "message": f"成功从{structure_name}中删除值{value}",
                    "result": result
                })
                
            elif cmd_type == "search":
                structure_name = command.get("structure_name")
                value = command.get("value")
                
                # 转换结构类型
                if structure_name == "binarytree":
                    structure_name = "binary_tree"
                
                result = self.tree_controller.search_node(structure_name, value)
                self.command_result.emit("success", {
                    "message": f"成功在{structure_name}中搜索值{value}",
                    "result": result
                })
                
            elif cmd_type == "traverse":
                structure_name = command.get("structure_name")
                traverse_type = command.get("traverse_type")
                
                # 转换结构类型
                if structure_name == "binarytree":
                    structure_name = "binary_tree"
                
                result = self.tree_controller.traverse_tree(structure_name, traverse_type)
                self.command_result.emit("success", {
                    "message": f"成功以{traverse_type}方式遍历{structure_name}",
                    "result": result
                })
                
            elif cmd_type == "build_huffman":
                values = command.get("values", {})
                
                result = self.tree_controller.create_structure("huffman_tree", values)
                self.command_result.emit("success", {
                    "message": "成功构建哈夫曼树",
                    "result": result
                })
                
            elif cmd_type == "encode":
                text = command.get("text")
                
                result = self.tree_controller.encode_text(text)
                self.command_result.emit("success", {
                    "message": f"成功编码文本: {text}",
                    "result": result
                })
                
            elif cmd_type == "decode":
                binary = command.get("binary")
                
                result = self.tree_controller.decode_text(binary)
                self.command_result.emit("success", {
                    "message": f"成功解码: {binary}",
                    "result": result
                })
                
            elif cmd_type == "clear":
                structure_name = command.get("structure_name")
                
                # 转换结构类型
                if structure_name == "binarytree":
                    structure_name = "binary_tree"
                
                result = self.tree_controller.clear_structure(structure_name)
                self.command_result.emit("success", {
                    "message": f"成功清空{structure_name}",
                    "result": result
                })
                
            else:
                self.command_result.emit("error", {
                    "message": f"未知的树形结构命令: {cmd_type}"
                })
                return False
            
            return True
            
        except Exception as e:
            self.command_result.emit("error", {
                "message": f"处理树形结构命令出错: {str(e)}"
            })
            return False