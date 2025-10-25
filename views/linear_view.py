#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
线性结构视图 - 用于展示和操作线性数据结构
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QLineEdit, QGroupBox, QFormLayout, QSpinBox,
                             QMessageBox, QSplitter, QFrame, QScrollArea, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
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
            structure: 要显示的数据结构对象或可视化数据
        """
        # 当传入 None 时，清空画布并刷新
        if structure is None:
            if hasattr(self, 'canvas'):
                self.canvas.update_data(None)
                self.canvas.update()
            if hasattr(self, 'status_label'):
                self.status_label.setText("已清空视图，请点击“新建”")
            return
        
        # 支持直接传入结构对象或可视化数据字典
        data = None
        if isinstance(structure, dict):
            data = structure
        elif hasattr(structure, 'get_visualization_data'):
            try:
                data = structure.get_visualization_data()
            except Exception:
                data = None
        
        # 更新可视化
        if data is not None:
            self.update_visualization(data)
        else:
            if hasattr(self, 'canvas'):
                self.canvas.update_data(None)
                self.canvas.update()

        # 触发视图重绘
        if hasattr(self, 'visualization_area'):
            self.visualization_area.structure = structure
            self.visualization_area.update()
    
    def __init__(self):
        """初始化线性结构视图"""
        super().__init__()
        
        # 当前选择的数据结构类型
        self.current_structure = "array_list"  # 默认为顺序表
        
        # 动画步骤
        self.animation_steps = []
        self.current_step_index = -1
        self._before_state = None
        self._after_state = None
        
        # 播放控制
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._on_timer_tick)
        self.is_playing = False
        self.play_speed_factor = 1.0
        self.play_base_interval_ms = 800
        
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
        self.insert_button.setEnabled(False)
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
        
        # 遍历/动画控制按钮
        self.prev_step_button = QPushButton("上一步")
        self.next_step_button = QPushButton("下一步")
        self.prev_step_button.setEnabled(False)
        self.next_step_button.setEnabled(False)
        buttons_layout.addWidget(self.prev_step_button)
        buttons_layout.addWidget(self.next_step_button)
        
        # 动态播放控制
        self.play_button = QPushButton("播放")
        self.replay_button = QPushButton("重新播放")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1x", "2x", "4x"])
        self.speed_combo.setCurrentText("1x")
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.replay_button)
        buttons_layout.addWidget(QLabel("速度"))
        buttons_layout.addWidget(self.speed_combo)
        
        # 隐藏步进按钮（改为动态播放）
        self.prev_step_button.hide()
        self.next_step_button.hide()
        self.prev_step_button.setEnabled(False)
        self.next_step_button.setEnabled(False)
        
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
        
        # 连接动画控制按钮
        self.prev_step_button.clicked.connect(self._prev_step)
        self.next_step_button.clicked.connect(self._next_step)
        
        # 连接动态播放控制
        self.play_button.clicked.connect(self._toggle_play)
        self.replay_button.clicked.connect(self._replay)
        self.speed_combo.currentIndexChanged.connect(self._update_speed)
    
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
        
        # 禁用插入按钮直到新建
        self.insert_button.setEnabled(False)
        # 发射操作信号
        self.operation_triggered.emit("change_structure", {"structure_type": self.current_structure})
        
        # 清空当前视图与动画状态，避免旧步骤残留影响新类型
        try:
            # 停止播放
            if hasattr(self, 'play_timer') and self.play_timer.isActive():
                self.play_timer.stop()
            self.is_playing = False if hasattr(self, 'is_playing') else False
            
            # 清空动画步骤与索引
            if hasattr(self, 'animation_steps'):
                self.animation_steps = []
            if hasattr(self, 'current_step_index'):
                self.current_step_index = -1
            self._before_state = None if hasattr(self, '_before_state') else None
            self._after_state = None if hasattr(self, '_after_state') else None
            
            # 禁用控制按钮并重置播放按钮文案
            if hasattr(self, 'prev_step_button'):
                self.prev_step_button.setEnabled(False)
            if hasattr(self, 'next_step_button'):
                self.next_step_button.setEnabled(False)
            if hasattr(self, 'play_button'):
                self.play_button.setEnabled(False)
                self.play_button.setText("播放")
            if hasattr(self, 'replay_button'):
                self.replay_button.setEnabled(False)
            
            # 清空画布并重绘（update_view(None) 会由控制器触发，这里先本地清空）
            if hasattr(self, 'canvas'):
                self.canvas.update_data(None)
                self.canvas.update()
        except Exception:
            pass
        
        # 更新状态
        self.status_label.setText(f"当前数据结构: {self.structure_combo.currentText()}")
    
    def _create_structure(self):
        """创建数据结构"""
        # 获取选择的数据结构类型
        structure_type = self.current_structure
        
        # 解析输入值
        values_text = self.value_input.text().strip()
        values = []
        if values_text:
            try:
                values = [int(v.strip()) for v in values_text.split(',') if v.strip() != '']
            except ValueError:
                QMessageBox.warning(self, "警告", "请输入有效的整数列表，例如：1,2,3")
                return
        
        # 若为顺序表，先设定容量（槽位数）
        capacity = None
        if structure_type == 'array_list':
            cap, ok = QInputDialog.getInt(self, "设定大小", "请输入顺序表容量（槽位数）:", 10, 1, 10000)
            if not ok:
                return
            capacity = cap
        
        # 发射操作信号
        self.operation_triggered.emit("create", {
            "structure_type": structure_type,
            "values": values,
            "capacity": capacity
        })
        self.insert_button.setEnabled(True)
        
        # 更新状态
        if capacity is not None:
            self.status_label.setText(f"已创建{self.structure_combo.currentText()}，容量: {capacity}，初始数据: {values}")
        else:
            self.status_label.setText(f"已创建{self.structure_combo.currentText()}，初始数据: {values}")
    
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
        # 发射操作信号
        self.operation_triggered.emit("push", {
            "structure_type": "stack",
            "value": self.value_input.text().strip()
        })
        
        # 更新状态
        self.status_label.setText("已执行入栈操作")
    
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
        # 在非动画更新时，重置高亮与播放状态，避免残留效果
        if hasattr(self, 'canvas'):
            self.canvas.highlighted_index = None
        if hasattr(self, 'play_timer') and self.play_timer.isActive():
            self.play_timer.stop()
        if hasattr(self, 'is_playing'):
            self.is_playing = False
        if hasattr(self, 'animation_steps'):
            self.animation_steps = []
        if hasattr(self, 'current_step_index'):
            self.current_step_index = -1
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(False)
            self.play_button.setText('播放')
        if hasattr(self, 'replay_button'):
            self.replay_button.setEnabled(False)
        if hasattr(self, 'prev_step_button'):
            self.prev_step_button.setEnabled(False)
        if hasattr(self, 'next_step_button'):
            self.next_step_button.setEnabled(False)
        
        # 更新画布数据
        self.canvas.update_data(data)
        
        # 重绘画布
        self.canvas.update()
    
    def update_visualization_with_animation(self, before_state, after_state, operation_type, index=None, value=None):
        """使用动画更新可视化显示（顺序表/链表/栈）"""
        # 确定结构类型
        struct_type = None
        if before_state:
            struct_type = before_state.get('type')
        if not struct_type and after_state:
            struct_type = after_state.get('type')
        
        if struct_type in ('array_list', 'linked_list', 'stack'):
            self._before_state = before_state
            self._after_state = after_state
            
            if struct_type == 'array_list':
                self.animation_steps = self._build_array_animation_steps(before_state, after_state, operation_type, index, value)
            elif struct_type == 'linked_list':
                self.animation_steps = self._build_linked_animation_steps(before_state, after_state, operation_type, index, value)
            else:
                # 栈动画
                self.animation_steps = self._build_stack_animation_steps(before_state, after_state, operation_type, value)
            
            self.current_step_index = -1
            
            # 启用播放控制按钮
            can_play = True if self.animation_steps else False
            self.play_button.setEnabled(can_play)
            self.replay_button.setEnabled(can_play)
            
            # 显示第一步并自动播放
            self._next_step()
            self._start_playback()
        else:
            # 非支持类型，直接更新
            self.update_visualization(after_state)
    
    def _build_array_animation_steps(self, before_state, after_state, operation_type, index, value):
        """构建顺序表动画步骤"""
        steps = []
        before_list = before_state.get('data') or before_state.get('elements') or []
        after_list = after_state.get('data') or after_state.get('elements') or before_list
        before_size = before_state.get('size', len(before_list))
        after_size = after_state.get('size', len(after_list))
        before_capacity = before_state.get('capacity', max(before_size, len(before_list)))
        after_capacity = after_state.get('capacity', max(after_size, len(after_list)))
        
        if operation_type == 'get':
            steps.append({
                'type': 'highlight', 'index': index,
                'display_data': before_list.copy(),
                'size': before_size, 'capacity': before_capacity
            })
            return steps
        
        if operation_type == 'insert':
            # 初始高亮
            steps.append({
                'type': 'highlight', 'index': index,
                'display_data': before_list.copy(),
                'size': before_size, 'capacity': before_capacity
            })
            # 扩展显示列表到插入后的大小
            display = before_list.copy()
            display.append(None)
            # 右移
            for j in range(before_size - 1, index - 1, -1):
                # 将元素右移到 j+1
                display[j + 1] = display[j]
                display[j] = None
                steps.append({
                    'type': 'shift_right', 'index': j,
                    'display_data': display.copy(),
                    'size': before_size, 'capacity': before_capacity
                })
            # 插入新值
            display[index] = value
            steps.append({
                'type': 'insert_value', 'index': index, 'value': value,
                'display_data': display.copy(),
                'size': after_size, 'capacity': after_capacity
            })
            # 最终状态
            steps.append({
                'type': 'final', 'index': None,
                'display_data': after_list.copy(),
                'size': after_size, 'capacity': after_capacity
            })
            return steps
        
        if operation_type == 'delete':
            # 初始高亮
            steps.append({
                'type': 'highlight', 'index': index,
                'display_data': before_list.copy(),
                'size': before_size, 'capacity': before_capacity
            })
            # 删除元素（淡出为 None）
            display = before_list.copy()
            display[index] = None
            steps.append({
                'type': 'delete_value', 'index': index,
                'display_data': display.copy(),
                'size': before_size, 'capacity': before_capacity
            })
            # 左移
            for j in range(index + 1, before_size):
                display[j - 1] = display[j]
                display[j] = None
                steps.append({
                    'type': 'shift_left', 'index': j,
                    'display_data': display.copy(),
                    'size': before_size, 'capacity': before_capacity
                })
            # 最终状态
            steps.append({
                'type': 'final', 'index': None,
                'display_data': after_list.copy(),
                'size': after_state.get('size', len(after_list)),
                'capacity': after_state.get('capacity', max(len(after_list), before_capacity))
            })
            return steps
        
        # 默认无动画
        return steps
    
    def _build_linked_animation_steps(self, before_state, after_state, operation_type, index, value):
        """构建链表动画步骤"""
        steps = []
        # 获取值列表
        before_nodes = before_state.get('nodes', [])
        before_list = [n.get('data') for n in before_nodes]
        after_nodes = after_state.get('nodes', [])
        after_list = [n.get('data') for n in after_nodes] if after_nodes else before_list
        size_before = before_state.get('size', len(before_list))
        size_after = after_state.get('size', len(after_list))
        
        # 遍历步进函数
        def append_traverse_steps(target_idx):
            for j in range(0, min(target_idx, size_before - 1) + 1):
                steps.append({
                    'struct': 'linked_list',
                    'type': 'traverse',
                    'index': j,
                    'display_data': before_list.copy(),
                    'size': size_before
                })
        
        if operation_type == 'get':
            append_traverse_steps(index)
            steps.append({
                'struct': 'linked_list',
                'type': 'final',
                'index': index,
                'display_data': before_list.copy(),
                'size': size_before
            })
            return steps
        
        if operation_type == 'insert':
            # 遍历到插入位置的前一个节点（头插除外）
            if index > 0:
                append_traverse_steps(index - 1)
            else:
                # 头插：高亮头节点（如果存在）
                if size_before > 0:
                    steps.append({
                        'struct': 'linked_list',
                        'type': 'traverse',
                        'index': 0,
                        'display_data': before_list.copy(),
                        'size': size_before
                    })
            # 插入显示
            steps.append({
                'struct': 'linked_list',
                'type': 'insert_value',
                'index': index,
                'display_data': after_list.copy(),
                'size': size_after
            })
            steps.append({
                'struct': 'linked_list',
                'type': 'final',
                'index': None,
                'display_data': after_list.copy(),
                'size': size_after
            })
            return steps
        
        if operation_type == 'delete':
            # 遍历到删除位置的前一个节点（头删除外）
            if index > 0:
                append_traverse_steps(index - 1)
            # 高亮目标节点
            steps.append({
                'struct': 'linked_list',
                'type': 'highlight',
                'index': index,
                'display_data': before_list.copy(),
                'size': size_before
            })
            # 删除后显示
            temp = before_list.copy()
            if 0 <= index < len(temp):
                temp.pop(index)
            steps.append({
                'struct': 'linked_list',
                'type': 'delete_value',
                'index': index,
                'display_data': temp,
                'size': len(temp)
            })
            steps.append({
                'struct': 'linked_list',
                'type': 'final',
                'index': None,
                'display_data': after_list.copy(),
                'size': size_after
            })
            return steps
        
        # 默认无动画
        return steps
    
    def _build_stack_animation_steps(self, before_state, after_state, operation_type, value=None):
        """构建栈动画步骤"""
        steps = []
        before_list = before_state.get('data', [])
        after_list = after_state.get('data', before_list)
        capacity_before = before_state.get('capacity')
        capacity_after = after_state.get('capacity', capacity_before)
        
        # 高亮栈顶（若存在）
        if before_list:
            steps.append({
                'struct': 'stack',
                'type': 'highlight',
                'index': len(before_list) - 1,
                'display_data': before_list.copy(),
                'size': len(before_list),
                'capacity': capacity_before
            })
        
        if operation_type == 'push':
            # 推入后显示新栈顶
            steps.append({
                'struct': 'stack',
                'type': 'insert_value',
                'index': len(after_list) - 1 if after_list else None,
                'display_data': after_list.copy(),
                'size': len(after_list),
                'capacity': capacity_after
            })
            steps.append({
                'struct': 'stack',
                'type': 'final',
                'index': None,
                'display_data': after_list.copy(),
                'size': len(after_list),
                'capacity': capacity_after
            })
            return steps
        
        if operation_type == 'pop':
            # 弹出后显示新的栈顶或空栈
            steps.append({
                'struct': 'stack',
                'type': 'delete_value',
                'index': len(before_list) - 1 if before_list else None,
                'display_data': after_list.copy(),
                'size': len(after_list),
                'capacity': capacity_after
            })
            steps.append({
                'struct': 'stack',
                'type': 'final',
                'index': None,
                'display_data': after_list.copy(),
                'size': len(after_list),
                'capacity': capacity_after
            })
            return steps
        
        if operation_type == 'peek':
            # 仅高亮栈顶，最终状态为原始
            steps.append({
                'struct': 'stack',
                'type': 'final',
                'index': len(before_list) - 1 if before_list else None,
                'display_data': before_list.copy(),
                'size': len(before_list),
                'capacity': capacity_before
            })
            return steps
        
        return steps
    
    def _on_timer_tick(self):
        """定时器触发：自动前进动画步进"""
        if not self.animation_steps:
            self._pause_playback()
            return
        if self.current_step_index < len(self.animation_steps) - 1:
            self._next_step()
        else:
            self._pause_playback()
            self.status_label.setText("动画完成")
    
    def _current_interval_ms(self):
        """根据速度下拉框计算当前播放间隔"""
        text = self.speed_combo.currentText() if hasattr(self, 'speed_combo') else "1x"
        try:
            factor = float(text.replace('x',''))
        except Exception:
            factor = 1.0
        # 保存倍速，便于其他逻辑复用
        self.play_speed_factor = factor
        # 倍速越大，间隔越短；设置下限避免过快
        return int(self.play_base_interval_ms / max(0.25, factor))
    
    def _start_playback(self):
        """开始播放动画"""
        if not self.animation_steps:
            return
        self.is_playing = True
        self.play_button.setText("暂停")
        self.play_timer.start(self._current_interval_ms())
        self.status_label.setText("播放中…")
    
    def _pause_playback(self):
        """暂停播放动画"""
        self.play_timer.stop()
        self.is_playing = False
        self.play_button.setText("播放")
        self.status_label.setText("已暂停")
    
    def _toggle_play(self):
        """切换播放/暂停"""
        if not self.animation_steps:
            return
        # 若已到结尾，重新播放
        if self.current_step_index >= len(self.animation_steps) - 1:
            self._replay()
            self._start_playback()
            return
        if self.is_playing:
            self._pause_playback()
        else:
            self._start_playback()
    
    def _replay(self):
        """重新播放，从头开始"""
        if not self.animation_steps:
            return
        self._pause_playback()
        self.current_step_index = -1
        self.canvas.highlighted_index = None
        self.status_label.setText("已重置，准备播放…")
        # 立即展示第一步并自动开始播放
        self._next_step()
        self._start_playback()
    
    def _update_speed(self):
        """更新播放速度并重启定时器（若正在播放）"""
        text = self.speed_combo.currentText() if hasattr(self, 'speed_combo') else "1x"
        try:
            self.play_speed_factor = float(text.replace('x',''))
        except Exception:
            self.play_speed_factor = 1.0
        if self.is_playing:
            self.play_timer.start(self._current_interval_ms())

    def _apply_step(self, step):
        """应用单个动画步骤到画布"""
        if not step:
            return
        
        # 设置高亮索引
        self.canvas.highlighted_index = step.get('index')
        
        # 选择结构类型
        struct_type = step.get('struct', self._before_state.get('type') if self._before_state else 'array_list')
        
        # 更新数据（显示用）
        if struct_type == 'linked_list':
            nodes = [{'id': i, 'data': val} for i, val in enumerate(step.get('display_data', []))]
            viz = {
                'type': 'linked_list',
                'nodes': nodes,
                'size': step.get('size')
            }
        elif struct_type == 'stack':
            viz = {
                'type': 'stack',
                'data': step.get('display_data', []),
                'size': step.get('size'),
                'capacity': step.get('capacity')
            }
        else:
            viz = {
                'type': 'array_list',
                'data': step.get('display_data', []),
                'size': step.get('size'),
                'capacity': step.get('capacity')
            }
        self.canvas.update_data(viz)
        self.canvas.update()
        
        # 更新状态栏文案
        t = step.get('type')
        idx = step.get('index')
        if t == 'highlight' and idx is not None:
            self.status_label.setText(f"高亮索引 {idx}")
        elif t == 'traverse':
            self.status_label.setText(f"遍历到索引 {idx}")
        elif t == 'shift_right':
            self.status_label.setText("右移元素…")
        elif t == 'shift_left':
            self.status_label.setText("左移元素…")
        elif t == 'insert_value':
            self.status_label.setText("插入新元素…")
        elif t == 'delete_value':
            self.status_label.setText("删除元素…")
        elif t == 'final':
            self.status_label.setText("动画完成")
    
    def _prev_step(self):
        """处理上一步按钮点击事件（顺序表动画）"""
        if not self.animation_steps:
            return
        if self.current_step_index > 0:
            self.current_step_index -= 1
            step = self.animation_steps[self.current_step_index]
            self._apply_step(step)
            self.next_step_button.setEnabled(True)
            if self.current_step_index == 0:
                self.prev_step_button.setEnabled(False)




    def _next_step(self):
        """处理下一步按钮点击事件（顺序表动画）"""
        if not self.animation_steps:
            return

        if self.current_step_index < len(self.animation_steps) - 1:
            self.current_step_index += 1
            step = self.animation_steps[self.current_step_index]
            self._apply_step(step)
            self.prev_step_button.setEnabled(self.current_step_index > 0)
            if self.current_step_index == len(self.animation_steps) - 1:
                self.next_step_button.setEnabled(False)
        else:
            self.next_step_button.setEnabled(False)


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
        self.capacity = None
        self.size = None
        self.highlighted_index = None
    
    def update_data(self, data):
        """更新数据
        
        Args:
            data: 可视化数据，包含结构类型和元素
        """
        if not data:
            self.data = None
            self.structure_type = None
            self.capacity = None
            self.size = None
            self.highlighted_index = None
            return
            
        self.structure_type = data.get("type")
        self.capacity = data.get("capacity")
        self.size = data.get("size")
        
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
        if not self.data and not (self.structure_type == "array_list" and self.capacity):
            return
            
        # 根据数据量计算所需宽度
        if self.structure_type == "linked_list":
            # 链表每个节点占用更多空间
            required_width = len(self.data) * 150 + 100
        else:
            # 其他线性结构
            total_slots = self.capacity if (self.structure_type == "array_list" and self.capacity) else len(self.data)
            required_width = total_slots * 80 + 100
        
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
        # 确保有数据可绘制（数组结构有容量时也应绘制空位）
        if (self.structure_type != "array_list" or self.capacity is None) and (not self.data or len(self.data) == 0):
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
        # 绘制容量和大小
        if self.capacity is not None and self.size is not None:
            painter.drawText(start_x + 120, start_y - 30, f"容量: {self.capacity}  大小: {self.size}")
        
        # 计算应绘制的总槽位数（优先使用容量）
        total_cells = self.capacity if self.capacity is not None else len(self.data)
        
        # 绘制索引
        for i in range(total_cells):
            x = start_x + i * cell_width
            painter.drawText(x + 20, start_y - 10, str(i))
        
        # 绘制单元格和值（为未赋值的槽位也绘制空格）
        for i in range(total_cells):
            x = start_x + i * cell_width
            
            # 绘制单元格
            if self.highlighted_index is not None and i == self.highlighted_index:
                painter.setPen(QPen(QColor(255, 152, 0), 2))
                painter.setBrush(QColor(255, 224, 178))
            else:
                painter.setPen(QPen(Qt.black, 2))
                painter.setBrush(Qt.NoBrush)
            painter.drawRect(x, start_y, cell_width, cell_height)
            
            # 绘制值
            value = self.data[i] if i < len(self.data) else None
            if value is None:
                # 空位保留为空或显示占位
                painter.setPen(QPen(QColor(150, 150, 150)))
                painter.drawText(x + 20, start_y + 25, "")
            else:
                painter.setPen(QPen(Qt.black))
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
        
        # 绘制索引标签
        for i in range(len(self.data)):
            x = start_x + i * (node_width + arrow_length)
            painter.drawText(x + 20, start_y - 10, str(i))
        
        # 绘制节点和箭头
        for i, value in enumerate(self.data):
            x = start_x + i * (node_width + arrow_length)
            
            # 绘制节点（支持高亮）
            if self.highlighted_index is not None and i == self.highlighted_index:
                painter.setPen(QPen(QColor(255, 152, 0), 2))
                painter.setBrush(QColor(255, 224, 178))
            else:
                painter.setPen(QPen(Qt.black, 2))
                painter.setBrush(Qt.NoBrush)
            painter.drawRect(x, start_y, node_width, node_height)
            
            # 绘制值
            painter.drawText(x + 20, start_y + 25, str(value))
            
            # 绘制箭头（除了最后一个节点）
            if i < len(self.data) - 1:
                arrow_x = x + node_width
                arrow_y = start_y + node_height // 2
                
                # 箭头线与头部
                painter.setPen(QPen(QColor(66, 66, 66)))
                painter.drawLine(arrow_x, arrow_y, arrow_x + arrow_length, arrow_y)
                painter.drawLine(arrow_x + arrow_length - 10, arrow_y - 5, arrow_x + arrow_length, arrow_y)
                painter.drawLine(arrow_x + arrow_length - 10, arrow_y + 5, arrow_x + arrow_length, arrow_y)
        
        # 绘制最后一个节点的NULL指针
        if self.data:
            last_x = start_x + (len(self.data) - 1) * (node_width + arrow_length) + node_width
            last_y = start_y + node_height // 2
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
            # 栈底标签
            painter.drawText(start_x - 80, start_y + 5, "栈底")
            # 栈顶标签，避免单元素时与栈底重叠
            top_label_y = start_y - (len(self.data) - 1) * cell_height + 5
            if len(self.data) == 1:
                top_label_y = start_y - cell_height + 5  # 上移到单元格顶部上方
            painter.drawText(start_x - 80, top_label_y, "栈顶")
        
        # 绘制栈元素（从下往上）
        for i, value in enumerate(self.data):
            y = start_y - i * cell_height
            
            # 绘制单元格（支持高亮栈顶或指定索引）
            if self.highlighted_index is not None and i == self.highlighted_index:
                painter.setPen(QPen(QColor(255, 152, 0), 2))
                painter.setBrush(QColor(255, 224, 178))
            else:
                painter.setPen(QPen(Qt.black, 2))
                painter.setBrush(Qt.NoBrush)
            painter.drawRect(start_x, y, cell_width, cell_height)
            
            # 绘制值
            painter.setPen(QPen(Qt.black))
            painter.drawText(start_x + 40, y + 25, str(value))