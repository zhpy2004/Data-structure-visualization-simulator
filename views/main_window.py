#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口视图 - 应用程序的主界面
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QLineEdit, QTextEdit, QMessageBox, QSplitter,
                             QAction, QToolBar, QStatusBar, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from views.linear_view import LinearView
from views.tree_view import TreeView


class MainWindow(QMainWindow):
    """主窗口类，应用程序的主界面"""
    
    # 自定义信号
    linear_action_triggered = pyqtSignal(str, dict)  # 线性结构操作信号
    tree_action_triggered = pyqtSignal(str, dict)    # 树形结构操作信号
    save_structure_requested = pyqtSignal()          # 保存数据结构信号
    load_structure_requested = pyqtSignal()          # 加载数据结构信号
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowTitle("数据结构可视化模拟器")
        self.setMinimumSize(1000, 700)
        
        # 创建子视图
        self.linear_view = LinearView()
        self.tree_view = TreeView()
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号和槽
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建选项卡部件
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建线性结构选项卡
        linear_tab = QWidget()
        linear_layout = QVBoxLayout(linear_tab)
        linear_layout.addWidget(self.linear_view)
        self.tab_widget.addTab(linear_tab, "线性结构")
        
        # 创建树形结构选项卡
        tree_tab = QWidget()
        tree_layout = QVBoxLayout(tree_tab)
        tree_layout.addWidget(self.tree_view)
        self.tab_widget.addTab(tree_tab, "树形结构")
        
        
        # 创建状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建菜单栏
        self._create_menu()
    
    def _create_toolbar(self):
        """创建工具栏"""
        # 主工具栏
        main_toolbar = QToolBar("主工具栏")
        self.addToolBar(main_toolbar)
        
        # 新建操作
        new_action = QAction("新建", self)
        new_action.setStatusTip("创建新的数据结构")
        main_toolbar.addAction(new_action)
        
        # 清空操作
        clear_action = QAction("清空", self)
        clear_action.setStatusTip("清空当前数据结构")
        main_toolbar.addAction(clear_action)
        
        # 添加分隔符
        main_toolbar.addSeparator()
        
        # 帮助操作
        help_action = QAction("帮助", self)
        help_action.setStatusTip("显示帮助信息")
        main_toolbar.addAction(help_action)
    
    def _create_menu(self):
        """创建菜单栏"""
        # 主菜单
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件")
        
        # 新建操作
        new_action = QAction("新建", self)
        file_menu.addAction(new_action)
        
        # 保存操作
        save_action = QAction("保存", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("保存当前数据结构到文件")
        save_action.triggered.connect(self._save_structure)
        file_menu.addAction(save_action)
        
        # 加载操作
        load_action = QAction("加载", self)
        load_action.setShortcut("Ctrl+O")
        load_action.setStatusTip("从文件加载数据结构")
        load_action.triggered.connect(self._load_structure)
        file_menu.addAction(load_action)
        
        # 添加分隔符
        file_menu.addSeparator()
        
        # 退出操作
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑")
        
        # 清空操作
        clear_action = QAction("清空", self)
        edit_menu.addAction(clear_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助")
        
        # 帮助操作
        help_action = QAction("帮助", self)
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
        
        # 关于操作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接选项卡切换信号
        self.tab_widget.currentChanged.connect(self._tab_changed)
        
        # 连接LinearView的操作信号到MainWindow的信号
        self.linear_view.operation_triggered.connect(self._handle_linear_view_operation)
        
        # 连接TreeView的操作信号到MainWindow的信号
        self.tree_view.operation_triggered.connect(self._handle_tree_view_operation)
    
    def _handle_linear_view_operation(self, operation, params):
        """处理LinearView的操作信号
        
        Args:
            operation: 操作类型
            params: 操作参数
        """
        # 发射线性操作信号
        self.linear_action_triggered.emit(operation, params)
    
    def _handle_tree_view_operation(self, operation, params):
        """处理TreeView的操作信号
        
        Args:
            operation: 操作类型
            params: 操作参数
        """
        # 发射树形操作信号
        self.tree_action_triggered.emit(operation, params)
    
    
    def _tab_changed(self, index):
        """选项卡切换处理
        
        Args:
            index: 新的选项卡索引
        """
        tab_name = self.tab_widget.tabText(index)
        self.status_bar.showMessage(f"当前选项卡: {tab_name}")
    
    def _show_help(self):
        """显示帮助信息"""
        help_text = """
        数据结构可视化模拟器使用帮助：
        
        1. 线性结构操作：
           - 在"线性结构"选项卡中可以创建和操作顺序表、链表和栈
           - 使用界面上的按钮进行插入、删除等操作
        
        2. 树形结构操作：
           - 在"树形结构"选项卡中可以创建和操作二叉树、二叉搜索树和哈夫曼树
           - 使用界面上的按钮进行插入、删除、搜索等操作
        
        3. DSL命令：
           - 在"DSL命令"选项卡中可以使用自定义命令语言操作数据结构
           - 命令格式：结构类型.操作(参数)
           
           示例命令：
           - linear.create_array_list([1, 2, 3, 4, 5])
           - linear.insert(2, 10)
           - tree.create_bst([5, 3, 7, 2, 4, 6, 8])
           - tree.search(4)
        """
        
        QMessageBox.information(self, "帮助", help_text)
    
    def _show_about(self):
        """显示关于信息"""
        about_text = """
        数据结构可视化模拟器
        
        版本：1.0.0
        
        本程序用于可视化展示线性结构和树形结构的构建与算法执行过程。
        
        支持的数据结构：
        - 线性结构：顺序表、链表、栈
        - 树形结构：二叉树、二叉搜索树、平衡二叉树(AVL树)、哈夫曼树
        """
        
        QMessageBox.about(self, "关于", about_text)
    
    def _save_structure(self):
        """保存当前数据结构"""
        # 发送信号通知控制器保存当前数据结构
        self.save_structure_requested.emit()
        
    def _load_structure(self):
        """加载数据结构"""
        # 发送信号通知控制器加载数据结构
        self.load_structure_requested.emit()
    
    def show_message(self, message):
        """在状态栏显示消息
        
        Args:
            message: 要显示的消息
        """
        self.status_bar.showMessage(message, 3000)  # 显示3秒