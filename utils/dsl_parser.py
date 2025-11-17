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
           | peek_cmd
           | clear_cmd
    
    create_cmd: "create" STRUCTURE_TYPE ["with" values] ["size" NUMBER]
    insert_cmd: "insert" value "at" position "in" STRUCTURE_NAME
    delete_cmd: "delete" delete_target "from" STRUCTURE_NAME
    get_cmd: "get" get_target "from" STRUCTURE_NAME
    push_cmd: "push" value "to" STRUCTURE_NAME
    pop_cmd: "pop" "from" STRUCTURE_NAME
    peek_cmd: "peek" STRUCTURE_NAME
    clear_cmd: "clear" STRUCTURE_NAME
    
    delete_target: value | AT position
    get_target: value | AT position
    
    values: value ("," value)*
    value: NUMBER
    position: NUMBER
    
    STRUCTURE_TYPE: "arraylist" | "linkedlist" | "stack"
    STRUCTURE_NAME: "arraylist" | "linkedlist" | "stack"
    AT: "at"
    
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
           | build_bst_cmd
           | build_avl_cmd
           | encode_cmd
           | decode_cmd
           | clear_cmd
    
    create_cmd: "create" STRUCTURE_TYPE ["with" values]
    insert_cmd: "insert" value ["at" position] "in" STRUCTURE_NAME
    delete_cmd: "delete" value ["at" position] "from" STRUCTURE_NAME
    search_cmd: "search" value "in" STRUCTURE_NAME
    traverse_cmd: "traverse" TRAVERSE_TYPE ["in" STRUCTURE_NAME]
    build_huffman_cmd: "build" "huffman" "with" huffman_values
    build_bst_cmd: "build" "bst" "with" values
    build_avl_cmd: "build" "avl" "with" values
    encode_cmd: "encode" STRING "using" HUFFMAN_KEYWORD
    decode_cmd: "decode" BINARY "using" HUFFMAN_KEYWORD
    clear_cmd: "clear" STRUCTURE_NAME
    
    values: value ("," value)*
    huffman_values: huffman_value ("," huffman_value)*
    huffman_value: CHAR ":" NUMBER
    value: NUMBER
    position: position_value ("," position_value)*
    position_value: NUMBER
    
    STRUCTURE_TYPE: "binarytree" | "bst" | "huffman" | "avl"
    STRUCTURE_NAME: "binarytree" | "bst" | "huffman" | "avl"
    TRAVERSE_TYPE: "preorder" | "inorder" | "postorder" | "levelorder"
    HUFFMAN_KEYWORD: "huffman"
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
        # 直接返回命令元组，而不是Tree对象
        return command
    
    @v_args(inline=True)
    def command(self, cmd):
        # 直接返回命令元组，而不是Tree对象
        return cmd
    
    @v_args(inline=True)
    def create_cmd(self, structure_type, *rest):
        values = []
        capacity = None
        for item in rest:
            if isinstance(item, list):
                values = item
            else:
                # 兼容 size NUMBER 的 Token，转为 int
                try:
                    capacity = int(item)
                except Exception:
                    pass
        return ("create", {
            "structure_type": str(structure_type),
            "values": values,
            "capacity": capacity
        })
    
    @v_args(inline=True)
    def insert_cmd(self, value, position, structure_name):
        return ("insert", {
            "value": value,
            "position": position,
            "structure_name": str(structure_name)
        })
    
    @v_args(inline=True)
    def delete_cmd(self, target, structure_name):
        # 为了避免下游误判，显式拆分 position/value 两种目标
        pos = None
        val = None
        try:
            if isinstance(target, dict):
                if target.get("type") == "position":
                    pos = target.get("value")
                elif target.get("type") == "value":
                    val = target.get("value")
        except Exception:
            pass
        return ("delete", {
            "target": target,
            "position": pos,
            "value": val,
            "structure_name": str(structure_name)
        })
    
    @v_args(inline=True)
    def get_cmd(self, target, structure_name):
        return ("get", {
            "target": target,
            "structure_name": str(structure_name)
        })
    
    @v_args(inline=True)
    def delete_target(self, *args):
        # 显式检测 AT 令牌，避免将 "delete at X" 误判为按值删除
        try:
            if len(args) == 2 and hasattr(args[0], 'type') and str(getattr(args[0], 'type', '')) == 'AT':
                return {"type": "position", "value": args[1]}
        except Exception:
            pass
        return {"type": "value", "value": args[0]}
    
    @v_args(inline=True)
    def get_target(self, *args):
        try:
            if len(args) == 2 and hasattr(args[0], 'type') and str(getattr(args[0], 'type', '')) == 'AT':
                return {"type": "position", "value": args[1]}
        except Exception:
            pass
        return {"type": "value", "value": args[0]}
    
    @v_args(inline=True)
    def push_cmd(self, value, structure_name):
        return ("push", {
            "value": value,
            "structure_name": str(structure_name)
        })
    
    @v_args(inline=True)
    def pop_cmd(self, structure_name):
        return ("pop", {
            "structure_name": str(structure_name)
        })
    
    @v_args(inline=True)
    def peek_cmd(self, structure_name):
        return ("peek", {
            "structure_name": str(structure_name)
        })
    
    @v_args(inline=True)
    def clear_cmd(self, structure_name):
        return ("clear", {
            "structure_name": str(structure_name)
        })
    
    def values(self, args):
        return [item for item in args]
    
    @v_args(inline=True)
    def value(self, token):
        return int(token)
    
    @v_args(inline=True)
    def position(self, token):
        return int(token)


