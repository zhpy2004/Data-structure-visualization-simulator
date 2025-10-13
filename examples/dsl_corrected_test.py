#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL修正测试文件 - 使用正确的DSL语法测试数据结构可视化模拟器
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.dsl_parser import parse_linear_dsl, parse_tree_dsl, parse_dsl_command
from PyQt5.QtCore import QObject


class CorrectedDSLTester(QObject):
    """修正的DSL测试器类"""
    
    def __init__(self):
        super().__init__()
        self.test_results = []
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_test(self, test_name, command, parser_func=None):
        """运行单个测试
        
        Args:
            test_name: 测试名称
            command: DSL命令
            parser_func: 指定的解析函数
        """
        print(f"\n--- 测试: {test_name} ---")
        print(f"命令: {command}")
        
        try:
            if parser_func:
                result = parser_func(command)
            else:
                result, cmd_type = parse_dsl_command(command)
            
            if isinstance(result, tuple) and result[0] == "error":
                print(f"❌ 解析失败: {result[1].get('error', '未知错误')}")
                self.failed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "command": command,
                    "status": "FAILED",
                    "error": result[1].get('error', '未知错误')
                })
            elif hasattr(result, 'get') and result.get("command") == "error":
                print(f"❌ 解析失败: {result.get('error', '未知错误')}")
                self.failed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "command": command,
                    "status": "FAILED",
                    "error": result.get('error', '未知错误')
                })
            else:
                print(f"✅ 解析成功: {result}")
                self.passed_tests += 1
                self.test_results.append({
                    "name": test_name,
                    "command": command,
                    "status": "PASSED",
                    "result": result
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
    
    def test_linear_structures_correct(self):
        """测试线性结构DSL命令（使用正确语法）"""
        print("\n" + "="*50)
        print("测试线性结构DSL命令（正确语法）")
        print("="*50)
        
        # 测试创建命令
        self.run_test("创建空顺序表", "create arraylist", parse_linear_dsl)
        self.run_test("创建带初值的顺序表", "create arraylist with 10,20,30,40,50", parse_linear_dsl)
        self.run_test("创建空链表", "create linkedlist", parse_linear_dsl)
        self.run_test("创建带初值的链表", "create linkedlist with 1,2,3,4,5", parse_linear_dsl)
        self.run_test("创建空栈", "create stack", parse_linear_dsl)
        self.run_test("创建带初值的栈", "create stack with 100,200,300", parse_linear_dsl)
        
        # 测试插入命令
        self.run_test("顺序表插入", "insert 25 at 2 in arraylist", parse_linear_dsl)
        self.run_test("链表插入", "insert 15 at 1 in linkedlist", parse_linear_dsl)
        
        # 测试删除命令
        self.run_test("顺序表按值删除", "delete 30 from arraylist", parse_linear_dsl)
        self.run_test("顺序表按位置删除", "delete at 2 from arraylist", parse_linear_dsl)
        self.run_test("链表按值删除", "delete 3 from linkedlist", parse_linear_dsl)
        self.run_test("链表按位置删除", "delete at 1 from linkedlist", parse_linear_dsl)
        
        # 测试查询命令
        self.run_test("顺序表按值查询", "get 20 from arraylist", parse_linear_dsl)
        self.run_test("顺序表按位置查询", "get at 1 from arraylist", parse_linear_dsl)
        self.run_test("链表按值查询", "get 2 from linkedlist", parse_linear_dsl)
        self.run_test("链表按位置查询", "get at 0 from linkedlist", parse_linear_dsl)
        
        # 测试栈操作
        self.run_test("栈压入", "push 400 to stack", parse_linear_dsl)
        self.run_test("栈弹出", "pop from stack", parse_linear_dsl)
        
        # 测试清空命令
        self.run_test("清空顺序表", "clear arraylist", parse_linear_dsl)
        self.run_test("清空链表", "clear linkedlist", parse_linear_dsl)
        self.run_test("清空栈", "clear stack", parse_linear_dsl)
    
    def test_tree_structures_correct(self):
        """测试树形结构DSL命令（使用正确语法）"""
        print("\n" + "="*50)
        print("测试树形结构DSL命令（正确语法）")
        print("="*50)
        
        # 测试创建命令
        self.run_test("创建空二叉树", "create binarytree", parse_tree_dsl)
        self.run_test("创建带初值的二叉树", "create binarytree with 10,5,15,3,7,12,20", parse_tree_dsl)
        self.run_test("创建空二叉搜索树", "create bst", parse_tree_dsl)
        self.run_test("创建带初值的二叉搜索树", "create bst with 50,30,70,20,40,60,80", parse_tree_dsl)
        self.run_test("创建空哈夫曼树", "create huffman", parse_tree_dsl)
        
        # 测试插入命令
        self.run_test("二叉树插入", "insert 25 in binarytree", parse_tree_dsl)
        self.run_test("二叉搜索树插入", "insert 45 in bst", parse_tree_dsl)
        self.run_test("二叉树指定位置插入", "insert 8 at 1,0 in binarytree", parse_tree_dsl)
        
        # 测试删除命令
        self.run_test("二叉树删除", "delete 15 from binarytree", parse_tree_dsl)
        self.run_test("二叉搜索树删除", "delete 30 from bst", parse_tree_dsl)
        self.run_test("二叉树指定位置删除", "delete 7 at 1,1 from binarytree", parse_tree_dsl)
        
        # 测试搜索命令
        self.run_test("二叉树搜索", "search 10 in binarytree", parse_tree_dsl)
        self.run_test("二叉搜索树搜索", "search 50 in bst", parse_tree_dsl)
        
        # 测试遍历命令
        self.run_test("前序遍历", "traverse preorder", parse_tree_dsl)
        self.run_test("中序遍历", "traverse inorder", parse_tree_dsl)
        self.run_test("后序遍历", "traverse postorder", parse_tree_dsl)
        self.run_test("层序遍历", "traverse levelorder", parse_tree_dsl)
        
        # 测试哈夫曼树命令
        self.run_test("构建哈夫曼树", "build huffman with a:5,b:9,c:12,d:13,e:16,f:45", parse_tree_dsl)
        self.run_test("哈夫曼编码", 'encode "hello" using huffman', parse_tree_dsl)
        self.run_test("哈夫曼解码", "decode 1010110 using huffman", parse_tree_dsl)
        
        # 测试清空命令
        self.run_test("清空二叉树", "clear binarytree", parse_tree_dsl)
        self.run_test("清空二叉搜索树", "clear bst", parse_tree_dsl)
        self.run_test("清空哈夫曼树", "clear huffman", parse_tree_dsl)
    
    def test_error_cases_correct(self):
        """测试错误情况（正确的错误测试）"""
        print("\n" + "="*50)
        print("测试错误情况和边界条件")
        print("="*50)
        
        # 测试语法错误
        self.run_test("无效命令", "invalid command", parse_linear_dsl)
        self.run_test("缺少参数", "create", parse_linear_dsl)
        self.run_test("错误的结构类型", "create invalidtype", parse_linear_dsl)
        self.run_test("错误的操作", "invalidop 10 from arraylist", parse_linear_dsl)
        
        # 测试参数错误
        self.run_test("插入位置错误", "insert abc at 1 in arraylist", parse_linear_dsl)
        self.run_test("删除参数错误", "delete from arraylist", parse_linear_dsl)
        self.run_test("遍历类型错误", "traverse invalidorder", parse_tree_dsl)
        
        # 测试空值情况
        self.run_test("空字符串命令", "", parse_linear_dsl)
        self.run_test("只有空格的命令", "   ", parse_linear_dsl)
    
    def test_complex_scenarios_correct(self):
        """测试复杂场景（正确语法）"""
        print("\n" + "="*50)
        print("测试复杂场景")
        print("="*50)
        
        # 测试大数据量（适中的数据量）
        self.run_test("中等数据量创建顺序表", "create arraylist with 1,2,3,4,5,6,7,8,9,10", parse_linear_dsl)
        
        # 测试特殊字符
        self.run_test("哈夫曼数字字符", "build huffman with 1:10,2:20,3:30", parse_tree_dsl)
        
        # 测试边界值
        self.run_test("零值插入", "insert 0 at 0 in arraylist", parse_linear_dsl)
        
        # 测试简单字符串编码
        self.run_test("简单字符串编码", 'encode "abc" using huffman', parse_tree_dsl)
    
    def test_unified_parser(self):
        """测试统一解析器"""
        print("\n" + "="*50)
        print("测试统一DSL解析器")
        print("="*50)
        
        # 测试线性结构命令
        self.run_test("统一解析器-顺序表", "create arraylist with 1,2,3")
        self.run_test("统一解析器-栈", "push 100 to stack")
        
        # 测试树形结构命令
        self.run_test("统一解析器-二叉树", "create binarytree with 10,5,15")
        self.run_test("统一解析器-遍历", "traverse inorder")
    
    def print_summary(self):
        """打印测试总结"""
        print("\n" + "="*60)
        print("测试总结")
        print("="*60)
        
        total_tests = self.passed_tests + self.failed_tests
        success_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {self.passed_tests}")
        print(f"失败测试: {self.failed_tests}")
        print(f"成功率: {success_rate:.2f}%")
        
        if self.failed_tests > 0:
            print("\n失败的测试:")
            for result in self.test_results:
                if result["status"] in ["FAILED", "ERROR"]:
                    print(f"  - {result['name']}: {result.get('error', '未知错误')}")
        
        print("\n详细测试结果:")
        for result in self.test_results:
            status_symbol = "✅" if result["status"] == "PASSED" else "❌"
            print(f"  {status_symbol} {result['name']}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始DSL修正测试...")
        
        self.test_linear_structures_correct()
        self.test_tree_structures_correct()
        self.test_error_cases_correct()
        self.test_complex_scenarios_correct()
        self.test_unified_parser()
        
        self.print_summary()


def main():
    """主函数"""
    print("数据结构可视化模拟器 - DSL修正测试")
    print("="*60)
    
    tester = CorrectedDSLTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()