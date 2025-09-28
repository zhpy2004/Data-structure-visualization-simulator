#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试用例 - 用于测试数据结构可视化模拟器的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controllers.app_controller import AppController
from PyQt5.QtWidgets import QApplication
import time


def test_linear_structures():
    """测试线性结构的功能"""
    print("===== 测试线性结构 =====")
    
    # 创建应用控制器
    app = QApplication(sys.argv)
    controller = AppController()
    controller.show_main_window()
    
    # 测试顺序表
    print("\n----- 测试顺序表 -----")
    test_commands = [
        "linear.array_list.create 10,20,30,40,50",
        "linear.array_list.insert 25 at 2",
        "linear.array_list.get 2",
        "linear.array_list.remove 3"
    ]
    
    for cmd in test_commands:
        print(f"执行命令: {cmd}")
        controller._handle_dsl_command(cmd)
        time.sleep(1)  # 暂停以便观察结果
    
    # 测试链表
    print("\n----- 测试链表 -----")
    test_commands = [
        "linear.linked_list.create 5,15,25,35,45",
        "linear.linked_list.insert 20 at 1",
        "linear.linked_list.get 2",
        "linear.linked_list.remove 3"
    ]
    
    for cmd in test_commands:
        print(f"执行命令: {cmd}")
        controller._handle_dsl_command(cmd)
        time.sleep(1)  # 暂停以便观察结果
    
    # 测试栈
    print("\n----- 测试栈 -----")
    test_commands = [
        "linear.stack.create 100,200,300",
        "linear.stack.push 400",
        "linear.stack.peek",
        "linear.stack.pop",
        "linear.stack.pop"
    ]
    
    for cmd in test_commands:
        print(f"执行命令: {cmd}")
        controller._handle_dsl_command(cmd)
        time.sleep(1)  # 暂停以便观察结果
    
    # 运行应用
    app.exec_()


def test_tree_structures():
    """测试树形结构的功能"""
    print("===== 测试树形结构 =====")
    
    # 创建应用控制器
    app = QApplication(sys.argv)
    controller = AppController()
    controller.show_main_window()
    
    # 测试二叉树
    print("\n----- 测试二叉树 -----")
    test_commands = [
        "tree.binary_tree.create 10,5,15,3,7,12,20",
        "tree.binary_tree.traverse preorder",
        "tree.binary_tree.traverse inorder",
        "tree.binary_tree.traverse postorder",
        "tree.binary_tree.traverse levelorder"
    ]
    
    for cmd in test_commands:
        print(f"执行命令: {cmd}")
        controller._handle_dsl_command(cmd)
        time.sleep(1)  # 暂停以便观察结果
    
    # 测试二叉搜索树
    print("\n----- 测试二叉搜索树 -----")
    test_commands = [
        "tree.bst.create 50,30,70,20,40,60,80",
        "tree.bst.insert 35",
        "tree.bst.search 40",
        "tree.bst.remove 30",
        "tree.bst.traverse inorder"
    ]
    
    for cmd in test_commands:
        print(f"执行命令: {cmd}")
        controller._handle_dsl_command(cmd)
        time.sleep(1)  # 暂停以便观察结果
    
    # 测试哈夫曼树
    print("\n----- 测试哈夫曼树 -----")
    test_commands = [
        "tree.huffman_tree.create a,b,c,d,e with 10,15,12,18,5",
        "tree.huffman_tree.encode abcde",
        "tree.huffman_tree.decode 01001011"
    ]
    
    for cmd in test_commands:
        print(f"执行命令: {cmd}")
        controller._handle_dsl_command(cmd)
        time.sleep(1)  # 暂停以便观察结果
    
    # 运行应用
    app.exec_()


def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "linear":
            test_linear_structures()
        elif sys.argv[1] == "tree":
            test_tree_structures()
        else:
            print("未知的测试类型，请使用 'linear' 或 'tree'")
    else:
        print("请指定测试类型: python test_cases.py [linear|tree]")


if __name__ == "__main__":
    main()