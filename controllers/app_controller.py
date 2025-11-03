#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用控制器 - 负责协调模型和视图之间的交互
"""

import json
import pickle
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from views.main_window import MainWindow
from utils.dsl_parser import parse_dsl_command
from controllers.linear_controller import LinearController
from controllers.tree_controller import TreeController
from controllers.dsl_controller import DSLController
from controllers.nl_controller import NLController


class AppController:
    """应用控制器类，负责协调整个应用程序的运行"""
    
    def __init__(self):
        """初始化应用控制器"""
        # 创建主窗口
        self.main_window = MainWindow()
        
        # 创建子控制器
        self.linear_controller = LinearController(self.main_window.linear_view)
        self.tree_controller = TreeController(self.main_window.tree_view)
        self.dsl_controller = DSLController(self.linear_controller, self.tree_controller)
        self.nl_controller = NLController(self.dsl_controller)
        
        # 连接信号和槽
        self._connect_signals()
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接主窗口的信号到控制器的槽函数
        self.main_window.linear_action_triggered.connect(self._handle_linear_action)
        self.main_window.tree_action_triggered.connect(self._handle_tree_action)
        
        # 连接视图级 DSL 命令信号
        self.main_window.linear_view.dsl_command_triggered.connect(self._handle_dsl_command)
        self.main_window.tree_view.dsl_command_triggered.connect(self._handle_dsl_command)
        
        # 连接保存和加载信号
        self.main_window.save_structure_requested.connect(self.save_structure)
        self.main_window.load_structure_requested.connect(self.load_structure)
        
        # 连接DSL控制器的信号
        self.dsl_controller.command_result.connect(self._handle_dsl_result)
    
    def _handle_linear_action(self, action_type, params):
        """处理线性结构操作"""
        # 切换到线性结构标签页
        try:
            self.main_window.tab_widget.setCurrentIndex(0)
        except Exception:
            pass
        self.linear_controller.handle_action(action_type, params)

    def _handle_tree_action(self, action_type, params):
        """处理树形结构操作"""
        # 切换到树形结构标签页
        try:
            self.main_window.tab_widget.setCurrentIndex(1)
        except Exception:
            pass
        self.tree_controller.handle_action(action_type, params)
    
    def _handle_dsl_command(self, command):
        """处理DSL命令"""
        s = (command or '').strip()
        # 新规则：默认自然语言；仅当以 DSL: 前缀开头时作为 DSL 直接执行
        if s.lower().startswith('dsl:'):
            # 去除 DSL: 前缀后按原有 DSL 路径执行
            dsl_text = s.split(':', 1)[1].strip() if ':' in s else ''
            # 预测命令类型并切换到对应标签页，同时设置上下文目标
            predicted = None
            try:
                first = ''
                if ('\n' in dsl_text) or (';' in dsl_text):
                    parts = [x.strip() for x in dsl_text.replace('\n', ';').split(';') if x.strip()]
                    first = parts[0] if parts else ''
                else:
                    first = dsl_text
                if first:
                    _, cmd_type = parse_dsl_command(first)
                    predicted = cmd_type
            except Exception:
                predicted = None
            if predicted == 'linear':
                try:
                    self.main_window.tab_widget.setCurrentIndex(0)
                except Exception:
                    pass
                self.dsl_controller.set_context_target('linear')
            elif predicted == 'tree':
                try:
                    self.main_window.tab_widget.setCurrentIndex(1)
                except Exception:
                    pass
                self.dsl_controller.set_context_target('tree')
            else:
                current_tab = self.main_window.tab_widget.currentIndex()
                self.dsl_controller.set_context_target('linear' if current_tab == 0 else 'tree')

            if ('\n' in dsl_text) or (';' in dsl_text):
                result = self.dsl_controller.process_script(dsl_text)
            else:
                result = self.dsl_controller.process_command(dsl_text)
            if not result:
                # 错误信息已通过信号传递
                return
            return

        # 其余情况均作为自然语言处理（无前缀）
        nl_text = s
        # 根据当前选项卡设置上下文目标，先生成 DSL
        current_tab = self.main_window.tab_widget.currentIndex()
        context_target = 'linear' if current_tab == 0 else 'tree'
        ok, dsl_text = self.nl_controller.handle_nl_command(nl_text, context_target=context_target)
        view = self.main_window.linear_view if context_target == 'linear' else self.main_window.tree_view
        if not ok or not dsl_text:
            view.append_dsl_output('NL→DSL: 无法解析该自然语言，请尝试更明确的表达。')
            return
        # 预览生成的 DSL
        view.append_dsl_output(f'NL→DSL 生成：\n{dsl_text}')
        # 预测命令类型并切换到对应标签页，同时设置上下文目标
        predicted = None
        try:
            first = ''
            if ('\n' in dsl_text) or (';' in dsl_text):
                parts = [x.strip() for x in dsl_text.replace('\n', ';').split(';') if x.strip()]
                first = parts[0] if parts else ''
            else:
                first = dsl_text
            if first:
                _, cmd_type = parse_dsl_command(first)
                predicted = cmd_type
        except Exception:
            predicted = None
        if predicted == 'linear':
            try:
                self.main_window.tab_widget.setCurrentIndex(0)
            except Exception:
                pass
            self.dsl_controller.set_context_target('linear')
        elif predicted == 'tree':
            try:
                self.main_window.tab_widget.setCurrentIndex(1)
            except Exception:
                pass
            self.dsl_controller.set_context_target('tree')
        else:
            current_tab = self.main_window.tab_widget.currentIndex()
            self.dsl_controller.set_context_target('linear' if current_tab == 0 else 'tree')
        # 将生成的 DSL 交由 DSLController 执行
        if ('\n' in dsl_text) or (';' in dsl_text):
            result = self.dsl_controller.process_script(dsl_text)
        else:
            result = self.dsl_controller.process_command(dsl_text)
        if not result:
            # 错误信息已通过信号传递
            return
        return

        # 旧路径不再使用：这里的逻辑由上面的 DSL: 分支与 NL 分支覆盖
        return
    
    def _handle_dsl_result(self, result_type, result_data):
        """处理DSL命令结果
        
        Args:
            result_type: 结果类型（success/error）
            result_data: 结果数据，包含 message 和 target 用于路由
        """
        target = result_data.get("target")
        message = result_data.get("message", "")
        # 根据目标类型自动切换标签页
        try:
            if target == "linear":
                self.main_window.tab_widget.setCurrentIndex(0)
            elif target == "tree":
                self.main_window.tab_widget.setCurrentIndex(1)
        except Exception:
            pass
        # 根据目标类型选择视图，默认路由到当前选项卡
        if target == "linear":
            view = self.main_window.linear_view
        elif target == "tree":
            view = self.main_window.tree_view
        else:
            current_tab = self.main_window.tab_widget.currentIndex()
            view = self.main_window.linear_view if current_tab == 0 else self.main_window.tree_view
        
        if result_type == "error":
            if message:
                view.append_dsl_output(f"错误: {message}")
            QMessageBox.warning(self.main_window, "DSL错误", message or "未知错误")
        else:
            if message:
                view.append_dsl_output(f"成功: {message}")
    
    def show_main_window(self):
        """显示主窗口（最大化）"""
        # 改为最大化显示（保留标题栏与边框）
        self.main_window.showMaximized()
        
    def save_structure(self):
        """保存当前数据结构到文件"""
        # 获取当前选项卡索引
        current_tab = self.main_window.tab_widget.currentIndex()
        
        # 准备要保存的数据
        data = {
            'tab_index': current_tab,
            'data': None
        }
        
        # 根据当前选项卡获取相应的数据
        if current_tab == 0:  # 线性结构
            structure_type = self.linear_controller.structure_type
            structure_data = self.linear_controller.get_structure_data()
            data['data'] = {
                'type': structure_type,
                'content': structure_data
            }
        elif current_tab == 1:  # 树形结构
            structure_type = self.tree_controller.structure_type
            structure_data = self.tree_controller.get_structure_data()
            data['data'] = {
                'type': structure_type,
                'content': structure_data
            }
        
        # 如果没有数据可保存
        if not data['data']:
            QMessageBox.warning(self.main_window, "保存失败", "当前没有可保存的数据结构")
            return
        
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "保存数据结构",
            "",
            "数据结构文件 (*.dsv);;所有文件 (*)"
        )
        
        if not file_path:
            return  # 用户取消了保存
        
        # 确保文件扩展名为.dsv
        if not file_path.endswith('.dsv'):
            file_path += '.dsv'
        
        try:
            # 保存数据到文件
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            
            QMessageBox.information(self.main_window, "保存成功", f"数据结构已保存到: {file_path}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "保存失败", f"保存数据时出错: {str(e)}")
    
    def load_structure(self):
        """从文件加载数据结构"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self.main_window,
            "加载数据结构",
            "",
            "数据结构文件 (*.dsv);;所有文件 (*)"
        )
        
        if not file_path:
            return  # 用户取消了加载
        
        try:
            # 从文件加载数据
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 切换到相应的选项卡
            tab_index = data.get('tab_index', 0)
            self.main_window.tab_widget.setCurrentIndex(tab_index)
            
            # 加载数据到相应的结构
            structure_data = data.get('data')
            if not structure_data:
                raise ValueError("文件中没有有效的数据结构")
            
            structure_type = structure_data.get('type')
            content = structure_data.get('content')
            
            if tab_index == 0:  # 线性结构
                # 先切到对应的线性结构页面（静默切换下拉选项）
                try:
                    if hasattr(self.main_window, 'linear_view') and hasattr(self.main_window.linear_view, 'set_structure_selection'):
                        self.main_window.linear_view.set_structure_selection(structure_type)
                except Exception:
                    pass
                # 设置当前结构类型并加载
                self.linear_controller.structure_type = structure_type
                self.linear_controller.load_structure(structure_type, content)
            elif tab_index == 1:  # 树形结构
                # 先切到对应的树形结构页面（静默切换下拉选项）
                try:
                    if hasattr(self.main_window, 'tree_view') and hasattr(self.main_window.tree_view, 'set_structure_selection'):
                        self.main_window.tree_view.set_structure_selection(structure_type)
                except Exception:
                    pass
                # 设置当前结构类型并加载
                self.tree_controller.structure_type = structure_type
                self.tree_controller.load_structure(structure_type, content)
            
            QMessageBox.information(self.main_window, "加载成功", f"数据结构已从文件加载: {file_path}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "加载失败", f"加载数据时出错: {str(e)}")
from services.operation_recorder import OperationRecorder

# --- Operation recording wrappers: record DSL and button actions ---
try:
    # Wrap DSL command handler to record successful executions
    if not getattr(AppController, "_oprec_wrapped", False):
        _orig_dsl = getattr(AppController, "_handle_dsl_command", None)
        _orig_lin = getattr(AppController, "_handle_linear_action", None)
        _orig_tree = getattr(AppController, "_handle_tree_action", None)

        def _wrap_dsl(self, dsl_text: str):
            ctx = getattr(self, "context_target", None)
            try:
                res = _orig_dsl(self, dsl_text)
                # We cannot know success from return; conservatively record on invocation.
                text = (dsl_text or "").strip()
                if text:
                    is_script = "\n" in text or ";" in text
                    if is_script:
                        parts = [p.strip() for p in text.replace("\n", ";").split(";")]
                        for cmd in parts:
                            if not cmd:
                                continue
                            cmd_low = cmd.lower()
                            rec_ctx = "global" if cmd_low == "clear" else (ctx if ctx in ("linear", "tree") else None)
                            OperationRecorder.record_dsl(cmd, rec_ctx or "linear", success=True, source="dsl")
                    else:
                        cmd_low = text.lower()
                        rec_ctx = "global" if cmd_low == "clear" else (ctx if ctx in ("linear", "tree") else None)
                        OperationRecorder.record_dsl(text, rec_ctx or "linear", success=True, source="dsl")
                return res
            except Exception:
                # In case of handler error, still attempt to record the raw text
                text = (dsl_text or "").strip()
                if text:
                    rec_ctx = ctx if ctx in ("linear", "tree") else None
                    OperationRecorder.record_dsl(text, rec_ctx or "linear", success=False, source="dsl")
                raise

        def _wrap_linear(self, action_type: str, params: dict):
            try:
                res = _orig_lin(self, action_type, params)
                struct_type = getattr(self.linear_controller, "structure_type", None)
                current = getattr(self.linear_controller, "current_structure", None)
                executed = True
                act = (action_type or "").strip().lower()
                if act in ("insert", "delete", "remove", "get", "push", "pop", "peek", "clear") and not current:
                    executed = False
                OperationRecorder.record_linear_action(action_type, params, struct_type, executed=executed)
                return res
            except Exception:
                struct_type = getattr(self.linear_controller, "structure_type", None)
                OperationRecorder.record_linear_action(action_type, params, struct_type, executed=False)
                raise

        def _wrap_tree(self, action_type: str, params: dict):
            try:
                res = _orig_tree(self, action_type, params)
                struct_type = getattr(self.tree_controller, "structure_type", None)
                current = getattr(self.tree_controller, "current_tree", None)
                executed = True
                act = (action_type or "").strip().lower()
                if act in ("insert", "remove", "delete", "search", "find", "traverse", "encode", "decode", "clear") and not current:
                    executed = False
                OperationRecorder.record_tree_action(action_type, params, struct_type, executed=executed)
                return res
            except Exception:
                struct_type = getattr(self.tree_controller, "structure_type", None)
                OperationRecorder.record_tree_action(action_type, params, struct_type, executed=False)
                raise

        if callable(_orig_dsl):
            AppController._handle_dsl_command = _wrap_dsl
        if callable(_orig_lin):
            AppController._handle_linear_action = _wrap_linear
        if callable(_orig_tree):
            AppController._handle_tree_action = _wrap_tree

        AppController._oprec_wrapped = True
except Exception:
    # Non-fatal: recording wrappers are optional
    pass