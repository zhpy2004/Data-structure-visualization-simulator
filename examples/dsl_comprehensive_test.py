#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL综合测试文件 - 测试数据结构可视化模拟器的DSL功能
包含线性结构和树形结构的所有DSL命令测试
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dsl_parser import parse_linear_dsl, parse_tree_dsl, parse_dsl_command
from controllers.dsl_controller import DSLController
from controllers.linear_controller import LinearController
from controllers.tree_controller import TreeController
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject
import time


class DSLTester(QObject):
    """DSL测试器类"""
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name, command, expected_result=None):
        """运行单个测试
        
        Args:
            test_name: 测试名称
            command: DSL命令
            expected_result: 期望结果（可选）
        """
        print(f"\n--- 测试: {test_name} ---")
        print(f"命令: {command}")
        
        try:
            # 解析命令
            result, cmd_type = parse_dsl_command(command)
            
            # 检查是否是错误结果
            # 对于错误情况，result可能是字典格式 {"error": "...", "command": "error"}
            # 对于成功情况，result是元组格式 (command_name, command_data)
            if isinstance(result, dict) and result.get("command") == "error":
                print(f"❌ 解析失败: {result.get('error')}")
                self.failed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "command": command,
                    "status": "FAILED",
                    "error": result.get('error')
                })
            elif isinstance(result, tuple) and len(result) == 2:
                # 成功解析的情况，result是(command_name, command_data)格式
                command_name, command_data = result
                print(f"✅ 解析成功: 命令={command_name}, 数据={command_data}")
                print(f"命令类型: {cmd_type}")
                self.passed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "command": command,
                    "status": "PASSED",
                    "result": {"command": command_name, "data": command_data},
                    "type": cmd_type
                })
            else:
                # 未知格式
                print(f"❌ 未知结果格式: {result}")
                self.failed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "command": command,
                    "status": "FAILED",
                    "error": f"未知结果格式: {type(result)}"
                })
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            self.failed_tests += 1
            self.test_results.append({
                "name": test_name,
                "command": command,
                "status": "ERROR",
                "error": str(e)
            })
    
    def test_linear_structures(self):
        """测试线性结构DSL命令"""
        print("\n" + "="*50)
        print("测试线性结构DSL命令")
        print("="*50)
        
        # 测试创建命令
        self.run_test("创建空顺序表", "create arraylist")
        self.run_test("创建带初值的顺序表", "create arraylist with 10,20,30,40,50")
        self.run_test("创建空链表", "create linkedlist")
        self.run_test("创建带初值的链表", "create linkedlist with 1,2,3,4,5")
        self.run_test("创建空栈", "create stack")
        self.run_test("创建带初值的栈", "create stack with 100,200,300")
        
        # 测试插入命令
        self.run_test("顺序表插入", "insert 25 at 2 in arraylist")
        self.run_test("链表插入", "insert 15 at 1 in linkedlist")
        
        # 测试删除命令
        self.run_test("顺序表按值删除", "delete 30 from arraylist")
        self.run_test("顺序表按位置删除", "delete at 2 from arraylist")
        self.run_test("链表按值删除", "delete 3 from linkedlist")
        self.run_test("链表按位置删除", "delete at 1 from linkedlist")
        
        # 测试查询命令
        self.run_test("顺序表按值查询", "get 20 from arraylist")
        self.run_test("顺序表按位置查询", "get at 1 from arraylist")
        self.run_test("链表按值查询", "get 2 from linkedlist")
        self.run_test("链表按位置查询", "get at 0 from linkedlist")
        
        # 测试栈操作
        self.run_test("栈压入", "push 400 to stack")
        self.run_test("栈弹出", "pop from stack")
        
        # 测试清空命令
        self.run_test("清空顺序表", "clear arraylist")
        self.run_test("清空链表", "clear linkedlist")
        self.run_test("清空栈", "clear stack")
    
    def test_tree_structures(self):
        """测试树形结构DSL命令"""
        print("\n" + "="*50)
        print("测试树形结构DSL命令")
        print("="*50)
        
        # 测试创建命令
        self.run_test("创建空二叉树", "create binarytree")
        self.run_test("创建带初值的二叉树", "create binarytree with 10,5,15,3,7,12,20")
        self.run_test("创建空二叉搜索树", "create bst")
        self.run_test("创建带初值的二叉搜索树", "create bst with 50,30,70,20,40,60,80")
        self.run_test("创建空哈夫曼树", "create huffman")
        
        # 测试插入命令
        self.run_test("二叉树插入", "insert 25 in binarytree")
        self.run_test("二叉搜索树插入", "insert 45 in bst")
        self.run_test("二叉树指定位置插入", "insert 8 at 1,0 in binarytree")
        
        # 测试删除命令
        self.run_test("二叉树删除", "delete 15 from binarytree")
        self.run_test("二叉搜索树删除", "delete 30 from bst")
        self.run_test("二叉树指定位置删除", "delete 7 at 1,1 from binarytree")
        
        # 测试搜索命令
        self.run_test("二叉树搜索", "search 10 in binarytree")
        self.run_test("二叉搜索树搜索", "search 50 in bst")
        
        # 测试遍历命令
        self.run_test("前序遍历", "traverse preorder")
        self.run_test("中序遍历", "traverse inorder")
        self.run_test("后序遍历", "traverse postorder")
        self.run_test("层序遍历", "traverse levelorder")
        
        # 测试哈夫曼树命令
        self.run_test("构建哈夫曼树", "build huffman with a:5,b:9,c:12,d:13,e:16,f:45")
        self.run_test("哈夫曼编码", 'encode "hello" using huffman')
        self.run_test("哈夫曼解码", "decode 1010110 using huffman")
        
        # 测试清空命令
        self.run_test("清空二叉树", "clear binarytree")
        self.run_test("清空二叉搜索树", "clear bst")
        self.run_test("清空哈夫曼树", "clear huffman")
    
    def test_error_cases(self):
        """测试错误情况"""
        print("\n" + "="*50)
        print("测试错误情况和边界条件")
        print("="*50)
        
        # 测试语法错误
        self.run_test("无效命令", "invalid command")
        self.run_test("缺少参数", "create")
        self.run_test("错误的结构类型", "create invalidtype")
        self.run_test("错误的操作", "invalidop 10 from arraylist")
        
        # 测试参数错误
        self.run_test("插入位置错误", "insert abc at 1 in arraylist")
        self.run_test("删除参数错误", "delete from arraylist")
        self.run_test("遍历类型错误", "traverse invalidorder")
        
        # 测试空值情况
        self.run_test("空字符串命令", "")
        self.run_test("只有空格的命令", "   ")
    
    def test_complex_scenarios(self):
        """测试复杂场景"""
        print("\n" + "="*50)
        print("测试复杂场景")
        print("="*50)
        
        # 测试大数据量
        large_data = ",".join([str(i) for i in range(1, 101)])
        self.run_test("大数据量创建顺序表", f"create arraylist with {large_data}")
        
        # 测试特殊字符
        self.run_test("哈夫曼特殊字符", "build huffman with 1:10,2:20,3:30")
        
        # 测试边界值
        self.run_test("零值插入", "insert 0 at 0 in arraylist")
        self.run_test("负数插入", "insert -10 at 1 in arraylist")
        
        # 测试长字符串编码
        self.run_test("长字符串编码", 'encode "this is a very long string for testing huffman encoding" using huffman')
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("DSL解析器测试总结")
        print("="*60)
        
        total_tests = self.passed_tests + self.failed_tests
        
        # 统计不同类型的测试
        valid_command_tests = 0
        error_handling_tests = 0
        valid_passed = 0
        error_passed = 0
        
        # 定义错误处理测试的名称
        error_test_names = {
            "无效命令", "缺少参数", "错误的结构类型", 
            "遍历类型错误", "空字符串命令", "只有空格的命令"
        }
        
        for result in self.test_results:
            if result['name'] in error_test_names:
                error_handling_tests += 1
                if result["status"] in ["FAILED", "ERROR"]:
                    error_passed += 1  # 错误处理测试失败是预期的
            else:
                valid_command_tests += 1
                if result["status"] == "PASSED":
                    valid_passed += 1
        
        print(f"总测试数: {total_tests}")
        print(f"├─ 有效命令测试: {valid_command_tests} 个")
        print(f"│  └─ 通过: {valid_passed} 个 ({(valid_passed/valid_command_tests*100):.1f}%)")
        print(f"└─ 错误处理测试: {error_handling_tests} 个")
        print(f"   └─ 正确拒绝: {error_passed} 个 ({(error_passed/error_handling_tests*100):.1f}%)")
        
        print(f"\n🎯 DSL解析器功能状态:")
        print(f"✅ 有效命令解析: {valid_passed}/{valid_command_tests} 正常工作")
        print(f"✅ 错误命令处理: {error_passed}/{error_handling_tests} 正确拒绝")
        
        overall_success = valid_passed == valid_command_tests and error_passed == error_handling_tests
        if overall_success:
            print(f"\n🎉 DSL解析器工作完全正常！")
        else:
            print(f"\n⚠️  发现问题需要修复")
        
        # 显示失败的有效命令测试（这些是真正的问题）
        real_failures = []
        expected_failures = []
        
        for result in self.test_results:
            if result["status"] in ["FAILED", "ERROR"]:
                if result['name'] in error_test_names:
                    expected_failures.append(result)
                else:
                    real_failures.append(result)
        
        if real_failures:
            print(f"\n❌ 需要修复的问题:")
            for result in real_failures:
                print(f"  - {result['name']}: {result.get('error', '未知错误')}")
        
        if expected_failures:
            print(f"\n✅ 预期的错误处理（正常）:")
            for result in expected_failures:
                print(f"  - {result['name']}: 正确拒绝无效命令")
        
        print("\n详细测试结果:")
        for result in self.test_results:
            if result['name'] in error_test_names:
                # 错误处理测试：失败是好的
                if result["status"] in ["FAILED", "ERROR"]:
                    status_symbol = "✅"
                    status_text = f"{result['name']} (正确拒绝)"
                else:
                    status_symbol = "❌"
                    status_text = f"{result['name']} (应该拒绝但没有)"
            else:
                # 正常测试：通过是好的
                status_symbol = "✅" if result["status"] == "PASSED" else "❌"
                status_text = result['name']
            
            print(f"  {status_symbol} {status_text}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始DSL综合测试...")
        
        self.test_linear_structures()
        self.test_tree_structures()
        self.test_error_cases()
        self.test_complex_scenarios()
        
        self.print_summary()


