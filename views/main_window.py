#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口视图 - 应用程序的主界面
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QComboBox,
                             QLineEdit, QTextEdit, QMessageBox, QSplitter,
                             QAction, QToolBar, QStatusBar, QGroupBox, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from views.linear_view import LinearView
from views.tree_view import TreeView
from utils.theme import get_app_qss
from services.operation_recorder import OperationRecorder
import re
import html as _html


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
        # 应用统一主题样式
        # 当前基础字体像素（用于自适应缩放）
        self._current_base_font_px = 13
        try:
            self.setStyleSheet(get_app_qss(self._current_base_font_px))
        except Exception:
            pass
        
        # 创建子视图
        self.linear_view = LinearView()
        self.tree_view = TreeView()
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号和槽
        self._connect_signals()

        # 初始化一次字体缩放（在窗口显示或尺寸变化后会再次更新）
        try:
            self._update_font_scale_by_window()
        except Exception:
            pass
    
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
        
        # 移除包含“新建/清空/帮助”的工具栏行
        
        # 创建菜单栏
        self._create_menu()
    
    # 已删除工具栏创建，避免在界面顶部显示“新建/清空/帮助”一行
    
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
        
        # 移除“编辑”菜单（包含清空操作），不再显示编辑栏
        
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

        # 历史菜单（同文件、帮助同层）
        history_menu = menu_bar.addMenu("历史")

        # 查看线性历史
        linear_history_action = QAction("查看线性历史", self)
        linear_history_action.setStatusTip("查看线性结构的 DSL 操作历史")
        linear_history_action.triggered.connect(lambda: self._show_history_dialog("线性历史", "linear"))
        history_menu.addAction(linear_history_action)

        # 查看树形历史
        tree_history_action = QAction("查看树形历史", self)
        tree_history_action.setStatusTip("查看树形结构的 DSL 操作历史")
        tree_history_action.triggered.connect(lambda: self._show_history_dialog("树形历史", "tree"))
        history_menu.addAction(tree_history_action)

        # 查看全部历史
        all_history_action = QAction("查看全部历史", self)
        all_history_action.setStatusTip("查看线性与树形的合并历史")
        all_history_action.triggered.connect(lambda: self._show_history_dialog("全部历史", None))
        history_menu.addAction(all_history_action)
    
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

    def _show_history_dialog(self, title, context):
        """显示历史记录对话框

        Args:
            title: 对话框标题
            context: 上下文（"linear"、"tree" 或 None 表示全部）
        """
        try:
            entries = OperationRecorder.get_history_entries(context)
        except Exception:
            entries = []

        if not entries:
            html_text = "<p style='color:#888'>暂无历史记录</p>"
        else:
            # Colors
            color_ts = "#888"
            color_ctx_linear = "#1E90FF"
            color_ctx_tree = "#2ECC71"
            color_ctx_global = "#F39C12"
            color_verb = "#8E44AD"
            color_num = "#27AE60"
            color_quote = "#D35400"

            def ctx_color(ctx):
                if ctx == "linear":
                    return color_ctx_linear
                if ctx == "tree":
                    return color_ctx_tree
                return color_ctx_global

            def highlight_dsl(dsl: str) -> str:
                # Escape HTML first
                esc = _html.escape(dsl)
                # Highlight quoted text
                esc = re.sub(r"(&quot;.*?&quot;)", lambda m: f"<span style='color:{color_quote}'>{m.group(1)}</span>", esc)
                # Highlight numbers
                esc = re.sub(r"\b(\d+)\b", lambda m: f"<span style='color:{color_num}'>{m.group(1)}</span>", esc)
                # Highlight first verb at start
                verb = (dsl.strip().split()[0]).lower() if dsl.strip() else ""
                if verb:
                    esc = re.sub(rf"^({re.escape(verb)})\b", lambda m: f"<span style='color:{color_verb};font-weight:600'>{m.group(1)}</span>", esc)
                return esc

            lines = [
                "<div style='font-family:Consolas,Menlo,Monaco,monospace;font-size:20px;line-height:1.6'>"
            ]
            for e in entries:
                ts = OperationRecorder._format_ts(e.get("ts"))
                ctx = e.get("ctx")
                dsl = e.get("dsl") or ""
                ctx_tag = ""
                if context is None and ctx:
                    ctx_tag = f" <span style='color:{ctx_color(ctx)}'>[{ctx}]</span>"
                line = (
                    f"<span style='color:{color_ts}'>{_html.escape(ts)}</span>"
                    f"{ctx_tag} "
                    f"{highlight_dsl(dsl)}"
                )
                lines.append(f"<div>{line}</div>")
            lines.append("</div>")
            html_text = "".join(lines)

        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        layout = QVBoxLayout(dlg)
        view = QTextEdit(dlg)
        view.setReadOnly(True)
        view.setAcceptRichText(True)
        view.setHtml(html_text)
        layout.addWidget(view)
        dlg.resize(800, 500)
        dlg.exec_()
    
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

    # ------- 自适应字体缩放 -------
    def _compute_base_font_px(self):
        """根据窗口宽度计算基础字体像素大小"""
        try:
            w = max(1, int(self.width()))
        except Exception:
            w = 1000
        # 以 1000px 宽度为基准 13px，最大不超过约 20px
        scale = w / 1000.0
        target = int(round(13 * max(1.0, min(1.6, scale))))
        return target

    def _update_font_scale_by_window(self):
        """当窗口尺寸变化时更新全局样式中的字体大小"""
        px = self._compute_base_font_px()
        if px != self._current_base_font_px:
            self._current_base_font_px = px
            try:
                self.setStyleSheet(get_app_qss(px))
            except Exception:
                pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 依据窗口大小调整全局字体大小
        try:
            self._update_font_scale_by_window()
        except Exception:
            pass