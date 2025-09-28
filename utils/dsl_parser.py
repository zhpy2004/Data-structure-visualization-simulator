#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL解析器 - 用于解析简单的领域特定语言，构建和操作数据结构
"""

from lark import Lark, Transformer, v_args
import re

# 线性结构DSL语法
LINEAR_DSL_GRAMMAR = r"""
    start: command
    
    command: create_cmd
           | insert_cmd
           | delete_cmd
           | get_cmd
           | push_cmd
           | pop_cmd
           | clear_cmd
    
    create_cmd: "create" structure_type ["with" values]
    insert_cmd: "insert" value "at" position "in" structure_name
    delete_cmd: "delete" (value | "at" position) "from" structure_name
    get_cmd: "get" (value | "at" position) "from" structure_name
    push_cmd: "push" value "to" structure_name
    pop_cmd: "pop" "from" structure_name
    clear_cmd: "clear" structure_name
    
    structure_type: "arraylist" | "linkedlist" | "stack"
    structure_name: "arraylist" | "linkedlist" | "stack"
    values: value ("," value)*
    value: NUMBER
    position: NUMBER
    
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

# 树形结构DSL语法
TREE_DSL_GRAMMAR = r"""
    start: command
    
    command: create_cmd
           | insert_cmd
           | delete_cmd
           | search_cmd
           | traverse_cmd
           | build_huffman_cmd
           | encode_cmd
           | decode_cmd
           | clear_cmd
    
    create_cmd: "create" structure_type ["with" values]
    insert_cmd: "insert" value ["at" position] "in" structure_name
    delete_cmd: "delete" value ["at" position] "from" structure_name
    search_cmd: "search" value "in" structure_name
    traverse_cmd: "traverse" traverse_type
    build_huffman_cmd: "build" "huffman" "with" huffman_values
    encode_cmd: "encode" STRING "using" "huffman"
    decode_cmd: "decode" BINARY "using" "huffman"
    clear_cmd: "clear" structure_name
    
    structure_type: "binarytree" | "bst" | "huffman"
    structure_name: "binarytree" | "bst" | "huffman"
    traverse_type: "preorder" | "inorder" | "postorder" | "levelorder"
    values: value ("," value)*
    huffman_values: huffman_value ("," huffman_value)*
    huffman_value: CHAR ":" NUMBER
    value: NUMBER
    position: position_value ("," position_value)*
    position_value: NUMBER
    
    CHAR: /[a-zA-Z0-9]/
    STRING: /"[^"]*"/
    BINARY: /[01]+/
    
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""


class LinearDSLTransformer(Transformer):
    """线性结构DSL转换器"""
    
    @v_args(inline=True)
    def start(self, command):
        return command
    
    @v_args(inline=True)
    def create_cmd(self, structure_type, values=None):
        result = {
            "type": structure_type
        }
        
        if values:
            result["data"] = values
        
        return ("create", result)
    
    @v_args(inline=True)
    def insert_cmd(self, value, position, structure_name):
        return {
            "command": "insert",
            "value": value,
            "position": position,
            "structure_name": structure_name
        }
    
    @v_args(inline=True)
    def delete_cmd(self, target, structure_name):
        result = {
            "command": "delete",
            "structure_name": structure_name
        }
        
        if isinstance(target, tuple) and target[0] == "at":
            result["position"] = target[1]
        else:
            result["value"] = target
        
        return result
    
    @v_args(inline=True)
    def get_cmd(self, target, structure_name):
        result = {
            "command": "get",
            "structure_name": structure_name
        }
        
        if isinstance(target, tuple) and target[0] == "at":
            result["position"] = target[1]
        else:
            result["value"] = target
        
        return result
    
    @v_args(inline=True)
    def push_cmd(self, value, structure_name):
        return {
            "command": "push",
            "value": value,
            "structure_name": structure_name
        }
    
    @v_args(inline=True)
    def pop_cmd(self, structure_name):
        return {
            "command": "pop",
            "structure_name": structure_name
        }
    
    @v_args(inline=True)
    def clear_cmd(self, structure_name):
        return ("clear", {
        })
    
    @v_args(inline=True)
    def structure_type(self, s):
        return str(s)
    
    @v_args(inline=True)
    def structure_name(self, s):
        return str(s)
    
    @v_args(inline=True)
    def values(self, *args):
        return list(args)
    
    @v_args(inline=True)
    def value(self, n):
        return int(n)
    
    @v_args(inline=True)
    def position(self, n):
        return int(n)


class TreeDSLTransformer(Transformer):
    """树形结构DSL转换器"""
    
    @v_args(inline=True)
    def start(self, command):
        return command
    
    @v_args(inline=True)
    def create_cmd(self, structure_type, values=None):
        result = {
            "command": "create",
            "structure_type": structure_type
        }
        
        if values:
            result["values"] = values
        
        return result
    
    @v_args(inline=True)
    def insert_cmd(self, value, position=None, structure_name=None):
        if structure_name is None:
            structure_name = position
            position = None
        
        result = {
            "value": value
        }
        
        if position:
            result["position"] = position
        
        return ("insert", result)
    
    @v_args(inline=True)
    def delete_cmd(self, value, position=None, structure_name=None):
        if structure_name is None:
            structure_name = position
            position = None
        
        result = {
            "value": value
        }
        
        if position:
            result["position"] = position
        
        return ("delete", result)
    
    @v_args(inline=True)
    def search_cmd(self, value, structure_name):
        return ("search", {
            "value": value
        })
    
    @v_args(inline=True)
    def traverse_cmd(self, traverse_type):
        return ("traverse", {
            "traverse_type": traverse_type
        })
    
    @v_args(inline=True)
    def build_huffman_cmd(self, huffman_values):
        return ("build_huffman", {
            "frequencies": huffman_values
        })
    
    @v_args(inline=True)
    def encode_cmd(self, text, _):
        # 去除引号
        text = text[1:-1] if text.startswith('"') and text.endswith('"') else text
        return ("encode", {
            "text": text
        })
    
    @v_args(inline=True)
    def decode_cmd(self, binary, _):
        return ("decode", {
            "binary": binary
        })
    
    @v_args(inline=True)
    def clear_cmd(self, structure_name):
        return ("clear", {})
    
    @v_args(inline=True)
    def structure_type(self, s):
        return str(s)
    
    @v_args(inline=True)
    def structure_name(self, s):
        return str(s)
    
    @v_args(inline=True)
    def traverse_type(self, t):
        return str(t)
    
    @v_args(inline=True)
    def values(self, *args):
        return list(args)
    
    @v_args(inline=True)
    def huffman_values(self, *args):
        return dict(args)
    
    @v_args(inline=True)
    def huffman_value(self, char, freq):
        return (char, int(freq))
    
    @v_args(inline=True)
    def value(self, n):
        return int(n)
    
    @v_args(inline=True)
    def position(self, *args):
        return list(args)
    
    @v_args(inline=True)
    def position_value(self, n):
        return int(n)
    
    @v_args(inline=True)
    def CHAR(self, c):
        return str(c)
    
    @v_args(inline=True)
    def STRING(self, s):
        return str(s)
    
    @v_args(inline=True)
    def BINARY(self, b):
        return str(b)


def parse_linear_dsl(command_str):
    """解析线性结构DSL命令
    
    Args:
        command_str: DSL命令字符串
    
    Returns:
        解析后的命令对象
    """
    try:
        parser = Lark(LINEAR_DSL_GRAMMAR, parser='lalr', transformer=LinearDSLTransformer())
        return parser.parse(command_str)
    except Exception as e:
        return ("error", {
            "error": f"解析错误: {str(e)}"
        })


def parse_tree_dsl(command_str):
    """解析树形结构DSL命令
    
    Args:
        command_str: DSL命令字符串
    
    Returns:
        解析后的命令对象
    """
    try:
        # 处理带有前缀的命令，如"tree.binary_tree.traverse preorder"
        if command_str.startswith("tree."):
            parts = command_str.split(".", 2)
            if len(parts) >= 3:
                # 提取实际命令部分
                structure_type = parts[1]  # 如"binary_tree"
                command_part = parts[2]    # 如"traverse preorder"
                
                # 处理特殊命令
                if command_part.startswith("traverse"):
                    traverse_type = command_part.split(" ", 1)[1] if " " in command_part else ""
                    return ("traverse", {
                        "traverse_type": traverse_type
                    })
                elif command_part.startswith("create"):
                    # 处理create命令
                    data_part = command_part.split(" ", 1)[1] if " " in command_part else ""
                    data = [int(x.strip()) for x in data_part.split(",")] if data_part else []
                    return ("create", {
                        "type": structure_type,
                        "data": data
                    })
                elif command_part.startswith("insert"):
                    # 处理insert命令
                    value_part = command_part.split(" ", 1)[1] if " " in command_part else ""
                    value = int(value_part) if value_part else 0
                    return ("insert", {
                        "value": value
                    })
                elif command_part.startswith("search"):
                    # 处理search命令
                    value_part = command_part.split(" ", 1)[1] if " " in command_part else ""
                    value = int(value_part) if value_part else 0
                    return ("search", {
                        "value": value
                    })
                elif command_part.startswith("remove") or command_part.startswith("delete"):
                    # 处理remove/delete命令
                    value_part = command_part.split(" ", 1)[1] if " " in command_part else ""
                    value = int(value_part) if value_part else 0
                    return ("delete", {
                        "value": value
                    })
        
        # 如果不是带前缀的命令，使用原有解析方式
        parser = Lark(TREE_DSL_GRAMMAR, parser='lalr', transformer=TreeDSLTransformer())
        return parser.parse(command_str)
    except Exception as e:
        return {
            "error": f"解析错误: {str(e)}",
            "command": "error"
        }


def is_linear_command(command_str):
    """判断是否为线性结构命令
    
    Args:
        command_str: 命令字符串
    
    Returns:
        是否为线性结构命令
    """
    linear_keywords = ["arraylist", "linkedlist", "stack"]
    return any(keyword in command_str.lower() for keyword in linear_keywords)


def is_tree_command(command_str):
    """判断是否为树形结构命令
    
    Args:
        command_str: 命令字符串
    
    Returns:
        是否为树形结构命令
    """
    tree_keywords = ["binarytree", "bst", "huffman", "preorder", "inorder", "postorder", "levelorder"]
    return any(keyword in command_str.lower() for keyword in tree_keywords)


def parse_dsl_command(command_str):
    """解析DSL命令
    
    Args:
        command_str: 命令字符串
    
    Returns:
        解析后的命令对象和类型
    """
    if is_linear_command(command_str):
        return parse_linear_dsl(command_str), "linear"
    elif is_tree_command(command_str):
        return parse_tree_dsl(command_str), "tree"
    else:
        return {
            "error": "无法识别的命令类型",
            "command": "error"
        }, "unknown"