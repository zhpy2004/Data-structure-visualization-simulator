#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
线性结构视图 - 用于展示和操作线性数据结构
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QLineEdit, QGroupBox, QFormLayout, QSpinBox,
                             QMessageBox, QSplitter, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QPen, QColor


class LinearView(QWidget):
    """线性结构视图类，用于展示和操作线性数据结构"""
    
    # 自定义信号
    operation_triggered = pyqtSignal(str, dict)  # 操作触发信号
    
    def show_message(self, title, message):
        """显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息内容
        """
        # 显示弹窗
        QMessageBox.information(self, title, message)
        
    def update_view(self, structure):
        """更新视图显示
        
        Args:
            structure: 要显示的数据结构对象
        """
        # 触发视图重绘
        if hasattr(self, 'visualization_area'):
            self.visualization_area.structure = structure
            self.visualization_area.update()

    
    def __init__(self):
        """初始化线性结构视图"""
        super().__init__()
        
        # 当前选择的数据结构类型
        self.current_structure = "array_list"  # 默认为顺序表
        
        # 初始化UI
        self._init_ui()
        
        # 连接信号和槽
        self._connect_signals()
    
    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建上部控制区域
        control_layout = QHBoxLayout()
        
        # 创建数据结构选择区域
        structure_group = QGroupBox("数据结构类型")
        structure_layout = QVBoxLayout(structure_group)
        
        self.structure_combo = QComboBox()
        self.structure_combo.addItem("顺序表", "array_list")
        self.structure_combo.addItem("链表", "linked_list")
        self.structure_combo.addItem("栈", "stack")
        structure_layout.addWidget(self.structure_combo)
        
        # 创建新建数据结构按钮
        self.create_button = QPushButton("新建")
        structure_layout.addWidget(self.create_button)
        
        # 创建清空按钮
        self.clear_button = QPushButton("清空")
        structure_layout.addWidget(self.clear_button)
        
        # 添加到控制布局
        control_layout.addWidget(structure_group)
        
        # 创建操作区域
        operations_group = QGroupBox("操作")
        operations_layout = QVBoxLayout(operations_group)
        
        # 创建通用操作区域
        common_form = QFormLayout()
        
        # 值输入
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("输入值，多个值用逗号分隔")
        common_form.addRow("值:", self.value_input)
        
        # 位置输入
        self.position_spin = QSpinBox()
        self.position_spin.setMinimum(0)
        self.position_spin.setMaximum(999)
        common_form.addRow("位置:", self.position_spin)
        
        operations_layout.addLayout(common_form)
        
        # 创建操作按钮布局
        buttons_layout = QHBoxLayout()
        
        # 顺序表和链表操作按钮
        self.insert_button = QPushButton("插入")
        self.remove_button = QPushButton("删除")
        self.get_button = QPushButton("获取")
        buttons_layout.addWidget(self.insert_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.get_button)
        
        # 栈操作按钮
        self.push_button = QPushButton("入栈")
        self.pop_button = QPushButton("出栈")
        self.peek_button = QPushButton("查看栈顶")
        buttons_layout.addWidget(self.push_button)
        buttons_layout.addWidget(self.pop_button)
        buttons_layout.addWidget(self.peek_button)
        
        # 默认隐藏栈操作按钮
        self.push_button.hide()
        self.pop_button.hide()
        self.peek_button.hide()
        
        operations_layout.addLayout(buttons_layout)
        
        # 添加到控制布局
        control_layout.addWidget(operations_group)
        
        # 添加控制布局到主布局
        main_layout.addLayout(control_layout)
        
        # 创建分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        
        # 创建可视化区域
        visualization_group = QGroupBox("可视化")
        visualization_layout = QVBoxLayout(visualization_group)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 允许小部件调整大小
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 根据需要显示水平滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 根据需要显示垂直滚动条
        
        # 创建可视化画布
        self.canvas = LinearCanvas()
        
        # 将画布添加到滚动区域
        scroll_area.setWidget(self.canvas)
        
        # 设置滚动区域的大小
        scroll_area.setMinimumSize(800, 600)
        visualization_layout.addWidget(scroll_area)
        
        # 添加可视化区域到主布局
        main_layout.addWidget(visualization_group, 1)  # 1表示拉伸因子
        
        # 创建状态标签
        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接数据结构选择信号
        self.structure_combo.currentIndexChanged.connect(self._structure_changed)
        
        # 连接新建和清空按钮
        self.create_button.clicked.connect(self._create_structure)
        self.clear_button.clicked.connect(self._clear_structure)
        
        # 连接顺序表和链表操作按钮
        self.insert_button.clicked.connect(self._insert_item)
        self.remove_button.clicked.connect(self._remove_item)
        self.get_button.clicked.connect(self._get_item)
        
        # 连接栈操作按钮
        self.push_button.clicked.connect(self._push_item)
        self.pop_button.clicked.connect(self._pop_item)
        self.peek_button.clicked.connect(self._peek_item)
    
    def _structure_changed(self, index):
        """数据结构类型改变处理
        
        Args:
            index: 选择的索引
        """
        # 获取选择的数据结构类型
        self.current_structure = self.structure_combo.itemData(index)
        
        # 更新UI显示
        if self.current_structure == "stack":
            # 显示栈操作按钮，隐藏顺序表和链表操作按钮
            self.insert_button.hide()
            self.remove_button.hide()
            self.get_button.hide()
            self.push_button.show()
            self.pop_button.show()
            self.peek_button.show()
            self.position_spin.setEnabled(False)
        else:
            # 显示顺序表和链表操作按钮，隐藏栈操作按钮
            self.insert_button.show()
            self.remove_button.show()
            self.get_button.show()
            self.push_button.hide()
            self.pop_button.hide()
            self.peek_button.hide()
            self.position_spin.setEnabled(True)
        
        # 发射操作信号
        self.operation_triggered.emit("change_structure", {"structure_type": self.current_structure})
        
        # 更新状态
        self.status_label.setText(f"当前数据结构: {self.structure_combo.currentText()}")
    
    def _create_structure(self):
        """创建新的数据结构"""
        # 获取输入值
        values_text = self.value_input.text().strip()
        
        if not values_text:
            QMessageBox.warning(self, "警告", "请输入初始值")
            return
        
        try:
            # 解析输入值
            if "," in values_text:
                # 多个值，解析为列表
                values = [int(v.strip()) for v in values_text.split(",")]
            else:
                # 单个值
                values = [int(values_text)]
            
            # 发射操作信号
            self.operation_triggered.emit("create", {
                "structure_type": self.current_structure,
                "values": values
            })
            
            # 更新状态
            self.status_label.setText(f"已创建{self.structure_combo.currentText()}")
            
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的整数值")
    
    def _clear_structure(self):
        """清空当前数据结构"""
        # 发射操作信号
        self.operation_triggered.emit("clear", {
            "structure_type": self.current_structure
        })
        
        # 更新状态
        self.status_label.setText(f"已清空{self.structure_combo.currentText()}")
    
    def _insert_item(self):
        """插入元素"""
        # 获取输入值和位置
        value_text = self.value_input.text().strip()
        position = self.position_spin.value()
        
        if not value_text:
            QMessageBox.warning(self, "警告", "请输入要插入的值")
            return
        
        try:
            # 解析输入值
            value = int(value_text)
            
            # 发射操作信号
            self.operation_triggered.emit("insert", {
                "structure_type": self.current_structure,
                "position": position,
                "value": value
            })
            
            # 更新状态
            self.status_label.setText(f"已在位置{position}插入值{value}")
            
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的整数值")
    
    def _remove_item(self):
        """删除元素"""
        # 获取位置
        position = self.position_spin.value()
        
        # 发射操作信号
        self.operation_triggered.emit("remove", {
            "structure_type": self.current_structure,
            "position": position
        })
        
        # 更新状态
        self.status_label.setText(f"已删除位置{position}的元素")
    
    def _get_item(self):
        """获取元素"""
        # 获取位置
        position = self.position_spin.value()
        
        # 发射操作信号
        self.operation_triggered.emit("get", {
            "structure_type": self.current_structure,
            "position": position
        })
    
    def _push_item(self):
        """入栈操作"""
        # 获取输入值
        value_text = self.value_input.text().strip()
        
        if not value_text:
            QMessageBox.warning(self, "警告", "请输入要入栈的值")
            return
        
        try:
            # 解析输入值
            value = int(value_text)
            
            # 发射操作信号
            self.operation_triggered.emit("push", {
                "structure_type": "stack",
                "value": value
            })
            
            # 更新状态
            self.status_label.setText(f"已将{value}入栈")
            
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的整数值")
    
    def _pop_item(self):
        """出栈操作"""
        # 发射操作信号
        self.operation_triggered.emit("pop", {
            "structure_type": "stack"
        })
        
        # 更新状态
        self.status_label.setText("已执行出栈操作")
    
    def _peek_item(self):
        """查看栈顶元素"""
        # 发射操作信号
        self.operation_triggered.emit("peek", {
            "structure_type": "stack"
        })
    
    def update_visualization(self, data):
        """更新可视化显示
        
        Args:
            data: 可视化数据
        """
        # 更新画布数据
        self.canvas.update_data(data)
        
        # 重绘画布
        self.canvas.update()
    
    def show_result(self, operation, result):
        """显示操作结果
        
        Args:
            operation: 操作名称
            result: 操作结果
        """
        if operation == "get":
            QMessageBox.information(self, "获取结果", f"位置 {result['position']} 的元素值为: {result['value']}")
        elif operation == "peek":
            QMessageBox.information(self, "栈顶元素", f"栈顶元素值为: {result['value']}")
        elif operation == "pop":
            QMessageBox.information(self, "出栈结果", f"出栈元素值为: {result['value']}")
        
        # 更新状态
        self.status_label.setText(f"操作 {operation} 完成")


