#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一主题与样式（QSS）
"""

# 应用级样式表（浅色主题）
DEFAULT_BASE_FONT_PX = 13

def _build_qss(base_font_px: int):
    px = max(11, min(22, int(base_font_px or DEFAULT_BASE_FONT_PX)))
    qss = """
/* 全局字体与背景 */
QWidget {
  font-family: "Microsoft YaHei UI", Arial, sans-serif;
  font-size: __BASE_FONT_PX__px;
  background: #f8fafc;
  color: #111827;
}

/* 分组框样式 */
QGroupBox {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-top: 12px;
  padding: 8px;
}
QGroupBox::title {
  subcontrol-origin: margin;
  left: 10px;
  padding: 0 4px;
  background: transparent;
}

/* 按钮样式 */
QPushButton {
  background: #2f80ed;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
}
QPushButton:hover { background: #1366d6; }
QPushButton:disabled { background: #9aa5b1; color: #ffffff; }

/* 下拉框样式 */
QComboBox {
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 4px 8px;
}
QComboBox QAbstractItemView {
  background: #ffffff;
  color: #000000;                  /* 默认黑字 */
  selection-background-color: #2f80ed; /* 选中蓝底 */
  selection-color: #000000;        /* 选中黑字 */
}
QComboBox QAbstractItemView::item { color: #000000; }
QComboBox QAbstractItemView::item:hover {
  background: #2f80ed; /* 蓝底 */
  color: #000000;      /* 黑字 */
}
QComboBox QAbstractItemView::item:selected {
  background: #2f80ed; /* 蓝底 */
  color: #000000;      /* 黑字 */
}
/* 兼容部分平台对选择颜色的处理 */
QAbstractItemView::item:hover { color: #000000; }
QAbstractItemView::item:selected { color: #000000; }

/* 针对“数据结构类型”下拉的高优先级规则 */
QComboBox#structureCombo QAbstractItemView {
  background: #ffffff;
  color: #000000;
  selection-background-color: #2f80ed;
  selection-color: #000000;
}
QAbstractItemView#structureComboPopup::item:hover {
  background: #2f80ed;
  color: #000000;
}
QAbstractItemView#structureComboPopup::item:selected {
  background: #2f80ed;
  color: #000000;
}

/* 文本输入与控制台 */
QLineEdit, QPlainTextEdit, QTextEdit {
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 6px;
}
QPlainTextEdit { font-family: Consolas, "Courier New", monospace; }

/* 标签与状态栏 */
QLabel { color: #374151; }
QStatusBar { background: #eef2f7; }

/* 选项卡 */
QTabWidget::pane { border: 1px solid #e5e7eb; border-radius: 8px; }
QTabBar::tab { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 6px 12px; margin: 2px; }
QTabBar::tab:selected { background: #e5f0ff; }
"""
    return qss.replace("__BASE_FONT_PX__", str(px))

def get_app_qss(base_font_px: int = DEFAULT_BASE_FONT_PX):
    """返回应用级样式表字符串，支持基础字体像素大小参数化"""
    return _build_qss(base_font_px)