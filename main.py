#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据结构可视化模拟器 - 主程序入口
"""

import sys
from PyQt5.QtWidgets import QApplication
from controllers.app_controller import AppController


def main():
    """程序入口函数"""
    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建应用控制器
    controller = AppController()
    
    # 显示主窗口
    controller.show_main_window()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()