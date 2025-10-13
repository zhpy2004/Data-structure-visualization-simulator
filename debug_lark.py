#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lark import Lark, Transformer, v_args, Token

# 测试语法 - 模拟我们的DSL
TEST_GRAMMAR = r"""
    start: command
    command: "create" structure_type ["with" values]
    structure_type: "arraylist" | "linkedlist"
    values: value ("," value)*
    value: NUMBER
    
    %import common.NUMBER
    %import common.WS
    %ignore WS
"""

class TestTransformer(Transformer):
    def start(self, args):
        print(f"start args: {args}, types: {[type(arg) for arg in args]}")
        return args[0]
    
    def command(self, args):
        print(f"command args: {args}, types: {[type(arg) for arg in args]}")
        # args[0] 是 "create" token
        # args[1] 是 structure_type 的结果
        # args[2] 是 values 的结果（如果存在）
        result = {"command": "create", "structure_type": args[1]}
        if len(args) > 2:
            result["values"] = args[2]
        return result
    
    def structure_type(self, args):
        print(f"structure_type args: {args}, types: {[type(arg) for arg in args]}")
        # 对于由单个终端符号组成的非终端符号，args[0] 是Token
        return str(args[0])
    
    def values(self, args):
        print(f"values args: {args}, types: {[type(arg) for arg in args]}")
        return [item for item in args]
    
    def value(self, args):
        print(f"value args: {args}, types: {[type(arg) for arg in args]}")
        return int(args[0])

class TestTransformerInline(Transformer):
    @v_args(inline=True)
    def start(self, command):
        print(f"start_inline command: {command}, type: {type(command)}")
        return command
    
    @v_args(inline=True)
    def command(self, create_token, structure_type, values=None):
        print(f"command_inline create_token: {create_token}, type: {type(create_token)}")
        print(f"command_inline structure_type: {structure_type}, type: {type(structure_type)}")
        print(f"command_inline values: {values}, type: {type(values)}")
        result = {"command": "create", "structure_type": structure_type}
        if values:
            result["values"] = values
        return result
    
    @v_args(inline=True)
    def structure_type(self, token):
        print(f"structure_type_inline token: {token}, type: {type(token)}")
        return str(token)
    
    def values(self, args):
        print(f"values_inline args: {args}, types: {[type(arg) for arg in args]}")
        return [item for item in args]
    
    @v_args(inline=True)
    def value(self, token):
        print(f"value_inline token: {token}, type: {type(token)}")
        return int(token)

def test_lark():
    print("=== 测试普通转换器 ===")
    parser1 = Lark(TEST_GRAMMAR, parser='lalr', transformer=TestTransformer())
    
    try:
        result = parser1.parse("create arraylist")
        print(f"Final result: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== 测试inline转换器 ===")
    parser2 = Lark(TEST_GRAMMAR, parser='lalr', transformer=TestTransformerInline())
    
    try:
        result = parser2.parse("create arraylist")
        print(f"Final result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_lark()