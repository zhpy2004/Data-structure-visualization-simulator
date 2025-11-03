#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
DSL 语法高亮器：用于在控制台中高亮 DSL 关键字、结构名、数字与字符串。
"""

from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt5.QtCore import Qt, QRegExp


class DSLHighlighter(QSyntaxHighlighter):
    """简单的 DSL 语法高亮器。

    - 高亮命令关键字：create/insert/delete/get/push/pop/peek/clear/search/traverse/build/encode/decode
    - 高亮结构名：arraylist/linkedlist/stack/binarytree/bst/huffman/avl
    - 高亮片段词：with/size/at/in/from/to/using/preorder/inorder/postorder/levelorder
    - 高亮数字与字符串
    - 高亮错误行（包含“错误”或“Error”或“Traceback”）
    """

    def __init__(self, parent_document):
        super().__init__(parent_document)
        self.rules = []

        # 关键字样式
        kw_format = QTextCharFormat()
        kw_format.setForeground(QColor(30, 100, 200))
        kw_format.setFontWeight(QFont.Bold)

        # 结构名样式
        type_format = QTextCharFormat()
        type_format.setForeground(QColor(200, 80, 30))
        type_format.setFontWeight(QFont.DemiBold)

        # 片段词样式
        aux_format = QTextCharFormat()
        aux_format.setForeground(QColor(90, 90, 90))

        # 数字样式
        num_format = QTextCharFormat()
        num_format.setForeground(QColor(120, 0, 160))

        # 字符串样式
        str_format = QTextCharFormat()
        str_format.setForeground(QColor(0, 150, 0))

        # 提示前缀 >>> 样式
        prompt_format = QTextCharFormat()
        prompt_format.setForeground(QColor(120, 120, 120))

        # 错误行样式（通过整行匹配）
        err_format = QTextCharFormat()
        err_format.setForeground(QColor(200, 0, 0))
        err_format.setFontWeight(QFont.Bold)

        # 组装规则
        keywords = [
            'create', 'insert', 'delete', 'get', 'push', 'pop', 'peek', 'clear',
            'search', 'traverse', 'build', 'encode', 'decode'
        ]
        types = ['arraylist', 'linkedlist', 'stack', 'binarytree', 'bst', 'huffman', 'avl']
        aux_words = ['with', 'size', 'at', 'in', 'from', 'to', 'using',
                     'preorder', 'inorder', 'postorder', 'levelorder']

        # 关键字规则
        for w in keywords:
            self.rules.append((QRegExp(rf"\b{w}\b", Qt.CaseInsensitive), kw_format))
        for t in types:
            self.rules.append((QRegExp(rf"\b{t}\b", Qt.CaseInsensitive), type_format))
        for a in aux_words:
            self.rules.append((QRegExp(rf"\b{a}\b", Qt.CaseInsensitive), aux_format))

        # 数字规则
        self.rules.append((QRegExp(r"\b\d+\b"), num_format))
        # 字符串规则（简单匹配双引号内文本）
        self.rules.append((QRegExp(r'"[^"]*"'), str_format))
        # 提示符 >>>
        self.rules.append((QRegExp(r"^>>>"), prompt_format))
        # 错误（整行）
        self.err_regexes = [QRegExp(r"错误"), QRegExp(r"Error"), QRegExp(r"Traceback")]  # 简单包含判断
        self.err_format = err_format

    def highlightBlock(self, text: str):
        # 错误行整行染色
        for rx in self.err_regexes:
            if rx.indexIn(text) != -1:
                self.setFormat(0, len(text), self.err_format)
                return

        # 常规规则
        for rx, fmt in self.rules:
            index = rx.indexIn(text, 0)
            while index >= 0:
                length = rx.matchedLength()
                self.setFormat(index, length, fmt)
                index = rx.indexIn(text, index + length)