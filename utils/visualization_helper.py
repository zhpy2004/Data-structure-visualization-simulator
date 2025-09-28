#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
可视化辅助工具 - 提供数据结构可视化的辅助函数
"""

from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF
import math

# 颜色常量
NODE_COLOR = QColor(100, 181, 246)  # 节点填充色
NODE_BORDER_COLOR = QColor(25, 118, 210)  # 节点边框色
HIGHLIGHT_COLOR = QColor(255, 152, 0)  # 高亮色
ARROW_COLOR = QColor(66, 66, 66)  # 箭头颜色
TEXT_COLOR = QColor(33, 33, 33)  # 文本颜色
NULL_COLOR = QColor(189, 189, 189)  # 空节点颜色

# 尺寸常量
NODE_RADIUS = 25  # 节点半径
ARROW_SIZE = 10  # 箭头大小
LINE_WIDTH = 2  # 线宽
TEXT_FONT_SIZE = 12  # 文本字体大小
LABEL_FONT_SIZE = 10  # 标签字体大小


def draw_node(painter, x, y, value, highlighted=False, label=None):
    """绘制节点
    
    Args:
        painter: QPainter对象
        x: 节点中心x坐标
        y: 节点中心y坐标
        value: 节点值
        highlighted: 是否高亮
        label: 节点标签
    """
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 设置节点颜色
    if highlighted:
        painter.setBrush(QBrush(HIGHLIGHT_COLOR))
        painter.setPen(QPen(QColor(HIGHLIGHT_COLOR.darker(150)), LINE_WIDTH))
    else:
        painter.setBrush(QBrush(NODE_COLOR))
        painter.setPen(QPen(NODE_BORDER_COLOR, LINE_WIDTH))
    
    # 绘制圆形节点
    painter.drawEllipse(QRectF(x - NODE_RADIUS, y - NODE_RADIUS, 
                              2 * NODE_RADIUS, 2 * NODE_RADIUS))
    
    # 设置文本颜色和字体
    painter.setPen(QPen(TEXT_COLOR))
    font = QFont()
    font.setPointSize(TEXT_FONT_SIZE)
    painter.setFont(font)
    
    # 绘制节点值
    text = str(value)
    text_rect = QRectF(x - NODE_RADIUS, y - NODE_RADIUS, 
                      2 * NODE_RADIUS, 2 * NODE_RADIUS)
    painter.drawText(text_rect, Qt.AlignCenter, text)
    
    # 如果有标签，绘制标签
    if label:
        label_font = QFont()
        label_font.setPointSize(LABEL_FONT_SIZE)
        painter.setFont(label_font)
        painter.setPen(QPen(QColor(33, 33, 33, 180)))
        label_rect = QRectF(x - NODE_RADIUS, y + NODE_RADIUS + 2, 
                           2 * NODE_RADIUS, LABEL_FONT_SIZE + 4)
        painter.drawText(label_rect, Qt.AlignCenter, label)
    
    # 恢复画笔状态
    painter.restore()


def draw_null_node(painter, x, y):
    """绘制空节点
    
    Args:
        painter: QPainter对象
        x: 节点中心x坐标
        y: 节点中心y坐标
    """
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 设置节点颜色
    painter.setBrush(Qt.NoBrush)
    painter.setPen(QPen(NULL_COLOR, LINE_WIDTH, Qt.DashLine))
    
    # 绘制圆形节点
    null_radius = NODE_RADIUS * 0.7
    painter.drawEllipse(QRectF(x - null_radius, y - null_radius, 
                              2 * null_radius, 2 * null_radius))
    
    # 绘制NULL文本
    painter.setPen(QPen(NULL_COLOR))
    font = QFont()
    font.setPointSize(LABEL_FONT_SIZE)
    painter.setFont(font)
    text_rect = QRectF(x - null_radius, y - null_radius, 
                      2 * null_radius, 2 * null_radius)
    painter.drawText(text_rect, Qt.AlignCenter, "NULL")
    
    # 恢复画笔状态
    painter.restore()


def draw_arrow(painter, start_x, start_y, end_x, end_y, highlighted=False):
    """绘制箭头
    
    Args:
        painter: QPainter对象
        start_x: 起点x坐标
        start_y: 起点y坐标
        end_x: 终点x坐标
        end_y: 终点y坐标
        highlighted: 是否高亮
    """
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 计算方向向量
    dx = end_x - start_x
    dy = end_y - start_y
    length = math.sqrt(dx * dx + dy * dy)
    
    if length < 1e-6:
        painter.restore()
        return
    
    # 单位向量
    dx, dy = dx / length, dy / length
    
    # 调整起点和终点，避免箭头与节点重叠
    start_x += dx * NODE_RADIUS
    start_y += dy * NODE_RADIUS
    end_x -= dx * NODE_RADIUS
    end_y -= dy * NODE_RADIUS
    
    # 设置箭头颜色
    if highlighted:
        painter.setPen(QPen(HIGHLIGHT_COLOR, LINE_WIDTH))
    else:
        painter.setPen(QPen(ARROW_COLOR, LINE_WIDTH))
    
    # 绘制线段
    painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))
    
    # 计算箭头
    angle = math.atan2(dy, dx)
    arrow_angle1 = angle + math.pi * 3/4
    arrow_angle2 = angle - math.pi * 3/4
    
    arrow_point1 = QPointF(end_x + ARROW_SIZE * math.cos(arrow_angle1),
                           end_y + ARROW_SIZE * math.sin(arrow_angle1))
    arrow_point2 = QPointF(end_x + ARROW_SIZE * math.cos(arrow_angle2),
                           end_y + ARROW_SIZE * math.sin(arrow_angle2))
    
    # 绘制箭头
    arrow_points = [QPointF(end_x, end_y), arrow_point1, arrow_point2]
    
    if highlighted:
        painter.setBrush(QBrush(HIGHLIGHT_COLOR))
    else:
        painter.setBrush(QBrush(ARROW_COLOR))
    
    painter.drawPolygon(arrow_points)
    
    # 恢复画笔状态
    painter.restore()


def draw_array_cell(painter, x, y, width, height, value, index, highlighted=False):
    """绘制数组单元格
    
    Args:
        painter: QPainter对象
        x: 左上角x坐标
        y: 左上角y坐标
        width: 宽度
        height: 高度
        value: 单元格值
        index: 单元格索引
        highlighted: 是否高亮
    """
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 设置单元格颜色
    if highlighted:
        painter.setBrush(QBrush(HIGHLIGHT_COLOR))
        painter.setPen(QPen(QColor(HIGHLIGHT_COLOR.darker(150)), LINE_WIDTH))
    else:
        painter.setBrush(QBrush(NODE_COLOR))
        painter.setPen(QPen(NODE_BORDER_COLOR, LINE_WIDTH))
    
    # 绘制矩形单元格
    painter.drawRect(QRectF(x, y, width, height))
    
    # 设置文本颜色和字体
    painter.setPen(QPen(TEXT_COLOR))
    font = QFont()
    font.setPointSize(TEXT_FONT_SIZE)
    painter.setFont(font)
    
    # 绘制单元格值
    value_rect = QRectF(x, y, width, height)
    painter.drawText(value_rect, Qt.AlignCenter, str(value))
    
    # 绘制索引标签
    label_font = QFont()
    label_font.setPointSize(LABEL_FONT_SIZE)
    painter.setFont(label_font)
    painter.setPen(QPen(QColor(33, 33, 33, 180)))
    label_rect = QRectF(x, y + height + 2, width, LABEL_FONT_SIZE + 4)
    painter.drawText(label_rect, Qt.AlignCenter, str(index))
    
    # 恢复画笔状态
    painter.restore()


def draw_stack(painter, x, y, width, height, values, max_size, top_index, highlighted_index=None):
    """绘制栈
    
    Args:
        painter: QPainter对象
        x: 左上角x坐标
        y: 左上角y坐标
        width: 宽度
        height: 高度
        values: 栈中的值列表
        max_size: 栈的最大容量
        top_index: 栈顶索引
        highlighted_index: 高亮索引
    """
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 计算单元格高度
    cell_height = min(height / max_size, 40)
    
    # 绘制栈边框
    painter.setPen(QPen(NODE_BORDER_COLOR, LINE_WIDTH))
    painter.setBrush(Qt.NoBrush)
    painter.drawRect(QRectF(x, y, width, height))
    
    # 绘制栈底和栈顶标签
    font = QFont()
    font.setPointSize(LABEL_FONT_SIZE)
    painter.setFont(font)
    painter.setPen(QPen(TEXT_COLOR))
    
    # 栈底标签
    bottom_label_rect = QRectF(x, y + height + 5, width, LABEL_FONT_SIZE + 4)
    painter.drawText(bottom_label_rect, Qt.AlignCenter, "栈底")
    
    # 栈顶标签
    top_y = y + height - (top_index + 1) * cell_height
    if top_index >= 0:
        top_label_rect = QRectF(x + width + 5, top_y, 40, cell_height)
        painter.drawText(top_label_rect, Qt.AlignVCenter | Qt.AlignLeft, "栈顶")
    
    # 绘制栈元素
    for i in range(len(values)):
        cell_y = y + height - (i + 1) * cell_height
        is_highlighted = (i == highlighted_index)
        
        # 设置单元格颜色
        if is_highlighted:
            painter.setBrush(QBrush(HIGHLIGHT_COLOR))
            painter.setPen(QPen(QColor(HIGHLIGHT_COLOR.darker(150)), LINE_WIDTH))
        else:
            painter.setBrush(QBrush(NODE_COLOR))
            painter.setPen(QPen(NODE_BORDER_COLOR, LINE_WIDTH))
        
        # 绘制单元格
        painter.drawRect(QRectF(x, cell_y, width, cell_height))
        
        # 绘制值
        painter.setPen(QPen(TEXT_COLOR))
        font = QFont()
        font.setPointSize(TEXT_FONT_SIZE)
        painter.setFont(font)
        value_rect = QRectF(x, cell_y, width, cell_height)
        painter.drawText(value_rect, Qt.AlignCenter, str(values[i]))
    
    # 恢复画笔状态
    painter.restore()


def calculate_tree_layout(tree_data, node_spacing=80, level_spacing=100):
    """计算树的布局
    
    Args:
        tree_data: 树数据，格式为 {"nodes": [...], "edges": [...]}
        node_spacing: 同一层节点之间的间距
        level_spacing: 层与层之间的间距
    
    Returns:
        包含节点位置的字典 {node_id: (x, y)}
    """
    if not tree_data or "nodes" not in tree_data or not tree_data["nodes"]:
        return {}
    
    # 构建节点字典和子节点关系
    nodes = {node["id"]: node for node in tree_data["nodes"]}
    children = {node_id: [] for node_id in nodes}
    
    # 找出根节点和构建子节点关系
    root_id = None
    for edge in tree_data.get("edges", []):
        parent_id, child_id = edge["source"], edge["target"]
        children[parent_id].append(child_id)
        
    # 找出根节点（没有父节点的节点）
    parent_nodes = set(edge["source"] for edge in tree_data.get("edges", []))
    child_nodes = set(edge["target"] for edge in tree_data.get("edges", []))
    root_candidates = set(nodes.keys()) - child_nodes
    
    if root_candidates:
        root_id = list(root_candidates)[0]
    else:
        # 如果没有明确的根节点，使用第一个节点
        root_id = list(nodes.keys())[0] if nodes else None
    
    if root_id is None:
        return {}
    
    # 计算每个节点的位置
    positions = {}
    
    def calculate_subtree_width(node_id):
        """计算子树宽度"""
        if not children[node_id]:
            return node_spacing
        
        return sum(calculate_subtree_width(child_id) for child_id in children[node_id])
    
    def assign_positions(node_id, x, y, level_width):
        """分配节点位置"""
        positions[node_id] = (x, y)
        
        if not children[node_id]:
            return
        
        # 计算子节点的位置
        child_count = len(children[node_id])
        total_width = sum(calculate_subtree_width(child_id) for child_id in children[node_id])
        
        # 调整起始位置，使子树居中
        start_x = x - total_width / 2 + node_spacing / 2
        
        for child_id in children[node_id]:
            child_width = calculate_subtree_width(child_id)
            child_x = start_x + child_width / 2
            child_y = y + level_spacing
            
            assign_positions(child_id, child_x, child_y, child_width)
            start_x += child_width
    
    # 从根节点开始计算位置
    root_width = calculate_subtree_width(root_id)
    assign_positions(root_id, 0, 0, root_width)
    
    return positions


def draw_tree(painter, tree_data, highlighted_nodes=None, highlighted_edges=None):
    """绘制树
    
    Args:
        painter: QPainter对象
        tree_data: 树数据，格式为 {"nodes": [...], "edges": [...]}
        highlighted_nodes: 高亮节点ID列表
        highlighted_edges: 高亮边列表，格式为 [(source_id, target_id), ...]
    """
    if not tree_data or "nodes" not in tree_data or not tree_data["nodes"]:
        return
    
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 计算树的布局
    positions = calculate_tree_layout(tree_data)
    
    # 找出位置的范围
    min_x = min(x for x, _ in positions.values()) if positions else 0
    max_x = max(x for x, _ in positions.values()) if positions else 0
    min_y = min(y for _, y in positions.values()) if positions else 0
    max_y = max(y for _, y in positions.values()) if positions else 0
    
    # 计算缩放和平移，使树居中显示
    width = painter.device().width()
    height = painter.device().height()
    
    # 添加边距
    margin = 50
    scale_x = (width - 2 * margin) / (max_x - min_x + 1) if max_x > min_x else 1
    scale_y = (height - 2 * margin) / (max_y - min_y + 1) if max_y > min_y else 1
    scale = min(scale_x, scale_y)
    
    # 计算居中偏移
    offset_x = (width - scale * (max_x - min_x)) / 2 - scale * min_x
    offset_y = (height - scale * (max_y - min_y)) / 2 - scale * min_y
    
    # 转换位置坐标
    transformed_positions = {}
    for node_id, (x, y) in positions.items():
        transformed_positions[node_id] = (x * scale + offset_x, y * scale + offset_y)
    
    # 先绘制边
    for edge in tree_data.get("edges", []):
        source_id, target_id = edge["source"], edge["target"]
        
        if source_id in transformed_positions and target_id in transformed_positions:
            source_x, source_y = transformed_positions[source_id]
            target_x, target_y = transformed_positions[target_id]
            
            # 检查是否高亮
            is_highlighted = False
            if highlighted_edges:
                is_highlighted = (source_id, target_id) in highlighted_edges
            
            draw_arrow(painter, source_x, source_y, target_x, target_y, is_highlighted)
    
    # 再绘制节点
    for node in tree_data["nodes"]:
        node_id = node["id"]
        if node_id in transformed_positions:
            x, y = transformed_positions[node_id]
            
            # 检查是否高亮
            is_highlighted = False
            if highlighted_nodes:
                is_highlighted = node_id in highlighted_nodes
            
            # 检查是否为空节点
            if node.get("value") == "NULL" or node.get("null", False):
                draw_null_node(painter, x, y)
            else:
                label = node.get("label")
                draw_node(painter, x, y, node["value"], is_highlighted, label)
    
    # 恢复画笔状态
    painter.restore()


def draw_huffman_codes(painter, codes, x, y, width):
    """绘制哈夫曼编码表
    
    Args:
        painter: QPainter对象
        codes: 哈夫曼编码字典 {字符: 编码}
        x: 左上角x坐标
        y: 左上角y坐标
        width: 表格宽度
    """
    if not codes:
        return
    
    # 保存当前画笔状态
    painter.save()
    
    # 设置抗锯齿
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 设置字体和颜色
    font = QFont()
    font.setPointSize(TEXT_FONT_SIZE)
    painter.setFont(font)
    painter.setPen(QPen(TEXT_COLOR))
    
    # 表格标题
    title_rect = QRectF(x, y, width, 30)
    painter.drawText(title_rect, Qt.AlignCenter, "哈夫曼编码表")
    
    # 表格参数
    row_height = 30
    col_width = width / 2
    header_y = y + 30
    
    # 绘制表头
    painter.setPen(QPen(NODE_BORDER_COLOR, LINE_WIDTH))
    painter.drawLine(x, header_y, x + width, header_y)
    painter.drawLine(x, header_y + row_height, x + width, header_y + row_height)
    painter.drawLine(x, header_y, x, header_y + row_height)
    painter.drawLine(x + col_width, header_y, x + col_width, header_y + row_height)
    painter.drawLine(x + width, header_y, x + width, header_y + row_height)
    
    # 绘制表头文本
    painter.setPen(QPen(TEXT_COLOR))
    char_header_rect = QRectF(x, header_y, col_width, row_height)
    code_header_rect = QRectF(x + col_width, header_y, col_width, row_height)
    painter.drawText(char_header_rect, Qt.AlignCenter, "字符")
    painter.drawText(code_header_rect, Qt.AlignCenter, "编码")
    
    # 绘制数据行
    data_y = header_y + row_height
    for i, (char, code) in enumerate(sorted(codes.items())):
        row_y = data_y + i * row_height
        
        # 绘制单元格边框
        painter.setPen(QPen(NODE_BORDER_COLOR, 1))
        painter.drawLine(x, row_y + row_height, x + width, row_y + row_height)
        painter.drawLine(x, row_y, x, row_y + row_height)
        painter.drawLine(x + col_width, row_y, x + col_width, row_y + row_height)
        painter.drawLine(x + width, row_y, x + width, row_y + row_height)
        
        # 绘制单元格文本
        painter.setPen(QPen(TEXT_COLOR))
        char_rect = QRectF(x, row_y, col_width, row_height)
        code_rect = QRectF(x + col_width, row_y, col_width, row_height)
        painter.drawText(char_rect, Qt.AlignCenter, char)
        painter.drawText(code_rect, Qt.AlignCenter, code)
    
    # 恢复画笔状态
    painter.restore()