class LinearCanvas(QWidget):
    """线性结构可视化画布"""
    
    def __init__(self):
        """初始化画布"""
        super().__init__()
        
        # 设置最小尺寸，允许画布根据内容自适应延伸
        self.setMinimumSize(800, 600)  # 设置初始最小尺寸
        
        # 初始化数据
        self.data = None
        self.structure_type = None
    
    def update_data(self, data):
        """更新数据
        
        Args:
            data: 可视化数据，包含结构类型和元素
        """
        if not data:
            self.data = None
            self.structure_type = None
            return
            
        self.structure_type = data.get("type")
        
        if self.structure_type == "linked_list":
            # 链表数据格式特殊处理
            self.data = [node.get("data") for node in data.get("nodes", [])]
        else:
            # 其他线性结构处理
            self.data = data.get("elements", [])
            if not self.data:
                # 尝试其他可能的键
                self.data = data.get("data", [])
        

        
        # 根据数据量调整画布大小
        self._adjust_canvas_size()
        
        # 强制重绘
        self.update()
    
    def _adjust_canvas_size(self):
        """根据数据量调整画布大小"""
        if not self.data:
            return
            
        # 根据数据量计算所需宽度
        if self.structure_type == "linked_list":
            # 链表每个节点占用更多空间
            required_width = len(self.data) * 150 + 100
        else:
            # 其他线性结构
            required_width = len(self.data) * 80 + 100
            
        # 设置最小高度
        required_height = 300
        
        # 更新画布尺寸
        self.setMinimumSize(max(800, required_width), max(600, required_height))
        self.updateGeometry()
    
    def paintEvent(self, event):
        """绘制事件
        
        Args:
            event: 绘制事件
        """
        # 确保有数据可绘制
        if not self.data or len(self.data) == 0:
            # 绘制提示信息
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(QPen(QColor(100, 100, 100)))
            painter.setFont(QFont("Arial", 14))
            painter.drawText(self.rect(), Qt.AlignCenter, "暂无数据可显示")
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        

        
        # 根据结构类型选择绘制方法
        if self.structure_type == "array_list":
            self._draw_array_list(painter)
        elif self.structure_type == "linked_list":
            self._draw_linked_list(painter)
        elif self.structure_type == "stack":
            self._draw_stack(painter)
        else:
            # 默认绘制方法，防止结构类型不匹配
            self._draw_array_list(painter)
    
    def _draw_array_list(self, painter):
        """绘制顺序表
        
        Args:
            painter: QPainter对象
        """
        # 设置字体
        font = QFont("Arial", 12)
        painter.setFont(font)
        
        # 计算单元格尺寸
        cell_width = 60
        cell_height = 40
        start_x = 50
        start_y = 100
        
        # 绘制顺序表标题
        painter.drawText(start_x, start_y - 30, "顺序表")
        
        # 绘制索引
        for i in range(len(self.data)):
            x = start_x + i * cell_width
            painter.drawText(x + 20, start_y - 10, str(i))
        
        # 绘制单元格和值
        for i, value in enumerate(self.data):
            x = start_x + i * cell_width
            
            # 绘制单元格
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(x, start_y, cell_width, cell_height)
            
            # 绘制值
            painter.drawText(x + 20, start_y + 25, str(value))
    
    def _draw_linked_list(self, painter):
        """绘制链表
        
        Args:
            painter: QPainter对象
        """
        # 设置字体
        font = QFont("Arial", 12)
        painter.setFont(font)
        
        # 计算节点尺寸
        node_width = 60
        node_height = 40
        arrow_length = 30
        start_x = 50
        start_y = 100
        
        # 绘制链表标题
        painter.drawText(start_x, start_y - 30, "链表")
        
        # 绘制节点和箭头
        for i, value in enumerate(self.data):
            x = start_x + i * (node_width + arrow_length)
            
            # 绘制节点
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(x, start_y, node_width, node_height)
            
            # 绘制值
            painter.drawText(x + 20, start_y + 25, str(value))
            
            # 绘制箭头（除了最后一个节点）
            if i < len(self.data) - 1:
                arrow_x = x + node_width
                arrow_y = start_y + node_height // 2
                
                # 绘制箭头线
                painter.drawLine(arrow_x, arrow_y, arrow_x + arrow_length, arrow_y)
                
                # 绘制箭头头部
                painter.drawLine(arrow_x + arrow_length - 10, arrow_y - 5, arrow_x + arrow_length, arrow_y)
                painter.drawLine(arrow_x + arrow_length - 10, arrow_y + 5, arrow_x + arrow_length, arrow_y)
        
        # 绘制最后一个节点的NULL指针
        if self.data:
            last_x = start_x + (len(self.data) - 1) * (node_width + arrow_length) + node_width
            last_y = start_y + node_height // 2
            
            # 绘制NULL文本
            painter.drawText(last_x + 10, last_y + 5, "NULL")
    
    def _draw_stack(self, painter):
        """绘制栈
        
        Args:
            painter: QPainter对象
        """
        # 设置字体
        font = QFont("Arial", 12)
        painter.setFont(font)
        
        # 计算单元格尺寸
        cell_width = 100
        cell_height = 40
        start_x = 150
        start_y = 250
        
        # 绘制栈标题
        painter.drawText(start_x, 50, "栈")
        
        # 绘制栈底和栈顶标记
        if self.data:
            painter.drawText(start_x - 80, start_y + 5, "栈底")
            painter.drawText(start_x - 80, start_y - (len(self.data) - 1) * cell_height + 5, "栈顶")
        
        # 绘制栈元素（从下往上）
        for i, value in enumerate(reversed(self.data)):
            y = start_y - i * cell_height
            
            # 绘制单元格
            painter.setPen(QPen(Qt.black, 2))
            painter.drawRect(start_x, y, cell_width, cell_height)
            
            # 绘制值
            painter.drawText(start_x + 40, y + 25, str(value))