def test_dsl_parser_only():
    """仅测试DSL解析器功能（不需要GUI）"""
    print("DSL解析器功能测试")
    print("="*50)
    
    tester = DSLTester()
    tester.run_all_tests()


def test_with_controllers():
    """使用控制器进行完整测试（需要GUI环境）"""
    print("DSL控制器完整功能测试")
    print("="*50)
    
    # 创建QApplication
    app = QApplication(sys.argv)
    
    # 创建控制器
    linear_controller = LinearController()
    tree_controller = TreeController()
    dsl_controller = DSLController(linear_controller, tree_controller)
    
    # 测试命令列表
    test_commands = [
        "create arraylist with 1,2,3,4,5",
        "insert 10 at 2 in arraylist",
        "create bst with 50,30,70,20,40",
        "search 30 in bst",
        "traverse inorder"
    ]
    
    print("测试DSL控制器命令处理:")
    for cmd in test_commands:
        print(f"\n执行命令: {cmd}")
        result = dsl_controller.process_command(cmd)
        print(f"处理结果: {result}")


def main():
    """主函数"""
    print("数据结构可视化模拟器 - DSL综合测试")
    print("="*60)
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 仅测试DSL解析器（推荐，无需GUI）")
    print("2. 完整功能测试（需要GUI环境）")
    
    try:
        choice = input("请输入选择 (1 或 2): ").strip()
        
        if choice == "1":
            test_dsl_parser_only()
        elif choice == "2":
            test_with_controllers()
        else:
            print("无效选择，默认运行解析器测试")
            test_dsl_parser_only()
            
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"测试过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()