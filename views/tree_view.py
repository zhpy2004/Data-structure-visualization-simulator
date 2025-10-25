#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
树形结构视图 - 用于展示和操作树形数据结构
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QLineEdit, QGroupBox, QFormLayout,
                             QMessageBox, QSplitter, QFrame, QRadioButton, QButtonGroup,
                             QScrollArea, QApplication, QMenu, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QBrush


class TreeView(QWidget):
    """树形结构视图类，用于展示和操作树形数据结构"""
    
    # 自定义信号
    operation_triggered = pyqtSignal(str, dict)  # 操作触发信号
    
    def update_view(self, structure):
        """更新视图显示
        
        Args:
            structure: 要显示的数据结构
        """
        # 确保画布存在
        if not hasattr(self, 'canvas'):
            self.show_message("错误", "画布组件未正确初始化")
            return
        
        # 处理空结构
        if structure is None:
            self.status_label.setText("暂无数据结构")
            self.update_visualization({'type': None, 'nodes': []}, None)
            return
        
        # 获取结构的可视化数据并更新显示
        try:
            vis_data = structure.get_visualization_data()
        except Exception as e:
            self.show_message("错误", f"获取可视化数据失败: {e}")
            return
        
        self.update_visualization(vis_data, vis_data.get('type'))
    
    def show_message(self, title, message):
        """显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息内容
        """
        # 显示弹窗
        QMessageBox.information(self, title, message)
        
    def highlight_huffman_codes(self, text, codes):
        """以遍历播放的方式高亮哈夫曼编码路径
        
        Args:
            text: 待编码文本
            codes: 哈夫曼编码表 {字符: 编码}
        """
        data = getattr(self.canvas, 'data', None)
        if not data:
            try:
                self.show_message("提示", "当前没有哈夫曼树可显示编码路径")
            except Exception:
                pass
            return
        try:
            # 构建ID映射与叶子映射
            id_map = {}
            char_leaf_id = {}
            for node in data:
                nid = node.get('id')
                if nid is None:
                    continue
                id_map[nid] = node
                ch = node.get('char')
                if ch is not None:
                    char_leaf_id[ch] = nid
            
            node_seq = []
            step_info = []
            for ch in text:
                code = codes.get(ch)
                if not code:
                    continue
                leaf_id = char_leaf_id.get(ch)
                if not leaf_id:
                    continue
                # 叶->根，随后反转得到根->叶路径
                path_rev_ids = [leaf_id]
                cur_id = leaf_id
                while True:
                    cur_node = id_map.get(cur_id)
                    if cur_node is None:
                        break
                    parent_id = cur_node.get('parent_id')
                    if parent_id is None:
                        parent_id = cur_node.get('parent')
                    if parent_id is None:
                        break
                    path_rev_ids.append(parent_id)
                    cur_id = parent_id
                path_ids = list(reversed(path_rev_ids))
                # 编码步骤与位数一一对应（跳过根）
                for j in range(1, min(len(path_ids), len(code) + 1)):
                    node_seq.append(path_ids[j])
                    bit = code[j - 1]
                    step_info.append({
                        'mode': 'encode',
                        'char': ch,
                        'bit': bit,
                        'step_in_char': j,
                        'total_char_steps': len(code)
                    })
            
            # 设置遍历播放数据
            self.canvas.stop_animation()
            self.canvas.traversal_order = [info['char'] for info in step_info]  # 仅用于长度与占位
            self.canvas.traversal_type = "huffman_encode"
            self.canvas.node_id_map = node_seq.copy()
            self.canvas.current_traversal_index = -1
            self.canvas.highlighted_nodes = []
            self.huffman_step_info = step_info
            
            # 播放控制
            self.prev_step_button.setEnabled(True)
            self.next_step_button.setEnabled(True)
            if hasattr(self, 'play_button'):
                self.play_button.setEnabled(True)
                self.replay_button.setEnabled(True)
                self.play_button.setText("播放")
            
            # 若有步骤，显示第一步并开始播放
            if self.canvas.node_id_map:
                self.canvas.highlighted_nodes = [self.canvas.node_id_map[0]]
                self.canvas.current_traversal_index = 0
                info0 = self.huffman_step_info[0] if self.huffman_step_info else None
                if info0:
                    self.status_label.setText(
                        f"哈夫曼编码：字符 '{info0['char']}' 步骤 {info0['step_in_char']}/{info0['total_char_steps']}（位 {info0['bit']}）"
                    )
                else:
                    self.status_label.setText(f"哈夫曼编码路径步骤: 1/{len(self.canvas.node_id_map)}")
                self.canvas.update()
                QApplication.processEvents()
                self._start_traversal_playback()
        except Exception:
            # 兜底：保留原始弹窗显示
            code_info = "哈夫曼编码表:\n"
            for char, code in codes.items():
                code_info += f"{char}: {code}\n"
            encoding_process = "编码过程:\n"
            for char in text:
                if char in codes:
                    encoding_process += f"{char} -> {codes[char]}\n"
                else:
                    encoding_process += f"{char} -> (未在编码表中)\n"
            self.show_message("哈夫曼编码详情", code_info + "\n" + encoding_process)
    
    def highlight_huffman_decode_path(self, binary, decoded):
        """以遍历播放的方式高亮哈夫曼解码路径
        
        Args:
            binary: 二进制编码串
            decoded: 解码后的文本（用于结果展示，可选）
        """
        data = getattr(self.canvas, 'data', None)
        if not data:
            try:
                self.show_message("提示", "当前没有哈夫曼树可显示解码路径")
            except Exception:
                pass
            return
        try:
            id_map = {node.get('id'): node for node in data if node.get('id') is not None}
            # 构建父->子映射
            children_map = {}
            for node in data:
                parent_id = node.get('parent_id')
                if parent_id is None:
                    parent_id = node.get('parent')
                if parent_id is not None:
                    children_map.setdefault(parent_id, []).append(node)
            # 根节点
            root_node = None
            for node in data:
                parent_id = node.get('parent_id')
                if parent_id is None:
                    parent_id = node.get('parent')
                if parent_id is None:
                    root_node = node
                    break
            if root_node is None:
                self.show_message("错误", "未找到哈夫曼树根节点")
                return
            
            def ordered_children(pid):
                children = children_map.get(pid, [])
                if not children:
                    return []
                return sorted(children, key=lambda c: c.get('x_pos', 0.5))  # 按x_pos判断左右
            
            node_seq = []
            step_info = []
            cur = root_node
            accum = ""
            for bit in binary:
                oc = ordered_children(cur.get('id'))
                next_node = None
                if oc:
                    if bit == '0':
                        next_node = oc[0]
                    elif len(oc) > 1:
                        next_node = oc[1]
                    else:
                        next_node = oc[0]
                if next_node is None:
                    break
                node_seq.append(next_node.get('id'))
                accum += bit
                recognized = next_node.get('char')
                step_info.append({
                    'mode': 'decode',
                    'bit': bit,
                    'accum_code': accum,
                    'recognized_char': recognized
                })
                if recognized is not None:
                    # 识别到字符，重置回根节点
                    cur = root_node
                    accum = ""
                else:
                    cur = next_node
            
            # 设置遍历播放数据
            self.canvas.stop_animation()
            self.canvas.traversal_order = [info.get('recognized_char') or '' for info in step_info]
            self.canvas.traversal_type = "huffman_decode"
            self.canvas.node_id_map = node_seq.copy()
            self.canvas.current_traversal_index = -1
            self.canvas.highlighted_nodes = []
            self.huffman_step_info = step_info
            self.huffman_decoded_text = decoded
            
            # 播放控制
            self.prev_step_button.setEnabled(True)
            self.next_step_button.setEnabled(True)
            if hasattr(self, 'play_button'):
                self.play_button.setEnabled(True)
                self.replay_button.setEnabled(True)
                self.play_button.setText("播放")
            
            # 若有步骤，显示第一步并开始播放
            if self.canvas.node_id_map:
                self.canvas.highlighted_nodes = [self.canvas.node_id_map[0]]
                self.canvas.current_traversal_index = 0
                info0 = self.huffman_step_info[0] if self.huffman_step_info else None
                if info0:
                    if info0.get('recognized_char'):
                        self.status_label.setText(
                            f"哈夫曼解码：位 {info0['bit']}，累积 {info0['accum_code']} -> 识别 '{info0['recognized_char']}'"
                        )
                    else:
                        self.status_label.setText(
                            f"哈夫曼解码：位 {info0['bit']}，累积 {info0['accum_code']}"
                        )
                else:
                    self.status_label.setText(f"哈夫曼解码路径步骤: 1/{len(self.canvas.node_id_map)}")
                self.canvas.update()
                QApplication.processEvents()
                self._start_traversal_playback()
        except Exception:
            # 兜底：保留原始解码过程弹窗
            decode_info = "解码过程:\n"
            current_code = ""
            for bit in binary:
                current_code += bit
                found = False
                for char, code in self.get_current_huffman_codes().items():
                    if code == current_code:
                        decode_info += f"{current_code} -> {char}\n"
                        current_code = ""
                        found = True
                        break
                if not found and len(current_code) > 0:
                    decode_info += f"当前累积: {current_code}\n"
            self.show_message("哈夫曼解码详情", decode_info)
    
    def get_current_huffman_codes(self):
        """获取当前哈夫曼树的编码表
        
        Returns:
            dict: 哈夫曼编码表 {字符: 编码}
        """
        # 存储当前哈夫曼树的编码表
        self.huffman_codes = getattr(self, 'huffman_codes', {})
        return self.huffman_codes
    
    def __init__(self):
        """初始化树形结构视图"""
        super().__init__()
        
        # 当前选择的数据结构类型
        self.current_structure = "binary_tree"  # 默认为二叉树
        
        # 初始化哈夫曼动画相关属性
        self.huffman_animation_timer = QTimer()
        self.animation_speed = 1000  # 默认动画速度：1秒一步
        self.huffman_build_steps = []
        self.current_build_step = 0
        
        # 初始化AVL动画相关属性
        self.avl_animation_timer = QTimer()
        self.avl_build_steps = []
        self.current_avl_step = 0
        
        # 初始化BST动画相关属性
        self.bst_animation_timer = QTimer()
        self.bst_build_steps = []
        self.current_bst_step = 0
        
        # 二叉树遍历播放控制（仿线性表）
        self.traversal_play_timer = QTimer(self)
        self.traversal_play_timer.timeout.connect(self._on_traversal_timer_tick)
        self.traversal_is_playing = False
        self.traversal_play_base_interval_ms = 800
        self.traversal_play_speed_factor = 1.0
        # 重播流程标记：用于在动画结束后恢复到操作后状态
        self.replay_in_progress = False
        
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
        self.structure_combo.addItem("二叉树", "binary_tree")
        self.structure_combo.addItem("二叉搜索树", "bst")
        self.structure_combo.addItem("平衡二叉树(AVL树)", "avl_tree")
        self.structure_combo.addItem("哈夫曼树", "huffman_tree")
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
        
        operations_layout.addLayout(common_form)
        
        # 创建遍历方式选择
        self.traversal_box = QGroupBox("遍历方式")
        traversal_layout = QHBoxLayout(self.traversal_box)
        
        self.traversal_group = QButtonGroup(self)
        
        self.preorder_radio = QRadioButton("前序遍历")
        self.inorder_radio = QRadioButton("中序遍历")
        self.postorder_radio = QRadioButton("后序遍历")
        self.levelorder_radio = QRadioButton("层序遍历")
        
        self.traversal_group.addButton(self.preorder_radio, 1)
        self.traversal_group.addButton(self.inorder_radio, 2)
        self.traversal_group.addButton(self.postorder_radio, 3)
        self.traversal_group.addButton(self.levelorder_radio, 4)
        
        self.preorder_radio.setChecked(True)  # 默认选择前序遍历
        
        traversal_layout.addWidget(self.preorder_radio)
        traversal_layout.addWidget(self.inorder_radio)
        traversal_layout.addWidget(self.postorder_radio)
        traversal_layout.addWidget(self.levelorder_radio)
        
        operations_layout.addWidget(self.traversal_box)
        
        # 创建操作按钮布局
        buttons_layout = QHBoxLayout()
        
        # 通用操作按钮
        self.insert_button = QPushButton("插入")
        self.remove_button = QPushButton("删除")
        self.search_button = QPushButton("搜索")
        self.traverse_button = QPushButton("遍历")
        
        buttons_layout.addWidget(self.insert_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.search_button)
        buttons_layout.addWidget(self.traverse_button)
        # 默认隐藏搜索按钮
        self.search_button.hide()
        # 禁用插入按钮，需先新建
        self.insert_button.setEnabled(False)
        
        # 哈夫曼树特有操作按钮
        self.encode_button = QPushButton("编码")
        self.decode_button = QPushButton("解码")
        
        buttons_layout.addWidget(self.encode_button)
        buttons_layout.addWidget(self.decode_button)
        
        # 遍历控制按钮
        self.prev_step_button = QPushButton("上一步")
        self.next_step_button = QPushButton("下一步")
        
        # 默认禁用遍历控制按钮
        self.prev_step_button.setEnabled(False)
        self.next_step_button.setEnabled(False)
        
        buttons_layout.addWidget(self.prev_step_button)
        buttons_layout.addWidget(self.next_step_button)
        
        # 隐藏手动遍历步进按钮
        self.prev_step_button.hide()
        self.next_step_button.hide()
        
        # 播放控制（仿线性表）
        self.play_button = QPushButton("播放")
        self.replay_button = QPushButton("重新播放")
        self.play_button.setEnabled(False)
        self.replay_button.setEnabled(False)
        buttons_layout.addWidget(self.play_button)
        buttons_layout.addWidget(self.replay_button)
        
        # 速度控制（仿线性表）
        speed_label = QLabel("速度")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1x", "2x", "4x"]) 
        self.speed_combo.setCurrentText("1x")
        buttons_layout.addWidget(speed_label)
        buttons_layout.addWidget(self.speed_combo)
        
        # 默认隐藏哈夫曼树操作按钮
        self.encode_button.hide()
        self.decode_button.hide()
        
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
        scroll_area.setWidgetResizable(True)  # 设置为True，允许画布自适应延伸
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 根据需要显示水平滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 根据需要显示垂直滚动条
        
        # 创建可视化画布
        self.canvas = TreeCanvas()
        # 不再设置固定尺寸，允许画布自适应延伸
        
        # 将画布添加到滚动区域
        scroll_area.setWidget(self.canvas)
        
        # 设置滚动区域的最小大小
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
        
        # 连接操作按钮
        self.insert_button.clicked.connect(self._insert_node)
        self.remove_button.clicked.connect(self._remove_node)
        self.search_button.clicked.connect(self._search_node)
        self.traverse_button.clicked.connect(self._traverse_tree)
        
        # 连接哈夫曼树特有操作按钮
        self.encode_button.clicked.connect(self._encode_text)
        self.decode_button.clicked.connect(self._decode_text)

        
        # 连接遍历控制按钮
        self.prev_step_button.clicked.connect(self._prev_step)
        self.next_step_button.clicked.connect(self._next_step)
        
        # 遍历播放控件信号（仿线性表）
        self.play_button.clicked.connect(self._toggle_traversal_play)
        self.replay_button.clicked.connect(self._replay_traversal)
        self.speed_combo.currentIndexChanged.connect(self._update_traversal_speed)
        
        # 连接哈夫曼动画定时器
        self.huffman_animation_timer.timeout.connect(self._animate_huffman_build)
        
        # 连接AVL动画定时器
        self.avl_animation_timer.timeout.connect(self._animate_avl_build)
        # 连接BST动画定时器
        self.bst_animation_timer.timeout.connect(self._animate_bst_build)
    
    def _structure_changed(self, index):
        """数据结构类型改变处理
        
        Args:
            index: 选择的索引
        """
        # 获取选择的数据结构类型
        self.current_structure = self.structure_combo.itemData(index)
        
        # 更新UI显示
        if self.current_structure == "huffman_tree":
            # 显示哈夫曼树特有操作按钮
            self.encode_button.show()
            self.decode_button.show()
            # 隐藏哈夫曼树不需要的按钮
            self.insert_button.hide()
            self.remove_button.hide()
            self.search_button.hide()
            self.traverse_button.hide()
            # 隐藏遍历方式选择框
            self.traversal_box.hide()
        elif self.current_structure == "binary_tree":
            # 二叉树页面隐藏搜索按钮
            self.search_button.hide()
            # 显示其他按钮
            self.insert_button.show()
            self.remove_button.show()
            self.traverse_button.show()
            # 隐藏哈夫曼树特有操作按钮
            self.encode_button.hide()
            self.decode_button.hide()
            # 显示遍历方式选择框
            self.traversal_box.show()
        elif self.current_structure == "bst":
            # 二叉搜索树页面隐藏遍历按钮，显示搜索按钮
            self.traverse_button.hide()
            self.insert_button.show()
            self.remove_button.show()
            self.search_button.show()
            # 隐藏哈夫曼树特有操作按钮
            self.encode_button.hide()
            self.decode_button.hide()
            # 隐藏遍历方式选择框
            self.traversal_box.hide()
        elif self.current_structure == "avl_tree":
            # AVL树页面显示基本操作按钮（显示搜索按钮，隐藏遍历相关界面）
            self.insert_button.show()
            self.remove_button.show()
            self.search_button.show()
            # 隐藏遍历相关界面
            self.traverse_button.hide()
            self.traversal_box.hide()
            # 隐藏哈夫曼树特有操作按钮
            self.encode_button.hide()
            self.decode_button.hide()
        
        # 禁用插入按钮直到新建
        self.insert_button.setEnabled(False)
        # 发射操作信号
        self.operation_triggered.emit("change_structure", {"structure_type": self.current_structure})
        
        # 清空当前视图与动画状态，避免旧步骤残留影响新类型
        try:
            # 停止所有定时器/播放
            if hasattr(self, 'traversal_play_timer') and self.traversal_play_timer.isActive():
                self.traversal_play_timer.stop()
            self.traversal_is_playing = False if hasattr(self, 'traversal_is_playing') else False
            if hasattr(self, 'stop_avl_animation'):
                self.stop_avl_animation()
            if hasattr(self, 'stop_huffman_animation'):
                self.stop_huffman_animation()
            if hasattr(self, 'stop_bst_animation'):
                self.stop_bst_animation()
            
            # 清空步骤与状态
            if hasattr(self, 'avl_build_steps'):
                self.avl_build_steps = []
            if hasattr(self, 'avl_delete_steps'):
                self.avl_delete_steps = []
            if hasattr(self, 'huffman_build_steps'):
                self.huffman_build_steps = []
            if hasattr(self, 'bst_build_steps'):
                self.bst_build_steps = []
            if hasattr(self, 'active_animation_type'):
                self.active_animation_type = None
            self.replay_in_progress = False if hasattr(self, 'replay_in_progress') else False
            
            # 清空遍历/搜索相关
            if hasattr(self, 'canvas'):
                self.canvas.current_traversal_index = -1
                self.canvas.traversal_order = []
                self.canvas.node_id_map = []
                self.canvas.search_target = None
                self.canvas.traversal_type = None
                self.canvas.highlighted_nodes = []
                # 重绘
                self.canvas.update()
            
            # 清空最后一次操作快照，防止重播恢复旧结构
            self.last_operation_before_state = None
            self.last_operation_after_state = None
            self.last_operation_type = None
            self.last_operation_value = None
            
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
        except Exception:
            pass
        
        # 更新状态
        self.status_label.setText(f"当前数据结构: {self.structure_combo.currentText()}")
    
    def _create_structure(self):
        """创建新的数据结构"""
        # 获取输入值（允许空初始值）
        values_text = self.value_input.text().strip()
        
        try:
            # 解析输入值
            if self.current_structure == "huffman_tree":
                # 哈夫曼树需要频率对
                if not values_text:
                    # 使用默认频率对
                    values = {"a": 8, "b": 3, "c": 1, "d": 1, "e": 4, "f": 1, "g": 2}
                else:
                    # 解析用户输入的频率对，格式如：a:8,b:3,c:1
                    values = {}
                    pairs = values_text.split(",")
                    for pair in pairs:
                        if ":" in pair:
                            char, freq = pair.split(":")
                            values[char.strip()] = int(freq.strip())
                        else:
                            raise ValueError("哈夫曼树输入格式应为：字符:频率,字符:频率,...")
            else:
                # 二叉树、BST、AVL允许空初始值，或用整数列表
                values = []
                if values_text:
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
            # 新建后启用插入按钮
            self.insert_button.setEnabled(True)
            
            # 如果是哈夫曼树，自动开始构建动画
            if self.current_structure == "huffman_tree":
                # 先触发构建动画信号，生成构建步骤
                self.operation_triggered.emit("build_huffman", {
                    "frequencies": values
                })
                # 然后开始哈夫曼树构建动画
                self.start_huffman_build_animation()
            # 如果是AVL树，自动开始构建动画
            elif self.current_structure == "avl_tree":
                # 先触发构建动画信号，生成构建步骤
                self.operation_triggered.emit("build_avl", {
                    "values": values
                })
                # 然后开始AVL树构建动画
                self.start_avl_build_animation()
            # 如果是BST，自动开始构建动画
            elif self.current_structure == "bst":
                # 触发构建动画信号，生成构建步骤
                self.operation_triggered.emit("build_bst", {
                    "values": values
                })
                # 然后开始BST构建动画
                self.start_bst_build_animation()
            
            # 更新状态
            self.status_label.setText(f"已创建{self.structure_combo.currentText()}")
            
        except ValueError as e:
            QMessageBox.warning(self, "警告", str(e) if str(e) else "请输入有效的值")
    
    def _clear_structure(self):
        """清空当前数据结构"""
        # 发射操作信号
        self.operation_triggered.emit("clear", {
            "structure_type": self.current_structure
        })
        
        # 清除所有动画步骤数据
        if hasattr(self, 'avl_build_steps'):
            self.avl_build_steps = []
        if hasattr(self, 'huffman_build_steps'):
            self.huffman_build_steps = []
        if hasattr(self, 'bst_build_steps'):
            self.bst_build_steps = []
        if hasattr(self, 'avl_delete_steps'):
            self.avl_delete_steps = []
        if hasattr(self, 'traversal_order'):
            self.traversal_order = []
        
        # 重置动画步骤索引
        self.current_avl_step = -1
        self.current_huffman_step = -1
        self.current_bst_step = -1 if hasattr(self, 'current_bst_step') else -1
        self.current_avl_delete_step = -1
        self.current_traversal_index = -1
        
        # 禁用动画控制按钮
        if hasattr(self, 'prev_step_button'):
            self.prev_step_button.setEnabled(False)
        if hasattr(self, 'next_step_button'):
            self.next_step_button.setEnabled(False)
        
        # 停止任何正在运行的动画定时器
        if hasattr(self, 'animation_timer') and self.animation_timer.isActive():
            self.animation_timer.stop()
        # 停止遍历播放并重置控件
        if hasattr(self, 'traversal_play_timer') and self.traversal_play_timer.isActive():
            self.traversal_play_timer.stop()
        if hasattr(self, 'bst_animation_timer') and self.bst_animation_timer.isActive():
            self.bst_animation_timer.stop()
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(False)
            self.replay_button.setEnabled(False)
            self.play_button.setText("播放")
        self.traversal_is_playing = False
        
        # 更新状态
        self.status_label.setText(f"已清空{self.structure_combo.currentText()}")
    
    def _insert_node(self):
        """插入节点"""
        # 获取输入值
        value_text = self.value_input.text().strip()
        
        if not value_text:
            QMessageBox.warning(self, "警告", "请输入要插入的值")
            return
        
        try:
            # 解析输入值
            value = int(value_text)
            
            # 发射操作信号
            self.operation_triggered.emit("insert", {
                "structure_type": self.current_structure,
                "value": value
            })
            
            # 更新状态
            self.status_label.setText(f"已插入值{value}")
            
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的整数值")
    
    def _remove_node(self):
        """删除节点"""
        # 获取输入值
        value_text = self.value_input.text().strip()
        
        if not value_text:
            QMessageBox.warning(self, "警告", "请输入要删除的值")
            return
        
        try:
            # 解析输入值
            value = int(value_text)
            
            # 发射操作信号
            self.operation_triggered.emit("remove", {
                "structure_type": self.current_structure,
                "value": value
            })
            
            # 更新状态
            self.status_label.setText(f"已删除值{value}")
            
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的整数值")
    
    def _search_node(self):
        """搜索节点"""
        # 获取输入值
        value_text = self.value_input.text().strip()
        
        if not value_text:
            QMessageBox.warning(self, "警告", "请输入要搜索的值")
            return
        
        try:
            # 解析输入值
            value = int(value_text)
            
            # 发射操作信号
            self.operation_triggered.emit("search", {
                "structure_type": self.current_structure,
                "value": value
            })
            
            # 更新状态
            self.status_label.setText(f"正在搜索值{value}")
            
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的整数值")
    
    def _traverse_tree(self):
        """遍历树"""
        # 获取选择的遍历方式
        traversal_id = self.traversal_group.checkedId()
        
        # 设置默认遍历类型为前序遍历
        traversal_type = "preorder"  # 默认值
        
        if traversal_id == 1:
            traversal_type = "preorder"
        elif traversal_id == 2:
            traversal_type = "inorder"
        elif traversal_id == 3:
            traversal_type = "postorder"
        elif traversal_id == 4:
            traversal_type = "levelorder"
        
        # 确保遍历类型不为None
        if not traversal_type:
            traversal_type = "preorder"  # 如果仍然为None，使用默认值
        
        # 发射操作信号
        self.operation_triggered.emit("traverse", {
            "structure_type": self.current_structure,
            "traversal_type": traversal_type
        })
        
        # 更新状态
        button_text = self.traversal_group.checkedButton().text() if self.traversal_group.checkedButton() else "前序遍历"
        self.status_label.setText(f"正在进行{button_text}")
    
    def _encode_text(self):
        """编码文本（哈夫曼树特有）"""
        # 获取输入文本
        text = self.value_input.text().strip()
        
        if not text:
            QMessageBox.warning(self, "警告", "请输入要编码的文本")
            return
        
        # 发射操作信号
        self.operation_triggered.emit("encode", {
            "structure_type": "huffman_tree",
            "text": text
        })
        
        # 更新状态
        self.status_label.setText(f"正在编码文本: {text}")
    
    def _decode_text(self):
        """解码文本（哈夫曼树特有）"""
        # 获取输入编码
        code = self.value_input.text().strip()
        
        if not code:
            QMessageBox.warning(self, "警告", "请输入要解码的二进制编码")
            return
        
        # 检查输入是否为二进制编码
        if not all(bit in "01" for bit in code):
            QMessageBox.warning(self, "警告", "请输入有效的二进制编码（只包含0和1）")
            return
        
        # 发射操作信号
        self.operation_triggered.emit("decode", {
            "structure_type": "huffman_tree",
            "binary": code
        })
        
        # 更新状态
        self.status_label.setText(f"正在解码: {code}")
    
    def update_visualization(self, data, structure_type=None):
        """更新可视化显示
        
        Args:
            data: 可视化数据
            structure_type: 结构类型
        """
        # 更新画布数据
        self.canvas.update_data(data)
        
        # 更新状态标签
        if structure_type:
            self.status_label.setText(f"当前数据结构: {structure_type}")
        
        # 重绘画布
        self.canvas.update()
    
    def update_visualization_with_animation(self, before_state, after_state, operation_type, value):
        """使用动画更新可视化显示
        
        Args:
            before_state: 操作前的状态
            after_state: 操作后的状态
            operation_type: 操作类型
            value: 操作的值
        """
        # 记录最后一次操作的前后状态与元信息，便于重播时恢复
        try:
            self.last_operation_before_state = before_state
            self.last_operation_after_state = after_state
            self.last_operation_type = operation_type
            self.last_operation_value = value
        except Exception:
            pass
        
        # 更新画布数据（直接使用操作后的状态）
        self.canvas.update_data(after_state)

        # 清理遍历序号以避免残留（适用于BST插入/删除及路径类操作）
        if hasattr(self.canvas, 'current_traversal_index'):
            self.canvas.current_traversal_index = -1
        if hasattr(self.canvas, 'traversal_order'):
            self.canvas.traversal_order = []
        if hasattr(self.canvas, 'node_id_map'):
            self.canvas.node_id_map = []
        
        # 更新状态标签
        op_cn = {"insert": "插入", "delete": "删除"}.get(operation_type, operation_type)
        self.status_label.setText(f"已完成{op_cn}操作: {value}")
        
        # 重绘画布
        self.canvas.update()
    
    def highlight_search_path(self, path, found, search_value=None):
        """高亮显示搜索路径
        
        Args:
            path: 搜索路径上的节点值列表
            found: 是否找到目标节点
            search_value: 搜索的目标值
        """
        # 获取当前数据
        data = self.canvas.data
        
        # 将节点值转换为节点ID
        node_ids = []
        if data:
            # 创建值到ID的映射（处理相同值的节点）
            value_to_ids = {}
            for node in data:
                if 'value' in node and 'id' in node:
                    if node['value'] not in value_to_ids:
                        value_to_ids[node['value']] = []
                    value_to_ids[node['value']].append(node['id'])
            
            # 跟踪已使用的节点ID
            used_node_ids = set()
            
            # 获取遍历路径中每个值在树中的位置顺序
            path_positions = {}
            for value in path:
                if value not in path_positions:
                    path_positions[value] = 0
                else:
                    path_positions[value] += 1
            
            # 重置计数器用于遍历
            value_counts = {value: 0 for value in path_positions.keys()}
            
            # 转换路径中的值为ID，按照遍历顺序正确映射相同值的节点
            for value in path:
                if value in value_to_ids and len(value_to_ids[value]) > value_counts[value]:
                    # 按照遍历顺序获取对应的节点ID
                    node_id = value_to_ids[value][value_counts[value]]
                    node_ids.append(node_id)
                    value_counts[value] += 1

        
        # 停止任何正在进行的动画
        self.canvas.stop_animation()
        # 停止AVL构建/删除动画定时器，避免与搜索播放冲突
        self.stop_avl_animation()
        
        # 设置搜索数据
        self.canvas.traversal_order = path
        self.canvas.traversal_type = "search"
        self.canvas.node_id_map = node_ids.copy()  # 使用副本避免引用问题
        self.canvas.search_target = search_value  # 保存搜索目标值
        
        # 重置动画状态
        self.canvas.current_traversal_index = -1
        self.canvas.highlighted_nodes = []
        
        # 更新状态标签
        if found:
            self.status_label.setText(f"准备搜索动画（已找到节点 {search_value}）...")
        else:
            self.status_label.setText(f"准备搜索动画（未找到节点 {search_value}）...")
        
        # 启用遍历控制按钮
        self.prev_step_button.setEnabled(True)
        self.next_step_button.setEnabled(True)
        
        # 启用遍历播放控件（仿线性表）
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.replay_button.setEnabled(True)
            self.play_button.setText("播放")
        
        # 立即显示第一个节点
        if node_ids and len(node_ids) > 0:
            self.canvas.highlighted_nodes = [node_ids[0]]
            self.canvas.current_traversal_index = 0
            self.status_label.setText(f"搜索步骤: 1/{len(path)}")
            # 强制重绘画布
            self.canvas.update()
            QApplication.processEvents()
            # 自动开始播放
            self._start_traversal_playback()
        
    def highlight_bst_insert_path(self, path, value):
        """以遍历播放逻辑展示BST插入路径，并在动画结束后执行插入"""
        data = self.canvas.data
        node_ids = []
        if data:
            value_to_ids = {}
            for node in data:
                if 'value' in node and 'id' in node:
                    value_to_ids.setdefault(node['value'], []).append(node['id'])
            # 按路径顺序映射ID
            counts = {}
            for v in path:
                idx = counts.get(v, 0)
                if v in value_to_ids and idx < len(value_to_ids[v]):
                    node_ids.append(value_to_ids[v][idx])
                counts[v] = idx + 1
        
        self.canvas.stop_animation()
        self.canvas.traversal_order = path
        self.canvas.traversal_type = "bst_insert"
        # 为BST插入增加一个“找到插入位置”的额外步骤：重复最后一个节点ID
        play_ids = node_ids.copy()
        if play_ids:
            play_ids.append(play_ids[-1])
        self.canvas.node_id_map = play_ids
        self.canvas.current_traversal_index = -1
        self.canvas.highlighted_nodes = []
        self.status_label.setText(f"准备BST插入路径动画：值 {value}")
        
        # 设置后置操作：动画结束后执行插入
        self.traversal_post_action = {
            'action': 'insert',
            'params': {'value': value, 'execute_only': True}
        }
        
        # 播放控制
        self.prev_step_button.setEnabled(True)
        self.next_step_button.setEnabled(True)
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.replay_button.setEnabled(True)
            self.play_button.setText("播放")
        
        # 若有可播放路径则按步骤播放，否则直接执行后置操作
        if play_ids:
            self.canvas.highlighted_nodes = [play_ids[0]]
            self.canvas.current_traversal_index = 0
            self.status_label.setText(f"BST插入路径步骤: 1/{len(self.canvas.node_id_map)}")
            self.canvas.update()
            QApplication.processEvents()
            self._start_traversal_playback()
        else:
            # 无路径（如空树）时直接触发插入，避免因为node_id_map为空无法执行后置操作
            self.prev_step_button.setEnabled(False)
            self.next_step_button.setEnabled(False)
            if hasattr(self, 'play_button'):
                self.play_button.setEnabled(False)
                self.replay_button.setEnabled(False)
                self.play_button.setText("播放")
            self.status_label.setText(f"路径为空，直接插入值 {value}")
            try:
                self.operation_triggered.emit('insert', {'value': value, 'execute_only': True})
            except Exception:
                pass
    def highlight_bst_delete_path(self, path, value):
        """以遍历播放逻辑展示BST删除路径，并在动画结束后执行删除"""
        data = self.canvas.data
        node_ids = []
        if data:
            value_to_ids = {}
            for node in data:
                if 'value' in node and 'id' in node:
                    value_to_ids.setdefault(node['value'], []).append(node['id'])
            counts = {}
            for v in path:
                idx = counts.get(v, 0)
                if v in value_to_ids and idx < len(value_to_ids[v]):
                    node_ids.append(value_to_ids[v][idx])
                counts[v] = idx + 1
        
        self.canvas.stop_animation()
        self.canvas.traversal_order = path
        self.canvas.traversal_type = "bst_delete"
        # 为BST删除增加一个“定位到要删除的节点”的额外步骤：重复最后一个节点ID
        play_ids = node_ids.copy()
        if play_ids:
            play_ids.append(play_ids[-1])
        self.canvas.node_id_map = play_ids
        self.canvas.current_traversal_index = -1
        self.canvas.highlighted_nodes = []
        self.status_label.setText(f"准备BST删除路径动画：值 {value}")
        
        # 设置后置操作：动画结束后执行删除
        self.traversal_post_action = {
            'action': 'delete',
            'params': {'value': value, 'execute_only': True}
        }
        
        self.prev_step_button.setEnabled(True)
        self.next_step_button.setEnabled(True)
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.replay_button.setEnabled(True)
            self.play_button.setText("播放")
        
        # 若有可播放路径则按步骤播放，否则直接执行后置操作
        if play_ids:
            self.canvas.highlighted_nodes = [play_ids[0]]
            self.canvas.current_traversal_index = 0
            self.status_label.setText(f"BST删除路径步骤: 1/{len(self.canvas.node_id_map)}")
            self.canvas.update()
            QApplication.processEvents()
            self._start_traversal_playback()
        else:
            # 无路径（如值不存在或空树）时直接触发删除，避免因为node_id_map为空无法执行后置操作
            self.prev_step_button.setEnabled(False)
            self.next_step_button.setEnabled(False)
            if hasattr(self, 'play_button'):
                self.play_button.setEnabled(False)
                self.replay_button.setEnabled(False)
                self.play_button.setText("播放")
            self.status_label.setText(f"路径为空，直接删除值 {value}")
            try:
                self.operation_triggered.emit('delete', {'value': value, 'execute_only': True})
            except Exception:
                pass
    def _prev_traversal_step(self):
        """处理上一步按钮点击事件"""
        if not hasattr(self.canvas, 'node_id_map') or not self.canvas.node_id_map:
            return
            
        # 更新当前遍历索引
        if self.canvas.current_traversal_index > 0:
            self.canvas.current_traversal_index -= 1
            
            # 更新高亮节点
            if self.canvas.current_traversal_index >= 0 and self.canvas.current_traversal_index < len(self.canvas.node_id_map):
                self.canvas.highlighted_nodes = [self.canvas.node_id_map[self.canvas.current_traversal_index]]
                
                # 更新状态标签
                if self.canvas.traversal_type in ("bst_insert", "bst_delete"):
                    action_cn = "BST插入路径步骤" if self.canvas.traversal_type == "bst_insert" else "BST删除路径步骤"
                    total_steps = len(self.canvas.node_id_map)
                    self.status_label.setText(f"{action_cn}: {self.canvas.current_traversal_index + 1}/{total_steps}")
                elif self.canvas.traversal_type == "search":
                    self.status_label.setText(f"搜索步骤: {self.canvas.current_traversal_index + 1}/{len(self.canvas.traversal_order)}")
                elif self.canvas.traversal_type in ("huffman_encode", "huffman_decode"):
                    info = None
                    try:
                        if hasattr(self, 'huffman_step_info') and self.huffman_step_info:
                            info = self.huffman_step_info[self.canvas.current_traversal_index]
                    except Exception:
                        info = None
                    if self.canvas.traversal_type == "huffman_encode" and info:
                        self.status_label.setText(
                            f"哈夫曼编码：字符 '{info.get('char')}' 步骤 {info.get('step_in_char')}/{info.get('total_char_steps')}（位 {info.get('bit')}）"
                        )
                    elif self.canvas.traversal_type == "huffman_decode" and info:
                        if info.get('recognized_char'):
                            self.status_label.setText(
                                f"哈夫曼解码：位 {info.get('bit')}，累积 {info.get('accum_code')} -> 识别 '{info.get('recognized_char')}'"
                            )
                        else:
                            self.status_label.setText(
                                f"哈夫曼解码：位 {info.get('bit')}，累积 {info.get('accum_code')}"
                            )
                    else:
                        self.status_label.setText(f"哈夫曼路径步骤: {self.canvas.current_traversal_index + 1}/{len(self.canvas.node_id_map)}")
                else:
                    traversal_name = {
                        "preorder": "前序遍历",
                        "inorder": "中序遍历",
                        "postorder": "后序遍历",
                        "levelorder": "层序遍历"
                    }.get(self.canvas.traversal_type, self.canvas.traversal_type)
                    self.status_label.setText(f"{traversal_name}遍历步骤: {self.canvas.current_traversal_index + 1}/{len(self.canvas.traversal_order)}")
                
                # 强制重绘画布
                self.canvas.update()
                QApplication.processEvents()
    
    def _next_traversal_step(self):
        """处理下一步按钮点击事件"""
        if not hasattr(self.canvas, 'node_id_map') or not self.canvas.node_id_map:
            return
            
        # 更新当前遍历索引
        if self.canvas.current_traversal_index < len(self.canvas.node_id_map) - 1:
            self.canvas.current_traversal_index += 1
            
            # 更新高亮节点
            if self.canvas.current_traversal_index < len(self.canvas.node_id_map):
                self.canvas.highlighted_nodes = [self.canvas.node_id_map[self.canvas.current_traversal_index]]
                
                # 更新状态标签
                if self.canvas.traversal_type in ("bst_insert", "bst_delete"):
                    action_cn = "BST插入路径步骤" if self.canvas.traversal_type == "bst_insert" else "BST删除路径步骤"
                    total_steps = len(self.canvas.node_id_map)
                    self.status_label.setText(f"{action_cn}: {self.canvas.current_traversal_index + 1}/{total_steps}")
                elif self.canvas.traversal_type == "search":
                    self.status_label.setText(f"搜索步骤: {self.canvas.current_traversal_index + 1}/{len(self.canvas.traversal_order)}")
                elif self.canvas.traversal_type in ("huffman_encode", "huffman_decode"):
                    info = None
                    try:
                        if hasattr(self, 'huffman_step_info') and self.huffman_step_info:
                            info = self.huffman_step_info[self.canvas.current_traversal_index]
                    except Exception:
                        info = None
                    if self.canvas.traversal_type == "huffman_encode" and info:
                        self.status_label.setText(
                            f"哈夫曼编码：字符 '{info.get('char')}' 步骤 {info.get('step_in_char')}/{info.get('total_char_steps')}（位 {info.get('bit')}）"
                        )
                    elif self.canvas.traversal_type == "huffman_decode" and info:
                        if info.get('recognized_char'):
                            self.status_label.setText(
                                f"哈夫曼解码：位 {info.get('bit')}，累积 {info.get('accum_code')} -> 识别 '{info.get('recognized_char')}'"
                            )
                        else:
                            self.status_label.setText(
                                f"哈夫曼解码：位 {info.get('bit')}，累积 {info.get('accum_code')}"
                            )
                    else:
                        self.status_label.setText(f"哈夫曼路径步骤: {self.canvas.current_traversal_index + 1}/{len(self.canvas.node_id_map)}")
                else:
                    traversal_name = {
                        "preorder": "前序遍历",
                        "inorder": "中序遍历",
                        "postorder": "后序遍历",
                        "levelorder": "层序遍历"
                    }.get(self.canvas.traversal_type, self.canvas.traversal_type)
                    self.status_label.setText(f"{traversal_name}遍历步骤: {self.canvas.current_traversal_index + 1}/{len(self.canvas.traversal_order)}")
                
                # 强制重绘画布
                self.canvas.update()
                QApplication.processEvents()
            
            # 检查是否完成遍历或搜索
            if self.canvas.current_traversal_index >= len(self.canvas.node_id_map) - 1:
                # 若存在后置操作（如BST插入/删除），优先执行并跳过结果弹窗
                if hasattr(self, 'traversal_post_action') and self.traversal_post_action:
                    post = self.traversal_post_action
                    self.traversal_post_action = None
                    # 禁用遍历控制按钮并暂停播放
                    self.prev_step_button.setEnabled(False)
                    self.next_step_button.setEnabled(False)
                    self._pause_traversal_playback()
                    action_cn = {'insert': '插入', 'delete': '删除'}.get(post.get('action'), post.get('action'))
                    self.status_label.setText(f"路径动画完成，执行{action_cn}操作…")
                    try:
                        self.operation_triggered.emit(post['action'], post.get('params', {}))
                    except Exception:
                        pass
                    return
                
                # 动画完成，显示结果弹窗（针对标准搜索/遍历；哈夫曼不弹窗）
                if self.canvas.traversal_type == "search":
                    found = self.canvas.traversal_order[-1] == self.canvas.search_target if hasattr(self.canvas, 'search_target') else False
                    result = {'found': found, 'value': self.canvas.search_target if hasattr(self.canvas, 'search_target') else None}
                    self.show_result("search", result)
                elif self.canvas.traversal_type in {"preorder", "inorder", "postorder", "levelorder"}:
                    result = {'result': self.canvas.traversal_order}
                    self.show_result("traverse", result)
                elif self.canvas.traversal_type == "huffman_decode":
                    # 完成信息由播放tick或此处设置为更友好文案
                    final_text = getattr(self, 'huffman_decoded_text', None)
                    if final_text is not None:
                        self.status_label.setText(f"哈夫曼解码完成：{final_text}")
                    else:
                        self.status_label.setText("哈夫曼解码完成")
                elif self.canvas.traversal_type == "huffman_encode":
                    self.status_label.setText("哈夫曼编码路径播放完成")
                
                # 禁用遍历控制按钮
                self.prev_step_button.setEnabled(False)
                self.next_step_button.setEnabled(False)
    
    def highlight_traversal_path(self, path, traverse_type):
        """高亮显示遍历路径
        
        Args:
            path: 遍历路径上的节点值列表
            traverse_type: 遍历类型
        """
        # 获取当前数据
        data = self.canvas.data
        
        # 将节点值转换为节点ID
        node_ids = []
        if data:
            # 创建值到ID列表的映射
            value_to_ids = {}
            for node in data:
                if 'value' in node and 'id' in node:
                    if node['value'] not in value_to_ids:
                        value_to_ids[node['value']] = []
                    value_to_ids[node['value']].append(node['id'])
            
            # 记录已使用的节点ID
            used_ids = set()
            
            # 为每个遍历路径中的值找到合适的节点ID
            for value in path:
                if value in value_to_ids and value_to_ids[value]:
                    # 尝试找到一个未使用的ID
                    found_unused = False
                    for node_id in value_to_ids[value]:
                        if node_id not in used_ids:
                            node_ids.append(node_id)
                            used_ids.add(node_id)
                            found_unused = True
                            print(f"映射节点值 {value} 到未使用的ID {node_id}")
                            break
                    
                    # 如果所有ID都已使用，则重用第一个ID
                    if not found_unused and value_to_ids[value]:
                        node_id = value_to_ids[value][0]
                        node_ids.append(node_id)
        
        # 停止任何正在进行的动画
        self.canvas.stop_animation()
        
        # 设置遍历数据
        self.canvas.traversal_order = path
        self.canvas.traversal_type = traverse_type
        self.canvas.node_id_map = node_ids.copy()  # 使用副本避免引用问题
        
        # 重置动画状态
        self.canvas.current_traversal_index = -1
        self.canvas.highlighted_nodes = []
        
        # 更新状态标签
        traversal_name = {
            "preorder": "前序遍历",
            "inorder": "中序遍历",
            "postorder": "后序遍历",
            "levelorder": "层序遍历"
        }.get(traverse_type, traverse_type)
        self.status_label.setText(f"准备{traversal_name}手动遍历...")
        
        # 启用遍历控制按钮
        self.prev_step_button.setEnabled(True)
        self.next_step_button.setEnabled(True)
        
        # 启用遍历播放控件（仿线性表）
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.replay_button.setEnabled(True)
            self.play_button.setText("播放")
        
        # 立即显示第一个节点
        if node_ids and len(node_ids) > 0:
            self.canvas.highlighted_nodes = [node_ids[0]]
            self.canvas.current_traversal_index = 0
            self.status_label.setText(f"{traversal_name}遍历步骤: 1/{len(path)}")
            # 强制重绘画布
            self.canvas.update()
            QApplication.processEvents()
            # 自动开始播放
            self._start_traversal_playback()
    
    def show_huffman_build_animation(self, build_steps):
        """显示哈夫曼树构建过程的动画
        
        Args:
            build_steps: 构建过程中的每一步状态
        """
        if not build_steps:
            return
        
        # 停止任何正在进行的动画
        self.stop_huffman_animation()
        
        # 设置构建步骤数据
        self.huffman_build_steps = build_steps
        self.current_build_step = 0
        
        # 更新状态标签
        self.status_label.setText(f"哈夫曼树构建动画开始，共{len(build_steps)}步")
        
        # 开始动画
        self.start_huffman_build_animation()
    
    def show_avl_build_animation(self, build_steps, inserted_value=None):
        """显示AVL树构建过程的动画
        
        Args:
            build_steps: 构建过程中的每一步状态
            inserted_value: 插入的值，用于在动画完成后显示弹窗（仅用于单个插入操作）
        """
        if not build_steps:
            return
        
        # 停止任何正在进行的动画
        self.stop_avl_animation()
        
        # 设置构建步骤数据
        self.avl_build_steps = build_steps
        self.current_avl_step = 0
        self.inserted_value = inserted_value  # 保存插入的值
        
        # 更新状态标签
        self.status_label.setText(f"AVL树构建动画开始，共{len(build_steps)}步")
        
        # 开始动画
        self.start_avl_build_animation()

    def show_avl_delete_animation(self, delete_steps, deleted_value=None):
        """显示AVL树删除过程的动画
        
        Args:
            delete_steps: 删除过程中的每一步状态
            deleted_value: 被删除的值，用于在动画完成后显示弹窗
        """
        if not delete_steps:
            return
        
        # 停止任何正在进行的动画
        self.stop_avl_animation()
        
        # 设置删除步骤数据
        self.avl_delete_steps = delete_steps
        self.current_avl_step = 0
        self.deleted_value = deleted_value  # 保存删除的值
        
        # 更新状态标签
        self.status_label.setText(f"AVL树删除动画开始，共{len(delete_steps)}步")
        
        # 开始动画
        self.start_avl_delete_animation()
 
    def show_bst_build_animation(self, build_steps):
        """显示BST构建过程的动画
        
        Args:
            build_steps: 构建过程中的每一步状态（来自 BST.build_with_steps）
        """
        if not build_steps:
            return
        
        # 停止任何正在进行的BST动画
        self.stop_bst_animation()
        
        # 设置构建步骤数据
        self.bst_build_steps = build_steps
        self.current_bst_step = 0
        
        # 更新状态标签
        self.status_label.setText(f"BST构建动画开始，共{len(build_steps)}步")
        
        # 开始动画
        self.start_bst_build_animation()
 
    def start_bst_build_animation(self):
        """开始BST构建动画"""
        if not getattr(self, 'bst_build_steps', []):
            return
        
        # 停止其他动画，避免冲突
        if hasattr(self, 'huffman_animation_timer') and self.huffman_animation_timer.isActive():
            self.huffman_animation_timer.stop()
        if hasattr(self, 'avl_animation_timer') and self.avl_animation_timer.isActive():
            self.avl_animation_timer.stop()
        if hasattr(self, 'bst_animation_timer') and self.bst_animation_timer.isActive():
            self.bst_animation_timer.stop()
        
        # 初始化动画状态
        self.current_bst_step = 0
        
        # 显示第一步
        self._show_bst_step(0)
        
        # 启用上一步/下一步按钮
        if hasattr(self, 'prev_step_button'):
            self.prev_step_button.setEnabled(False)
        if hasattr(self, 'next_step_button'):
            self.next_step_button.setEnabled(True)
        
        # 启用播放/重播并设为播放中
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.play_button.setText("暂停")
        if hasattr(self, 'replay_button'):
            self.replay_button.setEnabled(True)
        
        self.status_label.setText(f"BST构建步骤 1/{len(self.bst_build_steps)}")
        
        # 自动播放
        self.bst_animation_timer.start(self.animation_speed)
 
    def stop_bst_animation(self):
        """停止BST构建动画"""
        if hasattr(self, 'bst_animation_timer') and self.bst_animation_timer.isActive():
            self.bst_animation_timer.stop()
        self.current_bst_step = 0
 
    def _animate_bst_build(self):
        """BST构建动画处理函数"""
        if not getattr(self, 'bst_build_steps', []):
            self.bst_animation_timer.stop()
            return
        
        # 移动到下一步
        self.current_bst_step += 1
        
        # 检查是否完成动画
        if self.current_bst_step >= len(self.bst_build_steps):
            self.bst_animation_timer.stop()
            self.status_label.setText("BST构建动画完成")
            return
        
        self._show_bst_step(self.current_bst_step)
 
    def _show_bst_step(self, step_index):
        """显示BST构建的某一步（兼容快照并计算坐标）"""
        if not hasattr(self, 'bst_build_steps') or step_index < 0 or step_index >= len(self.bst_build_steps):
            return
        step_data = self.bst_build_steps[step_index]
        
        # 更新状态标签
        description = step_data.get('description') or step_data.get('action') or f"步骤 {step_index + 1}"
        self.status_label.setText(f"步骤 {step_index + 1}/{len(self.bst_build_steps)}: {description}")
        
        # 准备可视化数据
        visualization_data = {
            'type': 'bst',
            'nodes': [],
            'highlighted': []
        }
        
        # 兼容 tree/current_tree/tree_data 等字段名
        tree_snapshot = step_data.get('tree') or step_data.get('current_tree') or step_data.get('tree_data')
        if tree_snapshot:
            nodes = tree_snapshot.get('nodes', [])
            # 直接沿用模型提供的 level/x_pos/parent_id
            for node in nodes:
                n = {
                    'id': node.get('id'),
                    'value': node.get('value', node.get('data')),
                    'level': node.get('level', 0),
                    'x_pos': node.get('x_pos', 0.5),
                    'parent_id': node.get('parent_id') if node.get('parent_id') is not None else node.get('parent')
                }
                visualization_data['nodes'].append(n)
        
        # 待插入节点（如有），以虚线标注
        pending = step_data.get('pending_node')
        if pending:
            visualization_data['nodes'].append({
                'id': pending.get('id', -1),
                'value': pending.get('value'),
                'level': max([n.get('level', 0) for n in visualization_data['nodes']] + [0]) + 1,
                'x_pos': 0.5,
                'is_pending': True
            })
        
        # 高亮值 -> 映射为节点ID
        highlight_values = step_data.get('highlight_values', [])
        if highlight_values and visualization_data['nodes']:
            value_to_id = {}
            for n in visualization_data['nodes']:
                v = n.get('value')
                if v is not None and n.get('id') is not None:
                    value_to_id.setdefault(v, []).append(n.get('id'))
            highlighted_ids = []
            for v in highlight_values:
                ids = value_to_id.get(v) or []
                highlighted_ids.extend(ids)
            visualization_data['highlighted'] = highlighted_ids
        
        # 更新画布
        try:
            self.canvas.update_data(visualization_data)
            self.canvas.update()
            QApplication.processEvents()
        except Exception:
            pass
 
    def _prev_bst_step(self):
        """显示BST构建的上一步"""
        if not getattr(self, 'bst_build_steps', []):
            return
        if self.current_bst_step > 0:
            self.current_bst_step -= 1
            self._show_bst_step(self.current_bst_step)
            self.next_step_button.setEnabled(True)
            if self.current_bst_step == 0:
                self.prev_step_button.setEnabled(False)
            self.status_label.setText(f"BST构建步骤 {self.current_bst_step + 1}/{len(self.bst_build_steps)}")
 
    def _next_bst_step(self):
        """显示BST构建的下一步"""
        if not getattr(self, 'bst_build_steps', []):
            return
        if self.current_bst_step < len(self.bst_build_steps) - 1:
            self.current_bst_step += 1
            self._show_bst_step(self.current_bst_step)
            self.prev_step_button.setEnabled(True)
            if self.current_bst_step == len(self.bst_build_steps) - 1:
                self.next_step_button.setEnabled(False)
                self.status_label.setText("BST构建完成")
            else:
                self.status_label.setText(f"BST构建步骤 {self.current_bst_step + 1}/{len(self.bst_build_steps)}")
        else:
            self.status_label.setText("BST构建完成")
 
    def show_result(self, operation, result):
        """显示操作结果
        
        Args:
            operation: 操作类型
            result: 操作结果
        """
        if operation == "search":
            # 搜索结果弹窗
            found = result.get('found', False)
            if found:
                QMessageBox.information(self, "搜索结果", f"找到节点: {result.get('value')}")
            else:
                QMessageBox.information(self, "搜索结果", f"未找到节点: {result.get('value')}")
        elif operation == "traverse":
            # 遍历结果弹窗已移至动画结束后显示，这里不再显示
            if 'result' in result:
                # 显示遍历结果
                QMessageBox.information(self, "遍历结果", f"遍历结果: {', '.join(map(str, result['result']))}")
        elif operation == "huffman_build":
            # 哈夫曼树构建结果
            QMessageBox.information(self, "哈夫曼树构建", "哈夫曼树构建完成")
        elif operation == "huffman_encode":
            # 哈夫曼编码结果
            QMessageBox.information(self, "哈夫曼编码", f"编码结果: {result.get('encoded', '')}")
        elif operation == "huffman_decode":
            # 哈夫曼解码结果
            QMessageBox.information(self, "哈夫曼解码", f"解码结果: {result.get('decoded', '')}")
        else:
            # 其他操作结果
            QMessageBox.information(self, "操作结果", str(result))
        
        # 更新状态
        self.status_label.setText(f"操作 {operation} 完成")
    
    def _format_code_table(self, code_table):
        """格式化编码表
        
        Args:
            code_table: 编码表字典
            
        Returns:
            格式化后的编码表字符串
        """
        return "\n".join([f"{char}: {code}" for char, code in code_table.items()])
    
    def _build_huffman_animation(self):
        """触发哈夫曼树构建动画"""
        # 获取输入的频率数据
        values_text = self.value_input.text().strip()
        
        if not values_text:
            QMessageBox.warning(self, "警告", "请输入频率数据")
            return
        
        try:
            # 解析用户输入的频率对，格式如：A:5,B:9,C:12
            frequencies = {}
            pairs = values_text.split(",")
            for pair in pairs:
                if ":" in pair:
                    char, freq = pair.split(":")
                    frequencies[char.strip()] = int(freq.strip())
                else:
                    raise ValueError("哈夫曼树输入格式应为：字符:频率,字符:频率,...")
            
            # 发射操作信号，包含频率数据
            self.operation_triggered.emit("build_huffman", {
                "frequencies": frequencies
            })
            
            # 初始化动画状态
            if self.huffman_build_steps:
                self.current_build_step = 0
                self._show_huffman_step(0)
                
                # 启用上一步/下一步按钮
                self.prev_step_button.setEnabled(False)  # 第一步不能再往前
                self.next_step_button.setEnabled(True)
                
                self.status_label.setText("哈夫曼树构建动画准备就绪，请点击下一步继续")
            
        except ValueError as e:
            QMessageBox.warning(self, "警告", str(e) if str(e) else "请输入有效的频率数据")
    
    def _prev_step(self):
        """通用的上一步方法，根据当前动画类型调用相应的方法"""
        # 优先检查AVL树删除动画
        if hasattr(self, 'avl_delete_steps') and self.avl_delete_steps:
            self._prev_avl_delete_step()
        # 然后检查AVL树构建动画
        elif hasattr(self, 'avl_build_steps') and self.avl_build_steps:
            self._prev_avl_step()
        # 然后检查BST构建动画
        elif hasattr(self, 'bst_build_steps') and self.bst_build_steps:
            self._prev_bst_step()
        # 然后检查哈夫曼树构建动画
        elif hasattr(self, 'huffman_build_steps') and self.huffman_build_steps:
            self._prev_huffman_step()
        # 最后检查遍历和搜索动画
        elif hasattr(self.canvas, 'traversal_order') and hasattr(self.canvas, 'traversal_type'):
            self._prev_traversal_step()
        elif hasattr(self.canvas, 'search_target'):
            self._prev_traversal_step()  # 搜索动画也使用遍历步骤控制

    def _next_step(self):
        """通用的下一步方法，根据当前动画类型调用相应的方法"""
        # 优先检查AVL树删除动画
        if hasattr(self, 'avl_delete_steps') and self.avl_delete_steps:
            self._next_avl_delete_step()
        # 然后检查AVL树构建动画
        elif hasattr(self, 'avl_build_steps') and self.avl_build_steps:
            self._next_avl_step()
        # 然后检查BST构建动画
        elif hasattr(self, 'bst_build_steps') and self.bst_build_steps:
            self._next_bst_step()
        # 然后检查哈夫曼树构建动画
        elif hasattr(self, 'huffman_build_steps') and self.huffman_build_steps:
            self._next_huffman_step()
        # 最后检查遍历和搜索动画
        elif hasattr(self.canvas, 'traversal_order') and hasattr(self.canvas, 'traversal_type'):
            self._next_traversal_step()
        elif hasattr(self.canvas, 'search_target'):
            self._next_traversal_step()  # 搜索动画也使用遍历步骤控制
    
    def _prev_huffman_step(self):
        """显示哈夫曼树构建的上一步"""
        if not self.huffman_build_steps:
            return
            
        # 移动到上一步
        if self.current_build_step > 0:
            self.current_build_step -= 1
            self._show_huffman_step(self.current_build_step)
            
            # 更新按钮状态
            self.next_step_button.setEnabled(True)
            if self.current_build_step == 0:
                self.prev_step_button.setEnabled(False)
                
            self.status_label.setText(f"哈夫曼树构建步骤 {self.current_build_step + 1}/{len(self.huffman_build_steps)}")
    
    def _next_huffman_step(self):
        """显示哈夫曼树构建的下一步"""
        if not self.huffman_build_steps:
            return
            
        # 移动到下一步
        if self.current_build_step < len(self.huffman_build_steps) - 1:
            self.current_build_step += 1
            self._show_huffman_step(self.current_build_step)
            
            # 更新按钮状态
            self.prev_step_button.setEnabled(True)
            
            # 检查是否到达最后一步
            if self.current_build_step == len(self.huffman_build_steps) - 1:
                self.next_step_button.setEnabled(False)
                self.status_label.setText("哈夫曼树构建完成")
            else:
                self.status_label.setText(f"哈夫曼树构建步骤 {self.current_build_step + 1}/{len(self.huffman_build_steps)}")
        else:
            # 已经是最后一步，显示最终结果
            self.status_label.setText("哈夫曼树构建完成")
    
    def _prev_avl_step(self):
        """显示AVL树构建的上一步"""
        if not self.avl_build_steps:
            return
            
        # 移动到上一步
        if self.current_avl_step > 0:
            self.current_avl_step -= 1
            self._show_avl_step(self.current_avl_step)
            
            # 更新按钮状态
            self.next_step_button.setEnabled(True)
            if self.current_avl_step == 0:
                self.prev_step_button.setEnabled(False)
                
            self.status_label.setText(f"AVL树构建步骤 {self.current_avl_step + 1}/{len(self.avl_build_steps)}")
    
    def _prev_avl_delete_step(self):
        """显示AVL树删除的上一步"""
        if not self.avl_delete_steps:
            return
            
        # 移动到上一步
        if self.current_avl_step > 0:
            self.current_avl_step -= 1
            self._show_avl_delete_step(self.current_avl_step)
            
            # 更新按钮状态
            self.next_step_button.setEnabled(True)
            if self.current_avl_step == 0:
                self.prev_step_button.setEnabled(False)
                
            self.status_label.setText(f"AVL树删除步骤 {self.current_avl_step + 1}/{len(self.avl_delete_steps)}")
    
    def _next_avl_step(self):
        """显示AVL树构建的下一步"""
        if not self.avl_build_steps:
            return
            
        # 移动到下一步
        if self.current_avl_step < len(self.avl_build_steps) - 1:
            self.current_avl_step += 1
            self._show_avl_step(self.current_avl_step)
            
            # 更新按钮状态
            self.prev_step_button.setEnabled(True)
            
            # 检查是否到达最后一步
            if self.current_avl_step == len(self.avl_build_steps) - 1:
                self.next_step_button.setEnabled(False)
                self.status_label.setText("AVL树构建完成")
                
                # 在动画完成时显示插入成功弹窗（仅用于单个插入操作）
                if hasattr(self, 'inserted_value') and self.inserted_value is not None:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "成功", f"成功插入节点 {self.inserted_value}")
                    self.inserted_value = None  # 清除保存的值
            else:
                self.status_label.setText(f"AVL树构建步骤 {self.current_avl_step + 1}/{len(self.avl_build_steps)}")
        else:
            # 已经是最后一步，显示最终结果
            self.status_label.setText("AVL树构建完成")
    
    def _next_avl_delete_step(self):
        """显示AVL树删除的下一步"""
        if not self.avl_delete_steps:
            return
            
        # 移动到下一步
        if self.current_avl_step < len(self.avl_delete_steps) - 1:
            self.current_avl_step += 1
            self._show_avl_delete_step(self.current_avl_step)
            
            # 更新按钮状态
            self.prev_step_button.setEnabled(True)
            
            # 检查是否到达最后一步
            if self.current_avl_step == len(self.avl_delete_steps) - 1:
                self.next_step_button.setEnabled(False)
                self.status_label.setText("AVL树删除完成")
                
                # 在动画完成时显示删除成功弹窗
                if hasattr(self, 'deleted_value') and self.deleted_value is not None:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "成功", f"成功删除节点 {self.deleted_value}")
                    self.deleted_value = None  # 清除保存的值
            else:
                self.status_label.setText(f"AVL树删除步骤 {self.current_avl_step + 1}/{len(self.avl_delete_steps)}")
        else:
            # 已经是最后一步，显示最终结果
            self.status_label.setText("AVL树删除完成")
    
    def _change_animation_speed(self):
        """改变动画播放速度"""
        # 循环切换速度：正常 -> 快速 -> 慢速 -> 正常
        if self.animation_speed == 1000:  # 正常速度
            self.animation_speed = 500   # 快速
        elif self.animation_speed == 500:  # 快速
            self.animation_speed = 2000  # 慢速
        else:  # 慢速
            self.animation_speed = 1000  # 正常
        
        # 如果动画正在播放，更新定时器间隔
        if self.huffman_animation_timer.isActive():
            self.huffman_animation_timer.setInterval(self.animation_speed)
        if hasattr(self, 'avl_animation_timer') and self.avl_animation_timer.isActive():
            self.avl_animation_timer.setInterval(self.animation_speed)
        if hasattr(self, 'bst_animation_timer') and self.bst_animation_timer.isActive():
            self.bst_animation_timer.setInterval(self.animation_speed)
    
    def start_huffman_build_animation(self):
        """开始哈夫曼树构建动画"""
        if not self.huffman_build_steps:
            return
        
        # 停止任何正在进行的动画
        if self.huffman_animation_timer.isActive():
            self.huffman_animation_timer.stop()
        
        # 初始化动画状态
        self.current_build_step = 0
        
        # 显示第一步
        self._show_huffman_step(0)
        
        # 启用上一步/下一步按钮
        self.prev_step_button.setEnabled(False)  # 第一步不能再往前
        self.next_step_button.setEnabled(True)
        
        # 启用播放/重播按钮并设为播放中
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
        if hasattr(self, 'replay_button'):
            self.replay_button.setEnabled(True)
        if hasattr(self, 'play_button'):
            self.play_button.setText("暂停")
        
        self.status_label.setText(f"哈夫曼树构建步骤 1/{len(self.huffman_build_steps)}")
        
        # 自动播放哈夫曼构建动画
        self.huffman_animation_timer.start(self.animation_speed)
    
    def stop_huffman_animation(self):
        """停止哈夫曼树构建动画"""
        if self.huffman_animation_timer.isActive():
            self.huffman_animation_timer.stop()
        
        # 重置动画状态
        self.current_build_step = 0
    
    def _animate_huffman_build(self):
        """哈夫曼树构建动画处理函数"""
        if not self.huffman_build_steps:
            self.huffman_animation_timer.stop()
            return
        
        # 移动到下一步
        self.current_build_step += 1
        
        # 检查是否完成动画
        if self.current_build_step >= len(self.huffman_build_steps):
            # 动画完成，停止定时器
            self.huffman_animation_timer.stop()
            self.status_label.setText("哈夫曼树构建动画完成")
            return
        
        # 显示当前步骤
        self._show_huffman_step(self.current_build_step)
    
    # 已移除重复的 _animate_avl_build 定义（保留前文更健壮版本）
    

    
    def _show_huffman_step(self, step_index):
        """显示哈夫曼树构建的特定步骤"""
        if step_index >= len(self.huffman_build_steps):
            return
        
        step_data = self.huffman_build_steps[step_index]
        
        # 更新状态标签
        description = step_data.get('description', f'步骤 {step_index + 1}')
        self.status_label.setText(f"步骤 {step_index + 1}/{len(self.huffman_build_steps)}: {description}")
        
        # 准备可视化数据
        visualization_data = {
            'type': 'huffman_tree',
            'nodes': [],
            'highlighted': step_data.get('highlight_nodes', [])
        }
        
        # 根据步骤类型显示不同内容
        action = step_data.get('action', 'unknown')
        
        if action == 'initialize':
            # 初始化步骤：显示优先队列中的节点
            queue_nodes = step_data.get('queue_nodes', [])
            for i, node in enumerate(queue_nodes):
                visualization_data['nodes'].append({
                    'id': node['id'],
                    'value': f"{node['char']}:{node['freq']}" if node['char'] else f"内部:{node['freq']}",
                    'freq': node['freq'],
                    'char': node['char'],
                    'level': 0,
                    'x_pos': 0.1 + (0.8 * i / (len(queue_nodes) - 1 if len(queue_nodes) > 1 else 1)),
                    'is_leaf': node.get('is_leaf', True)
                })
        
        elif action == 'merge':
            # 合并步骤：显示当前树和剩余队列节点
            current_tree = step_data.get('current_tree')
            if current_tree and current_tree.get('nodes'):
                # 添加当前树的节点
                tree_nodes = current_tree['nodes']
                for node in tree_nodes:
                    visualization_data['nodes'].append({
                        'id': node['id'],
                        'value': f"{node['char']}:{node['freq']}" if node['char'] else f"内部:{node['freq']}",
                        'freq': node['freq'],
                        'char': node['char'],
                        'level': self._calculate_node_level(node, tree_nodes),
                        'x_pos': self._calculate_node_x_pos(node, tree_nodes),
                        'is_leaf': node.get('is_leaf', node['char'] is not None),
                        'parent_id': node.get('parent_id')
                    })
            
            # 添加队列中剩余的节点（显示在底部）
            queue_nodes = step_data.get('queue_nodes', [])
            max_level = max([node.get('level', 0) for node in visualization_data['nodes']], default=0)
            for i, node in enumerate(queue_nodes):
                visualization_data['nodes'].append({
                    'id': node['id'],
                    'value': f"{node['char']}:{node['freq']}" if node['char'] else f"内部:{node['freq']}",
                    'freq': node['freq'],
                    'char': node['char'],
                    'level': max_level + 2,  # 放在树的下方
                    'x_pos': 0.1 + (0.8 * i / (len(queue_nodes) - 1 if len(queue_nodes) > 1 else 1)),
                    'is_leaf': node.get('is_leaf', True)
                })
        
        elif action == 'complete':
            # 完成步骤：显示最终的哈夫曼树
            final_tree = step_data.get('current_tree')
            if final_tree and final_tree.get('nodes'):
                tree_nodes = final_tree['nodes']
                for node in tree_nodes:
                    visualization_data['nodes'].append({
                        'id': node['id'],
                        'value': f"{node['char']}:{node['freq']}" if node['char'] else f"内部:{node['freq']}",
                        'freq': node['freq'],
                        'char': node['char'],
                        'level': self._calculate_node_level(node, tree_nodes),
                        'x_pos': self._calculate_node_x_pos(node, tree_nodes),
                        'is_leaf': node.get('is_leaf', node['char'] is not None),
                        'parent_id': node.get('parent_id')
                    })
        
        # 更新画布数据
        self.canvas.update_data(visualization_data)
    
    def _show_avl_delete_step(self, step_index):
        """显示 AVL 删除动画的某一步（兼容多种快照结构并计算坐标）"""
        if not hasattr(self, 'avl_delete_steps') or step_index < 0 or step_index >= len(self.avl_delete_steps):
            return

        step_data = self.avl_delete_steps[step_index]

        # 更新状态标签
        description = step_data.get('description') or step_data.get('action') or f"步骤 {step_index + 1}"
        self.status_label.setText(f"步骤 {step_index + 1}/{len(self.avl_delete_steps)}: {description}")

        # 准备可视化数据
        visualization_data = {
            'type': 'avl_tree',
            'nodes': [],
            'highlighted': step_data.get('highlight_nodes', [])
        }

        # 兼容 tree/current_tree/tree_data 等不同字段命名的快照
        tree_snapshot = step_data.get('tree') or step_data.get('current_tree') or step_data.get('tree_data')
        if tree_snapshot:
            nodes = tree_snapshot.get('nodes', [])
            edges = tree_snapshot.get('edges') or tree_snapshot.get('links') or []
            parent_map = {}
            # 从边构建 parent 映射（若节点里未提供 parent_id）
            for edge in edges:
                src = edge.get('source', edge.get('from'))
                tgt = edge.get('target', edge.get('to'))
                if src is not None and tgt is not None:
                    parent_map[tgt] = src

            for node in nodes:
                nid = node.get('id')
                val = node.get('value', node.get('data'))
                pid = node.get('parent_id', node.get('parent'))
                if pid is None and nid in parent_map:
                    pid = parent_map.get(nid)
                visualization_data['nodes'].append({
                    'id': nid,
                    'value': '' if val is None else str(val),
                    'parent_id': pid,
                    'height': node.get('height', 0),
                    'balance_factor': node.get('balance', node.get('balance_factor', 0)),
                    'level': node.get('level', 0),
                    'x_pos': node.get('x_pos', 0.5)
                })

            # 如果坐标信息缺失或需要更新，则计算节点的位置
            self._calculate_avl_node_positions(visualization_data['nodes'])

        # 更新画布数据
        try:
            self.canvas.update_data(visualization_data)
            self.canvas.update()
            QApplication.processEvents()
        except Exception:
            pass
    
    def _calculate_node_level(self, node, all_nodes):
        """计算节点的层级"""
        if node.get('parent_id') is None:
            return 0
        
        parent = next((n for n in all_nodes if n['id'] == node['parent_id']), None)
        if parent:
            return self._calculate_node_level(parent, all_nodes) + 1
        else:
            return 0
    
    def _calculate_node_x_pos(self, node, all_nodes):
        """计算节点的水平位置"""
        # 如果是根节点，放在中间
        if node.get('parent_id') is None:
            return 0.5
        
        # 找到父节点
        parent = next((n for n in all_nodes if n['id'] == node['parent_id']), None)
        if not parent:
            return 0.5
        
        # 找到所有兄弟节点
        siblings = [n for n in all_nodes if n.get('parent_id') == node['parent_id']]
        
        if len(siblings) == 1:
            # 如果只有一个子节点，放在父节点正下方
            return self._calculate_node_x_pos(parent, all_nodes)
        elif len(siblings) == 2:
            # 如果有两个子节点，分别放在左右
            parent_x = self._calculate_node_x_pos(parent, all_nodes)
            level = self._calculate_node_level(node, all_nodes)
            offset = 0.3 / (level + 1)  # 层级越深，偏移越小
            
            # 根据节点在兄弟中的位置决定左右
            if siblings[0]['id'] == node['id']:
                return parent_x - offset  # 左子节点
            else:
                return parent_x + offset  # 右子节点
        else:
            # 多个子节点的情况（理论上哈夫曼树不会出现）
            parent_x = self._calculate_node_x_pos(parent, all_nodes)
            sibling_index = next((i for i, s in enumerate(siblings) if s['id'] == node['id']), 0)
            offset = (sibling_index / (len(siblings) - 1) - 0.5) * 0.4
            return parent_x + offset

    def start_avl_build_animation(self):
        """开始AVL树构建动画"""
        if not hasattr(self, 'avl_build_steps') or not self.avl_build_steps:
            return
        
        # 停止任何正在进行的动画
        if hasattr(self, 'avl_animation_timer') and self.avl_animation_timer.isActive():
            self.avl_animation_timer.stop()
        
        # 初始化动画状态
        self.current_avl_step = 0
        
        # 显示第一步
        self._show_avl_step(0)
        
        # 启用上一步/下一步按钮
        if hasattr(self, 'prev_step_button'):
            self.prev_step_button.setEnabled(False)  # 第一步不能再往前
        if hasattr(self, 'next_step_button'):
            self.next_step_button.setEnabled(True)
        
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"AVL树构建步骤 1/{len(self.avl_build_steps)}")
        
        # 启用播放/重播按钮并设为播放中
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.play_button.setText("暂停")
        if hasattr(self, 'replay_button'):
            self.replay_button.setEnabled(True)
        
        # 自动播放AVL构建动画
        if hasattr(self, 'avl_animation_timer'):
            self.avl_animation_timer.start(self.animation_speed)

    def _animate_avl_build(self):
        """AVL树动画处理函数（构建/删除通用）"""
        # 根据当前是否有删除或构建步骤来选择动画数据源
        active_steps = None
        show_fn = None
        completion_text = None

        if hasattr(self, 'avl_delete_steps') and self.avl_delete_steps:
            active_steps = self.avl_delete_steps
            show_fn = self._show_avl_delete_step
            completion_text = "AVL树删除动画完成"
        elif hasattr(self, 'avl_build_steps') and self.avl_build_steps:
            active_steps = self.avl_build_steps
            show_fn = self._show_avl_step
            completion_text = "AVL树构建动画完成"
        else:
            if hasattr(self, 'avl_animation_timer'):
                self.avl_animation_timer.stop()
            return

        # 移动到下一步
        self.current_avl_step += 1

        # 检查是否完成动画
        if self.current_avl_step >= len(active_steps):
            if hasattr(self, 'avl_animation_timer'):
                self.avl_animation_timer.stop()
            if hasattr(self, 'status_label'):
                self.status_label.setText(completion_text)
            return

        # 显示当前步骤
        show_fn(self.current_avl_step)
    
    def start_avl_delete_animation(self):
        """开始AVL树删除动画"""
        if not hasattr(self, 'avl_delete_steps') or not self.avl_delete_steps:
            return
        
        # 停止任何正在进行的动画
        if hasattr(self, 'avl_animation_timer') and self.avl_animation_timer.isActive():
            self.avl_animation_timer.stop()
        
        # 初始化动画状态
        self.current_avl_step = 0
        
        # 显示第一步
        self._show_avl_delete_step(0)
        
        # 启用上一步/下一步按钮
        if hasattr(self, 'prev_step_button'):
            self.prev_step_button.setEnabled(False)  # 第一步不能再往前
        if hasattr(self, 'next_step_button'):
            self.next_step_button.setEnabled(True)
        
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"AVL树删除步骤 1/{len(self.avl_delete_steps)}")
        
        # 启用播放/重播按钮并设为播放中
        if hasattr(self, 'play_button'):
            self.play_button.setEnabled(True)
            self.play_button.setText("暂停")
        if hasattr(self, 'replay_button'):
            self.replay_button.setEnabled(True)
        
        # 自动播放AVL删除动画
        if hasattr(self, 'avl_animation_timer'):
            self.avl_animation_timer.start(self.animation_speed)


    def _show_avl_step(self, step_index):
        """显示AVL树构建的特定步骤（兼容多种步骤数据格式）"""
        if not hasattr(self, 'avl_build_steps') or step_index >= len(self.avl_build_steps):
            return

        step_data = self.avl_build_steps[step_index]

        # 更新状态标签
        description = step_data.get('description') or step_data.get('action') or step_data.get('type') or f'步骤 {step_index + 1}'
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"步骤 {step_index + 1}/{len(self.avl_build_steps)}: {description}")

        # 准备可视化数据
        visualization_data = {
            'type': 'avl_tree',
            'nodes': [],
            'highlighted': step_data.get('highlight_nodes', [])
        }

        # 支持三种树快照字段：tree（新格式）/ current_tree / tree_data（旧格式）
        tree_snapshot = step_data.get('tree') or step_data.get('current_tree') or step_data.get('tree_data')

        if tree_snapshot:
            nodes = tree_snapshot.get('nodes', [])
            # edges 或 links 均可，用来推导 parent_id
            edges = tree_snapshot.get('edges') or tree_snapshot.get('links') or []

            parent_map = {}
            for edge in edges:
                src = edge.get('source', edge.get('from'))
                tgt = edge.get('target', edge.get('to'))
                if src is not None and tgt is not None:
                    parent_map[tgt] = src

            # 转换为画布所需节点结构
            for node in nodes:
                nid = node.get('id')
                val = node.get('value', node.get('data'))
                pid = node.get('parent_id', node.get('parent'))
                if pid is None and nid in parent_map:
                    pid = parent_map.get(nid)
                visualization_data['nodes'].append({
                    'id': nid,
                    'value': '' if val is None else str(val),
                    'parent_id': pid,
                    'height': node.get('height', 0),
                    'balance_factor': node.get('balance', node.get('balance_factor', 0)),
                    'level': node.get('level', 0),
                    'x_pos': node.get('x_pos', 0.5),
                    'is_pending': node.get('is_pending', False)
                })

            # 计算AVL节点位置
            self._calculate_avl_node_positions(visualization_data['nodes'])

        # 兼容“待插入节点”旧格式
        pending_node = step_data.get('pending_node')
        if pending_node:
            visualization_data['nodes'].append({
                'id': pending_node.get('id'),
                'value': str(pending_node.get('value')),
                'level': pending_node.get('level', 0),
                'x_pos': pending_node.get('x_pos', 0.85),
                'parent_id': pending_node.get('parent_id'),
                'is_pending': True
            })

        # 更新画布
        if hasattr(self, 'canvas'):
            try:
                self.canvas.update_data(visualization_data)
                self.canvas.update()
                QApplication.processEvents()
            except Exception:
                pass

    def _calculate_avl_node_positions(self, nodes):
        """计算AVL树节点的层级和水平位置
        
        Args:
            nodes: 节点列表
        """
        if not nodes:
            return
        
        # 构建节点ID到节点的映射
        node_map = {node['id']: node for node in nodes}
        
        # 构建父子关系映射
        children_map = {}
        for node in nodes:
            parent_id = node.get('parent_id')
            if parent_id is not None:
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(node['id'])
        
        # 找出根节点
        root_nodes = [node for node in nodes if node.get('parent_id') is None]
        if not root_nodes:
            return
        
        root_node = root_nodes[0]
        
        # 计算每个节点的层级
        def calculate_level(node_id, level=0):
            node = node_map[node_id]
            node['level'] = level
            
            # 递归计算子节点层级
            if node_id in children_map:
                for child_id in children_map[node_id]:
                    calculate_level(child_id, level + 1)
        
        calculate_level(root_node['id'])
        
        # 计算每个节点的水平位置
        def calculate_x_position(node_id, left=0.0, right=1.0):
            node = node_map[node_id]
            
            # 当前节点位置在区间中间
            node['x_pos'] = (left + right) / 2
            
            # 如果有子节点，递归计算子节点位置
            if node_id in children_map:
                children = children_map[node_id]
                if len(children) == 1:
                    child_id = children[0]
                    mid = (left + right) / 2
                    # 根据数值判断左右；无法判断则默认左侧，避免垂直堆叠
                    try:
                        parent_val = float(node_map[node_id].get('value'))
                        child_val = float(node_map[child_id].get('value'))
                    except Exception:
                        parent_val = None
                        child_val = None
                    if parent_val is not None and child_val is not None:
                        if child_val < parent_val:
                            calculate_x_position(child_id, left, mid)  # 左子节点
                        else:
                            calculate_x_position(child_id, mid, right)  # 右子节点
                    else:
                        calculate_x_position(child_id, left, mid)
                elif len(children) == 2:
                    # 有两个子节点，分别放在左右
                    mid = (left + right) / 2
                    calculate_x_position(children[0], left, mid)  # 左子节点
                    calculate_x_position(children[1], mid, right)  # 右子节点
        
        calculate_x_position(root_node['id'])
    


    def stop_avl_animation(self):
        """停止所有AVL树动画（构建和删除）"""
        # 停止构建/删除动画定时器
        if hasattr(self, 'avl_animation_timer') and self.avl_animation_timer.isActive():
            self.avl_animation_timer.stop()
        
        # 重置播放索引，但保留步骤数据以支持重新播放
        if hasattr(self, 'current_avl_step'):
            self.current_avl_step = 0

    # —— 二叉树遍历播放控制（仿线性表）——
    def _on_traversal_timer_tick(self):
        """计时器推进遍历步骤"""
        if not hasattr(self.canvas, 'node_id_map') or not self.canvas.node_id_map:
            self._pause_traversal_playback()
            return
        self._next_traversal_step()
        # 若播放到末尾，自动暂停
        if self.canvas.current_traversal_index >= len(self.canvas.node_id_map) - 1:
            self._pause_traversal_playback()
            # 对哈夫曼播放，保留步骤函数设置的完成文案
            if getattr(self.canvas, 'traversal_type', None) in ("huffman_encode", "huffman_decode"):
                return
            # 若为搜索动画，结束后清理步骤状态与按钮，避免残留序号
            if getattr(self.canvas, 'traversal_type', None) == "search":
                try:
                    self.canvas.current_traversal_index = -1
                    self.canvas.highlighted_nodes = []
                    self.canvas.traversal_order = []
                    self.canvas.node_id_map = []
                    self.canvas.search_target = None
                    self.canvas.traversal_type = None
                    if hasattr(self, 'prev_step_button'):
                        self.prev_step_button.setEnabled(False)
                    if hasattr(self, 'next_step_button'):
                        self.next_step_button.setEnabled(False)
                    if hasattr(self, 'play_button'):
                        self.play_button.setText("播放")
                except Exception:
                    pass
                if hasattr(self, 'status_label'):
                    self.status_label.setText("动画完成")
                return
            # 重播模式下：恢复到操作后的状态
            if getattr(self, 'replay_in_progress', False) and hasattr(self, 'last_operation_after_state') and self.last_operation_after_state:
                try:
                    self.canvas.update_data(self.last_operation_after_state)
                    op_cn = {"insert": "插入", "delete": "删除"}.get(getattr(self, 'last_operation_type', ''), getattr(self, 'last_operation_type', ''))
                    val = getattr(self, 'last_operation_value', None)
                    if val is not None:
                        self.status_label.setText(f"已完成{op_cn}操作: {val}")
                    else:
                        self.status_label.setText("动画完成")
                except Exception:
                    self.status_label.setText("动画完成")
                finally:
                    self.replay_in_progress = False
            else:
                self.status_label.setText("动画完成")

    def _current_traversal_interval_ms(self):
        """根据速度选择器计算播放间隔"""
        try:
            text = self.speed_combo.currentText() if hasattr(self, 'speed_combo') else "1x"
            factor = 1.0
            if text.endswith('x'):
                factor = float(text[:-1])
        except Exception:
            factor = 1.0
        self.traversal_play_speed_factor = factor
        base = self.traversal_play_base_interval_ms
        return int(base / max(0.25, factor))

    def _start_traversal_playback(self):
        """开始自动播放遍历"""
        if not hasattr(self.canvas, 'node_id_map') or not self.canvas.node_id_map:
            return
        self.traversal_is_playing = True
        self.play_button.setText("暂停")
        self.traversal_play_timer.start(self._current_traversal_interval_ms())
        self.status_label.setText("播放中……")

    def _pause_traversal_playback(self):
        """暂停播放"""
        if hasattr(self, 'traversal_play_timer') and self.traversal_play_timer.isActive():
            self.traversal_play_timer.stop()
        self.traversal_is_playing = False
        if hasattr(self, 'play_button'):
            self.play_button.setText("播放")

    def _toggle_traversal_play(self):
        """切换播放/暂停（同时适配哈夫曼与AVL构建/删除动画）"""
        # 若处于哈夫曼构建动画场景，优先控制哈夫曼定时器
        if hasattr(self, 'huffman_build_steps') and self.huffman_build_steps:
            # 若已到结尾，重播构建动画
            if getattr(self, 'current_build_step', 0) >= len(self.huffman_build_steps):
                self.stop_huffman_animation()
                self.start_huffman_build_animation()
                return
            # 切换播放/暂停
            if self.huffman_animation_timer.isActive():
                self.huffman_animation_timer.stop()
                if hasattr(self, 'play_button'):
                    self.play_button.setText("播放")
                self.status_label.setText("已暂停")
            else:
                self.huffman_animation_timer.start(self.animation_speed)
                if hasattr(self, 'play_button'):
                    self.play_button.setText("暂停")
                self.status_label.setText("播放中……")
            return
        
        # 若处于BST构建动画场景，控制BST定时器
        if hasattr(self, 'bst_build_steps') and self.bst_build_steps:
            total_steps = len(self.bst_build_steps)
            if getattr(self, 'current_bst_step', 0) >= total_steps:
                self.stop_bst_animation()
                self.start_bst_build_animation()
                return
            if self.bst_animation_timer.isActive():
                self.bst_animation_timer.stop()
                if hasattr(self, 'play_button'):
                    self.play_button.setText("播放")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("已暂停")
            else:
                self.bst_animation_timer.start(self.animation_speed)
                if hasattr(self, 'play_button'):
                    self.play_button.setText("暂停")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("播放中……")
            return
        
        # 若处于AVL构建/删除动画场景，控制AVL定时器（搜索场景优先使用遍历播放）
        if getattr(self.canvas, 'traversal_type', None) != "search" and ((hasattr(self, 'avl_delete_steps') and self.avl_delete_steps) or (hasattr(self, 'avl_build_steps') and self.avl_build_steps)):
            total_steps = len(self.avl_delete_steps) if getattr(self, 'avl_delete_steps', []) else len(self.avl_build_steps)
            if getattr(self, 'current_avl_step', 0) >= total_steps:
                self.stop_avl_animation()
                if getattr(self, 'avl_delete_steps', []):
                    self.start_avl_delete_animation()
                else:
                    self.start_avl_build_animation()
                return
            if self.avl_animation_timer.isActive():
                self.avl_animation_timer.stop()
                if hasattr(self, 'play_button'):
                    self.play_button.setText("播放")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("已暂停")
            else:
                self.avl_animation_timer.start(self.animation_speed)
                if hasattr(self, 'play_button'):
                    self.play_button.setText("暂停")
                if hasattr(self, 'status_label'):
                    self.status_label.setText("播放中……")
            return
        
        # 默认：控制遍历播放
        if not hasattr(self.canvas, 'node_id_map') or not self.canvas.node_id_map:
            return
        # 到达末尾则重播
        if self.canvas.current_traversal_index >= len(self.canvas.node_id_map) - 1:
            self._replay_traversal()
            self._start_traversal_playback()
            return
        if self.traversal_is_playing:
            self._pause_traversal_playback()
        else:
            self._start_traversal_playback()

    def _replay_traversal(self):
        """重置并从头播放（若有操作前状态，先显示再播放）"""
        # 若为哈夫曼构建动画，执行构建重播并返回
        if hasattr(self, 'huffman_build_steps') and self.huffman_build_steps:
            self.stop_huffman_animation()
            # 重新开始构建动画（展示第一步并自动播放）
            self.start_huffman_build_animation()
            # 播放按钮文本更新
            if hasattr(self, 'play_button'):
                self.play_button.setText("暂停")
            return
        
        # 若为BST构建动画，执行重播并返回
        if hasattr(self, 'bst_build_steps') and self.bst_build_steps:
            self.stop_bst_animation()
            self.start_bst_build_animation()
            if hasattr(self, 'play_button'):
                self.play_button.setText("暂停")
            return
        
        # 若为AVL构建/删除动画，执行重播并返回（搜索场景优先用遍历重播）
        if getattr(self.canvas, 'traversal_type', None) != "search" and ((hasattr(self, 'avl_delete_steps') and self.avl_delete_steps) or (hasattr(self, 'avl_build_steps') and self.avl_build_steps)):
            self.stop_avl_animation()
            if getattr(self, 'avl_delete_steps', []):
                self.start_avl_delete_animation()
            else:
                self.start_avl_build_animation()
            if hasattr(self, 'play_button'):
                self.play_button.setText("暂停")
            return
        
        self._pause_traversal_playback()
        # 停止可能的画布动画，避免冲突
        if hasattr(self.canvas, 'stop_animation'):
            self.canvas.stop_animation()
        # 若没有可播放路径，直接返回（但若有前态则恢复预览）
        if not hasattr(self.canvas, 'node_id_map') or not self.canvas.node_id_map:
            if hasattr(self, 'last_operation_before_state') and self.last_operation_before_state:
                try:
                    self.replay_in_progress = True
                    self.canvas.update_data(self.last_operation_before_state)
                    op_cn = {"insert": "插入", "delete": "删除"}.get(getattr(self, 'last_operation_type', ''), getattr(self, 'last_operation_type', ''))
                    val = getattr(self, 'last_operation_value', None)
                    if val is not None:
                        self.status_label.setText(f"重播：先显示{op_cn}前状态（值 {val}）")
                    else:
                        self.status_label.setText("重播：先显示操作前状态")
                except Exception:
                    pass
            return
        # 若当前是BST路径动画且有最近一次操作的前态，则先恢复并标记重播模式
        try:
            if getattr(self.canvas, 'traversal_type', None) in ("bst_insert", "bst_delete") and \
               hasattr(self, 'last_operation_before_state') and self.last_operation_before_state:
                self.replay_in_progress = True
                self.canvas.update_data(self.last_operation_before_state)
                op_cn = "插入" if getattr(self.canvas, 'traversal_type', None) == "bst_insert" else "删除"
                val = getattr(self, 'last_operation_value', None)
                if val is not None:
                    self.status_label.setText(f"重播：先显示{op_cn}前状态（值 {val}），随后自动播放")
                else:
                    self.status_label.setText(f"重播：先显示{op_cn}前状态，随后自动播放")
        except Exception:
            # 安全兜底，不影响后续重播
            pass
        # 重置索引与高亮
        self.canvas.current_traversal_index = -1
        self.canvas.highlighted_nodes = []
        self.prev_step_button.setEnabled(True)
        self.next_step_button.setEnabled(True)
        # 展示第一步并开始播放
        self._next_traversal_step()
        self._start_traversal_playback()

    def _update_traversal_speed(self):
        """更新速度设置"""
        if self.traversal_is_playing:
            self.traversal_play_timer.start(self._current_traversal_interval_ms())