class TreeDSLTransformer(Transformer):
    """树形结构DSL转换器"""
    
    @v_args(inline=True)
    def start(self, command):
        # 直接返回命令元组，而不是Tree对象
        return command
    
    @v_args(inline=True)
    def command(self, cmd):
        # 直接返回命令元组，而不是Tree对象
        return cmd
    
    @v_args(inline=True)
    def create_cmd(self, structure_type, values=None):
        return ("create", {
            "structure_type": str(structure_type),
            "values": values if values else []
        })
    
    @v_args(inline=True)
    def insert_cmd(self, *children):
        # children can be:
        # [value, structure_name] when position is omitted
        # [value, position(list), structure_name] when position is present
        value = children[0] if len(children) >= 1 else None
        position = None
        structure_name = None
        if len(children) == 3:
            position = children[1]
            structure_name = children[2]
        elif len(children) == 2:
            second = children[1]
            # position rule returns a list; structure_name is a Token
            position = second if isinstance(second, list) else None
            structure_name = None if isinstance(second, list) else second
        return ("insert", {
            "value": value,
            "position": position,
            "structure_name": str(structure_name) if structure_name else None
        })
    
    @v_args(inline=True)
    def delete_cmd(self, *children):
        # children can be:
        # [value, structure_name] when position is omitted
        # [value, position(list), structure_name] when position is present
        value = children[0] if len(children) >= 1 else None
        position = None
        structure_name = None
        if len(children) == 3:
            position = children[1]
            structure_name = children[2]
        elif len(children) == 2:
            second = children[1]
            position = second if isinstance(second, list) else None
            structure_name = None if isinstance(second, list) else second
        return ("delete", {
            "value": value,
            "position": position,
            "structure_name": str(structure_name) if structure_name else None
        })
    
    @v_args(inline=True)
    def search_cmd(self, value, structure_name):
        return ("search", {"value": value, "structure_name": str(structure_name)})
    
    @v_args(inline=True)
    def traverse_cmd(self, traverse_type, structure_name=None):
        return ("traverse", {"traverse_type": str(traverse_type), "structure_name": str(structure_name) if structure_name else None})
    
    @v_args(inline=True)
    def build_huffman_cmd(self, huffman_values):
        return ("build_huffman", {"values": huffman_values})
    
    @v_args(inline=True)
    def build_bst_cmd(self, values):
        return ("build_bst", {"values": values})
    
    @v_args(inline=True)
    def build_avl_cmd(self, values):
        return ("build_avl", {"values": values})
    
    @v_args(inline=True)
    def encode_cmd(self, text, huffman_keyword):
        return ("encode", {
            "text": str(text).strip('"'),  # 移除引号
            "huffman": str(huffman_keyword)
        })
    
    @v_args(inline=True)
    def decode_cmd(self, binary, huffman_keyword):
        return ("decode", {"binary": str(binary), "huffman": str(huffman_keyword)})
    
    @v_args(inline=True)
    def clear_cmd(self, structure_name):
        return ("clear", {
            "structure_name": str(structure_name)
        })
    
    def values(self, args):
        return [item for item in args]
    
    def huffman_values(self, args):
        return dict(args)
    
    @v_args(inline=True)
    def huffman_value(self, char, freq):
        return (char, int(freq))
    
    @v_args(inline=True)
    def value(self, token):
        return int(token)
    
    def position(self, args):
        return [item for item in args]
    
    @v_args(inline=True)
    def position_value(self, token):
        return int(token)


