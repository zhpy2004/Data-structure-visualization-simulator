#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL工作功能测试文件 - 测试当前能够正常工作的DSL功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dsl_parser import parse_linear_dsl, parse_tree_dsl, parse_dsl_command


def test_working_dsl_features():
    """测试当前能够正常工作的DSL功能"""
    print("数据结构可视化模拟器 - DSL工作功能测试")
    print("="*60)
    
    working_tests = []
    failed_tests = []
    
    def run_test(name, command, parser_func):
        """运行单个测试"""
        print(f"\n测试: {name}")
        print(f"命令: {command}")
        
        try:
            result = parser_func(command)
            
            if isinstance(result, tuple) and result[0] == "error":
                print(f"❌ 失败: {result[1].get('error', '未知错误')}")
                failed_tests.append((name, command, result[1].get('error', '未知错误')))
            else:
                print(f"✅ 成功: {result}")
                working_tests.append((name, command, result))
                
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            failed_tests.append((name, command, str(e)))
    
    # 测试哈夫曼树相关功能（这些在之前的测试中成功了）
    print("\n" + "="*40)
    print("测试哈夫曼树DSL功能")
    print("="*40)
    
    run_test("构建哈夫曼树", "build huffman with a:5,b:9,c:12,d:13,e:16,f:45", parse_tree_dsl)
    run_test("哈夫曼数字字符", "build huffman with 1:10,2:20,3:30", parse_tree_dsl)
    
    # 测试一些基本的语法解析
    print("\n" + "="*40)
    print("测试基本语法解析")
    print("="*40)
    
    # 尝试一些简单的命令
    simple_commands = [
        ("简单遍历命令", "traverse preorder", parse_tree_dsl),
        ("简单遍历命令2", "traverse inorder", parse_tree_dsl),
        ("简单遍历命令3", "traverse postorder", parse_tree_dsl),
        ("简单遍历命令4", "traverse levelorder", parse_tree_dsl),
    ]
    
    for name, cmd, parser in simple_commands:
        run_test(name, cmd, parser)
    
    # 测试统一解析器的命令识别
    print("\n" + "="*40)
    print("测试统一解析器命令识别")
    print("="*40)
    
    unified_commands = [
        "create arraylist with 1,2,3",
        "push 100 to stack",
        "create binarytree with 10,5,15",
        "traverse inorder",
        "build huffman with a:5,b:9"
    ]
    
    for cmd in unified_commands:
        print(f"\n测试统一解析: {cmd}")
        try:
            result, cmd_type = parse_dsl_command(cmd)
            print(f"✅ 识别为: {cmd_type}")
            print(f"解析结果: {result}")
        except Exception as e:
            print(f"❌ 解析失败: {str(e)}")
    
    # 打印总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    total_tests = len(working_tests) + len(failed_tests)
    success_rate = (len(working_tests) / total_tests * 100) if total_tests > 0 else 0
    
    print(f"总测试数: {total_tests}")
    print(f"成功测试: {len(working_tests)}")
    print(f"失败测试: {len(failed_tests)}")
    print(f"成功率: {success_rate:.2f}%")
    
    if working_tests:
        print("\n✅ 工作正常的功能:")
        for name, cmd, result in working_tests:
            print(f"  - {name}: {cmd}")
    
    if failed_tests:
        print("\n❌ 需要修复的功能:")
        for name, cmd, error in failed_tests:
            print(f"  - {name}: {cmd}")
            print(f"    错误: {error}")


def demonstrate_working_features():
    """演示当前工作的DSL功能"""
    print("\n" + "="*60)
    print("DSL功能演示")
    print("="*60)
    
    print("\n1. 哈夫曼树构建功能:")
    print("   命令: build huffman with a:5,b:9,c:12,d:13,e:16,f:45")
    try:
        result = parse_tree_dsl("build huffman with a:5,b:9,c:12,d:13,e:16,f:45")
        print(f"   结果: {result}")
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n2. 遍历命令功能:")
    traversal_types = ["preorder", "inorder", "postorder", "levelorder"]
    for t_type in traversal_types:
        cmd = f"traverse {t_type}"
        print(f"   命令: {cmd}")
        try:
            result = parse_tree_dsl(cmd)
            print(f"   结果: {result}")
        except Exception as e:
            print(f"   错误: {e}")
    
    print("\n3. 命令类型识别功能:")
    test_commands = [
        "create arraylist with 1,2,3",
        "traverse inorder",
        "build huffman with a:5,b:9"
    ]
    
    for cmd in test_commands:
        print(f"   命令: {cmd}")
        try:
            result, cmd_type = parse_dsl_command(cmd)
            print(f"   类型: {cmd_type}")
        except Exception as e:
            print(f"   错误: {e}")


if __name__ == "__main__":
    test_working_dsl_features()
    demonstrate_working_features()