class TreeCanvas(QWidget):
    """树形结构可视化画布"""
    
    def __init__(self):
        """初始化画布"""
        super().__init__()
        
        # 设置最小尺寸，允许画布根据内容自适应延伸
        self.setMinimumSize(800, 600)  # 设置初始最小尺寸
        
        # 初始化数据
        self.data = None
        self.structure_type = None
        
        # 节点样式
        self.node_radius = 20
        self.level_height = 80
        self.highlighted_nodes = []
        
        # 遍历相关
        self.traversal_order = []
        self.traversal_type = None
        self.current_traversal_index = -1
        
        # 动画定时器
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_traversal)
        self.animation_speed = 500  # 动画速度（毫秒）
    
    def _animate_traversal(self):
        """遍历动画处理函数"""
        # 检查是否有遍历顺序
        if not self.traversal_order or not hasattr(self, 'node_id_map') or len(self.node_id_map) == 0:
            self.animation_timer.stop()
            return
        
        # 更新当前遍历索引
        self.current_traversal_index += 1
        
        # 检查是否完成遍历
        if self.current_traversal_index >= len(self.traversal_order):
            # 遍历完成，停止定时器
            self.animation_timer.stop()
            
            # 动画结束后显示遍历结果弹窗
            parent = self.parent()
            while parent and not hasattr(parent, 'show_result'):
                parent = parent.parent()
            
            if parent and hasattr(parent, 'show_result') and self.traversal_order:
                result = {'result': self.traversal_order}
                parent.show_result("traverse", result)
            return
        
        # 更新高亮节点（显示当前节点）
        if self.current_traversal_index < len(self.node_id_map):
            current_node_id = self.node_id_map[self.current_traversal_index]
            self.highlighted_nodes = [current_node_id]
            

            
            # 强制重绘画布
            self.update()
            
            # 确保更新被处理
            QApplication.processEvents()
    
    def stop_animation(self):
        """停止动画"""
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        
        # 重置动画状态
        self.current_traversal_index = -1
        self.highlighted_nodes = []
    
    def update_data(self, data):
        """更新画布数据
        
        Args:
            data: 可视化数据，包含结构类型和节点
        """

        # 更新数据
        self.data = data.get("nodes", [])
        self.structure_type = data.get("type")
        self.highlighted_nodes = data.get("highlighted", [])
        
        # 如果是AVL树，需要计算节点位置
        if self.structure_type == "avl_tree" and self.data:
            self._calculate_avl_node_positions(self.data)
        
        # 触发重绘
        self.update()

    def _find_tree_view(self):
        parent = self.parent()
        while parent is not None:
            if hasattr(parent, 'operation_triggered'):
                return parent
            parent = parent.parent()
        return None

    def _get_parent_id(self, node):
        # parent_id 可能为 0，不能直接用 or 合并
        if 'parent_id' in node:
            return node.get('parent_id')
        return node.get('parent')

    def _derive_path(self, target_node):
        # 从可视化数据推导根到目标节点的路径（0/1 表示左/右）
        if not self.data:
            return []
        id_map = {n.get('id'): n for n in self.data}

        path_rev = []
        current = target_node
        while True:
            parent_id = self._get_parent_id(current)
            if parent_id is None:
                break  # 到达根节点
            parent = id_map.get(parent_id)
            if parent is None:
                break
            # 找到父节点的子节点集合
            children = []
            for n in self.data:
                pid = self._get_parent_id(n)
                if pid == parent.get('id'):
                    children.append(n)
            direction = 0
            if len(children) >= 2:
                # 通过 x_pos 判断左右
                left_child = min(children, key=lambda c: c.get('x_pos', 0.5))
                direction = 0 if current.get('id') == left_child.get('id') else 1
            else:
                # 只有一个子节点时，与父节点 x_pos 比较
                direction = 0 if current.get('x_pos', 0.5) < parent.get('x_pos', 0.5) else 1
            path_rev.append(direction)
            current = parent
        return list(reversed(path_rev))

    def mousePressEvent(self, event):
        # 命中测试，检测是否点击到某个节点
        if not self.data or len(self.data) == 0:
            return

        click_pos = event.pos()
        start_y = 50
        clicked = None
        for node in self.data:
            x = int(node.get('x_pos', 0.5) * self.width())
            y = int(start_y + node.get('level', 0) * self.level_height)
            dx = click_pos.x() - x
            dy = click_pos.y() - y
            if dx * dx + dy * dy <= self.node_radius * self.node_radius:
                clicked = node
                break

        if not clicked:
            return

        # 目前仅支持二叉树的节点点击菜单（AVL禁用右键菜单）
        if self.structure_type != 'binary_tree':
            return

        path = self._derive_path(clicked)
        tree_view = self._find_tree_view()
        if not tree_view:
            return

        # 构建上下文菜单（AVL移除路径插入，仅BinaryTree保留）
        menu = QMenu(self)
        action_insert_left = None
        action_insert_right = None
        if self.structure_type == 'binary_tree':
            action_insert_left = menu.addAction('插入左子节点')
            action_insert_right = menu.addAction('插入右子节点')
        action_delete = menu.addAction('删除该节点')

        chosen = menu.exec_(self.mapToGlobal(event.pos()))
        if chosen is None:
            return

        try:
            if self.structure_type == 'binary_tree' and chosen == action_insert_left:
                value, ok = QInputDialog.getInt(self, '插入左子节点', '输入整数值:')
                if ok:
                    emit_data = {
                        'structure_type': self.structure_type,
                        'value': value,
                        'position': path + [0]
                    }
                    tree_view.operation_triggered.emit('insert', emit_data)
            elif self.structure_type == 'binary_tree' and chosen == action_insert_right:
                value, ok = QInputDialog.getInt(self, '插入右子节点', '输入整数值:')
                if ok:
                    emit_data = {
                        'structure_type': self.structure_type,
                        'value': value,
                        'position': path + [1]
                    }
                    tree_view.operation_triggered.emit('insert', emit_data)
            elif chosen == action_delete:
                emit_data = {'structure_type': self.structure_type}
                if self.structure_type == 'binary_tree':
                    emit_data['position'] = path
                elif self.structure_type == 'avl_tree':
                    # AVL移除按路径删除，改为按值删除当前节点
                    emit_data['value'] = clicked.get('value')
                tree_view.operation_triggered.emit('delete', emit_data)
        except Exception:
            pass
    
    def _calculate_avl_node_positions(self, nodes):
        """计算AVL树节点的层级和水平位置
        
        Args:
            nodes: 节点列表
        """
        if not nodes:
            return
        
        # 构建节点ID到节点的映射
        node_map = {node['id']: node for node in nodes}
        
        # 构建父子关系映射
        children_map = {}
        for node in nodes:
            parent_id = node.get('parent_id')
            if parent_id is not None:
                if parent_id not in children_map:
                    children_map[parent_id] = []
                children_map[parent_id].append(node['id'])
        
        # 找出根节点
        root_nodes = [node for node in nodes if node.get('parent_id') is None]
        if not root_nodes:
            return
        
        root_node = root_nodes[0]
        
        # 计算每个节点的层级
        def calculate_level(node_id, level=0):
            node = node_map[node_id]
            node['level'] = level
            
            # 递归计算子节点层级
            if node_id in children_map:
                for child_id in children_map[node_id]:
                    calculate_level(child_id, level + 1)
        
        calculate_level(root_node['id'])
        
        # 计算每个节点的水平位置
        def calculate_x_position(node_id, left=0.0, right=1.0):
            node = node_map[node_id]
            
            # 当前节点位置在区间中间
            node['x_pos'] = (left + right) / 2
            
            # 如果有子节点，递归计算子节点位置
            if node_id in children_map:
                children = children_map[node_id]
                if len(children) == 1:
                    child_id = children[0]
                    mid = (left + right) / 2
                    # 根据数值判断左右；无法判断则默认左侧，避免垂直堆叠
                    try:
                        parent_val = float(node_map[node_id].get('value'))
                        child_val = float(node_map[child_id].get('value'))
                    except Exception:
                        parent_val = None
                        child_val = None
                    if parent_val is not None and child_val is not None:
                        if child_val < parent_val:
                            calculate_x_position(child_id, left, mid)  # 左子节点
                        else:
                            calculate_x_position(child_id, mid, right)  # 右子节点
                    else:
                        calculate_x_position(child_id, left, mid)
                elif len(children) == 2:
                    # 有两个子节点，分别放在左右
                    mid = (left + right) / 2
                    calculate_x_position(children[0], left, mid)  # 左子节点
                    calculate_x_position(children[1], mid, right)  # 右子节点
        
        calculate_x_position(root_node['id'])

    
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
        

        
        self._draw_tree(painter)
    
    def _draw_tree(self, painter):
        """绘制树
        
        Args:
            painter: QPainter对象
        """
        # 设置字体
        font = QFont("Arial", 10)
        painter.setFont(font)
        
        # 检查数据是否有效
        if not self.data:
            return
            
        try:
            # 计算树的高度和宽度
            max_level = max([node.get("level", 0) for node in self.data]) if self.data else 0
            tree_height = (max_level + 1) * self.level_height
            
            # 计算所需的画布尺寸
            required_width = (len(self.data) * 100) + 200  # 根据节点数量估算宽度
            required_height = tree_height + 100  # 根据层级估算高度
            
            # 如果所需尺寸超过当前尺寸，调整画布大小
            if required_width > self.width() or required_height > self.height():
                self.setMinimumSize(required_width, required_height)
                self.updateGeometry()
            
            # 计算画布中心点
            center_x = self.width() // 2
            start_y = 50
            
            # 首先绘制边
            for node in self.data:
                parent_id = node.get("parent_id")
                if parent_id is None:
                    parent_id = node.get("parent")
                
                # 注意：parent_id可能为0（根节点的子节点），所以不能用 if parent_id 判断
                if parent_id is not None:  # 包括parent_id为0的情况
                    # 找到父节点
                    parent = next((n for n in self.data if n.get("id") == parent_id), None)
                    if parent:
                        # 计算节点位置
                        parent_x = int(parent.get("x_pos", 0.5) * self.width())
                        parent_y = int(start_y + parent.get("level", 0) * self.level_height)
                        
                        node_x = int(node.get("x_pos", 0.5) * self.width())
                        node_y = int(start_y + node.get("level", 0) * self.level_height)
                        
                        # 绘制连接线
                        painter.setPen(QPen(Qt.black, 2))
                        painter.drawLine(parent_x, parent_y, node_x, node_y)
                        
        except Exception as e:
            # 绘制出错时静默处理
            return
        
        # 然后绘制节点
        try:
            for node in self.data:
                # 计算节点位置
                x = int(node.get("x_pos", 0.5) * self.width())
                y = int(start_y + node.get("level", 0) * self.level_height)
                
                # 设置节点颜色
                if node.get("is_pending"):
                    # 待插入节点 - 使用虚线边框和半透明填充
                    painter.setBrush(QBrush(QColor(255, 165, 0, 128)))  # 橙色半透明
                elif node.get("id") in self.highlighted_nodes:
                    # 高亮节点
                    painter.setBrush(QBrush(QColor(255, 200, 0)))
                else:
                    # 普通节点
                    painter.setBrush(QBrush(QColor(200, 240, 255)))
                
                # 显示遍历顺序
                if hasattr(self, 'traversal_order') and self.traversal_order and hasattr(self, 'node_id_map'):
                    # 查找节点在遍历路径中的位置
                    node_id = node.get("id")
                    if node_id in self.node_id_map:
                        index = self.node_id_map.index(node_id)
                        if index <= self.current_traversal_index:
                            # 在节点外部显示遍历顺序
                            order_text = str(index + 1)
                            painter.setPen(QPen(Qt.red, 2))
                            # 将数字放在节点的右上方，完全在节点外部
                            painter.drawText(x + self.node_radius + 5, y - self.node_radius - 5, order_text)
                
                # 绘制节点圆
                if node.get("is_pending"):
                    # 待插入节点使用虚线边框
                    pen = QPen(QColor(255, 140, 0), 2)  # 橙色边框
                    pen.setStyle(Qt.DashLine)  # 虚线样式
                    painter.setPen(pen)
                else:
                    painter.setPen(QPen(Qt.black, 2))
                painter.drawEllipse(x - self.node_radius, y - self.node_radius, 
                                  2 * self.node_radius, 2 * self.node_radius)
                
                # 绘制节点值
                painter.setPen(Qt.black)
                value_text = str(node.get("value", ""))
                # 计算文本宽度，以便居中显示
                text_width = painter.fontMetrics().width(value_text)
                painter.drawText(x - text_width // 2, y + 5, value_text)
                
                # 如果是待插入节点，添加标签
                if node.get("is_pending"):
                    painter.setPen(QPen(QColor(255, 140, 0), 2))
                    label_text = "待插入"
                    label_width = painter.fontMetrics().width(label_text)
                    painter.drawText(x - label_width // 2, y + self.node_radius + 20, label_text)
                
                # 如果是哈夫曼树，显示权重/频率
                if self.structure_type == "huffman_tree" and "weight" in node:
                    weight_text = f"({node['weight']})"
                    # 在节点下方显示权重
                    weight_width = painter.fontMetrics().width(weight_text)
                    painter.drawText(x - weight_width // 2, y + self.node_radius + 15, weight_text)
                elif self.structure_type == "huffman_tree" and "freq" in node:
                    freq_text = f"({node['freq']})"
                    # 在节点下方显示频率
                    freq_width = painter.fontMetrics().width(freq_text)
                    painter.drawText(x - freq_width // 2, y + self.node_radius + 15, freq_text)
                
                # 如果有编码，显示编码
                if "code" in node:
                    code_text = node["code"]
                    # 在节点上方显示编码
                    code_width = painter.fontMetrics().width(code_text)
                    painter.drawText(x - code_width // 2, y - self.node_radius - 5, code_text)
        except Exception as e:
            # 绘制节点出错时静默处理
            pass
            return
    
    # 已移除重复的 start_avl_build_animation 定义（保留前文更健壮版本）
    
    # 已移除重复的 stop_avl_animation 定义（保留前文整合版本）
    
    def _animate_avl_build(self):
        """AVL树构建动画处理函数"""
        if not self.avl_build_steps:
            self.avl_animation_timer.stop()
            return
        
        # 移动到下一步
        self.current_avl_step += 1
        
        # 检查是否完成动画
        if self.current_avl_step >= len(self.avl_build_steps):
            # 动画完成，停止定时器
            self.avl_animation_timer.stop()
            self.status_label.setText("AVL树构建动画完成")
            return
        
        # 显示当前步骤
        self._show_avl_step(self.current_avl_step)
    
    # 已移除重复的 _show_avl_step 定义（保留前文更健壮版本）