def parse_linear_dsl(command_str):
    """解析线性结构DSL命令
    
    Args:
        command_str: DSL命令字符串
    
    Returns:
        解析后的命令对象
    """
    try:
        parser = Lark(LINEAR_DSL_GRAMMAR, parser='lalr')
        tree = parser.parse(command_str)
        transformer = LinearDSLTransformer()
        return transformer.transform(tree)
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
        # 处理带有前缀的命令，如"tree.binary_tree.insert 5 at 0,1"
        if command_str.startswith("tree."):
            parts = command_str.split(".", 2)
            if len(parts) >= 3:
                structure_type = parts[1]  # 如 "binary_tree" / "bst" / "huffman"
                command_part = parts[2].strip()
                lower_cmd = command_part.lower()
                
                # traverse（不需要结构名）
                if lower_cmd.startswith("traverse"):
                    # 仅支持普通二叉树（binary_tree）
                    if structure_type != "binary_tree":
                        return ("error", {"error": "遍历命令仅支持普通二叉树（binarytree）"})
                    traverse_type = command_part.split(" ", 1)[1].strip() if " " in command_part else ""
                    return ("traverse", {
                        "structure_name": structure_type,
                        "traverse_type": traverse_type
                    })
                # create：返回与 DSLController 兼容的键
                elif lower_cmd.startswith("create"):
                    data_part = command_part.split(" ", 1)[1].strip() if " " in command_part else ""
                    values = [int(x.strip()) for x in data_part.split(",")] if data_part else []
                    return ("create", {
                        "structure_type": structure_type,
                        "values": values
                    })
                # insert：支持可选 at path
                elif lower_cmd.startswith("insert"):
                    # 格式：insert <num> [at <a,b,c>]
                    m = re.match(r"insert\s+(\d+)(?:\s+at\s+([0-9,\s]+))?", command_part, re.IGNORECASE)
                    if not m:
                        return ("error", {"error": "无法解析 insert 命令"})
                    value = int(m.group(1))
                    pos = m.group(2)
                    position = None
                    if pos:
                        position = [int(x.strip()) for x in pos.split(",") if x.strip() != ""]
                    return ("insert", {
                        "structure_name": structure_type,
                        "value": value,
                        "position": position
                    })
                # search：需要结构名和值
                elif lower_cmd.startswith("search"):
                    m = re.match(r"search\s+(\d+)", command_part, re.IGNORECASE)
                    if not m:
                        return ("error", {"error": "无法解析 search 命令"})
                    value = int(m.group(1))
                    return ("search", {
                        "structure_name": structure_type,
                        "value": value
                    })
                # delete/remove：支持可选 at path
                elif lower_cmd.startswith("remove") or lower_cmd.startswith("delete"):
                    m = re.match(r"(?:remove|delete)\s+(\d+)(?:\s+at\s+([0-9,\s]+))?", command_part, re.IGNORECASE)
                    if not m:
                        return ("error", {"error": "无法解析 delete 命令"})
                    value = int(m.group(1))
                    pos = m.group(2)
                    position = None
                    if pos:
                        position = [int(x.strip()) for x in pos.split(",") if x.strip() != ""]
                    return ("delete", {
                        "structure_name": structure_type,
                        "value": value,
                        "position": position
                    })
                # clear：按结构名前缀清空
                elif lower_cmd.startswith("clear"):
                    return ("clear", {"structure_name": structure_type})
        
        # 如果不是带前缀的命令，使用原有解析方式（语法树）
        parser = Lark(TREE_DSL_GRAMMAR, parser='lalr')
        tree = parser.parse(command_str)
        transformer = TreeDSLTransformer()
        return transformer.transform(tree)
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
    s = command_str.lower().strip()
    if s.startswith("tree."):
        return True
    tree_keywords = ["binarytree", "bst", "huffman", "avl", "preorder", "inorder", "postorder", "levelorder", "traverse"]
    return any(keyword in s for keyword in tree_keywords)


def parse_dsl_command(command_str):
    """解析DSL命令
    
    Args:
        command_str: 命令字符串
    
    Returns:
        解析后的命令对象和类型
    """
    s = command_str.strip().lower()
    # 全局清除：仅 "clear" 时不区分结构类型
    if s == "clear":
        return ("clear_all", {}), "global"
    
    if is_linear_command(command_str):
        return parse_linear_dsl(command_str), "linear"
    elif is_tree_command(command_str):
        return parse_tree_dsl(command_str), "tree"
    else:
        return {
            "error": "无法识别的命令类型",
            "command": "error"
        }, "unknown"