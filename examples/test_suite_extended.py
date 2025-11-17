#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
扩展测试套件：覆盖正确运行、错误条件、边界数据的用例，并输出结果分析。
该脚本通过 DSLController 驱动 LinearController / TreeController，并使用轻量 MockView 捕获消息与状态。
"""

import sys
import os
import time
from typing import List, Tuple, Dict, Any

# 保证项目根路径可导入
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 轻量视图及控件模拟
class DummyButton:
    def __init__(self):
        self.enabled = False
    def setEnabled(self, flag: bool):
        self.enabled = bool(flag)

class DummyCombo:
    def __init__(self):
        self._items = []
        self._index = 0
    def addItem(self, text, data=None):
        self._items.append((text, data))
    def count(self):
        return len(self._items)
    def itemData(self, i):
        try:
            return self._items[i][1]
        except Exception:
            return None
    def currentIndex(self):
        return self._index
    def setCurrentIndex(self, i):
        self._index = int(i)

class LinearMockView:
    def __init__(self):
        self.messages: List[Tuple[str, str]] = []
        self.results: List[Tuple[str, Dict[str, Any]]] = []
        self.animations: List[Dict[str, Any]] = []
        self.structure_combo = DummyCombo()  # 提供占位下拉
        self.insert_button = DummyButton()
    def show_message(self, title, msg):
        self.messages.append((str(title), str(msg)))
        print(f"[LinearView:{title}] {msg}")
    def show_result(self, title, payload):
        self.results.append((str(title), payload))
        print(f"[LinearView:{title}] {payload}")
    def update_view(self, structure):
        print(f"[LinearView] update_view structure={structure}")
    def update_visualization(self, data, structure_type=None):
        print(f"[LinearView] visualization: type={structure_type}, data={data}")
    def update_visualization_with_animation(self, before_state, after_state, action, **kwargs):
        self.animations.append({
            'action': action,
            'before': before_state,
            'after': after_state,
            'kwargs': kwargs
        })
        print(f"[LinearView] anim action={action}, before={before_state}, after={after_state}, extra={kwargs}")

class TreeMockView:
    def __init__(self):
        self.messages: List[Tuple[str, str]] = []
        self.animations: List[Dict[str, Any]] = []
        self.structure_combo = DummyCombo()
        self.insert_button = DummyButton()
    def show_message(self, title, msg):
        self.messages.append((str(title), str(msg)))
        print(f"[TreeView:{title}] {msg}")
    def update_view(self, structure):
        print(f"[TreeView] update_view structure={structure}")
    def update_visualization(self, data, structure_type=None):
        print(f"[TreeView] visualization: type={structure_type}, data={data}")
    def update_visualization_with_animation(self, before_state, after_state, action, value=None, **kwargs):
        self.animations.append({
            'action': action,
            'before': before_state,
            'after': after_state,
            'value': value,
            'kwargs': kwargs
        })
        print(f"[TreeView] anim action={action}, before={before_state}, after={after_state}, value={value}, extra={kwargs}")
    def show_bst_build_animation(self, steps):
        print(f"[TreeView] BST build steps={len(steps)}")
    def show_avl_build_animation(self, steps, inserted_value=None):
        print(f"[TreeView] AVL build steps={len(steps)}, inserted={inserted_value}")
    def show_avl_delete_animation(self, steps, deleted_value=None):
        print(f"[TreeView] AVL delete steps={len(steps)}, deleted={deleted_value}")
    def highlight_traversal_path(self, result, traverse_type):
        print(f"[TreeView] traverse {traverse_type}: {result}")
    def highlight_search_path(self, path, found, search_value=None):
        print(f"[TreeView] search path={path}, found={found}, value={search_value}")
    def highlight_bst_insert_path(self, path, value):
        print(f"[TreeView] bst insert path={path}, value={value}")
    def highlight_bst_delete_path(self, path, value):
        print(f"[TreeView] bst delete path={path}, value={value}")

# 控制器
from controllers.linear_controller import LinearController
from controllers.tree_controller import TreeController
from controllers.dsl_controller import DSLController


class TestRunner:
    def __init__(self):
        self.linear_view = LinearMockView()
        self.tree_view = TreeMockView()
        self.linear_ctrl = LinearController(self.linear_view)
        self.tree_ctrl = TreeController(self.tree_view)
        self.dsl = DSLController(self.linear_ctrl, self.tree_ctrl)
        self.cases: List[Dict[str, Any]] = []

    # 状态辅助
    def _linear_elements(self) -> List[Any]:
        data = self.linear_ctrl.get_structure_data()
        if not data:
            return []
        return list(data.get('elements', []))
    def _tree_state(self) -> Dict[str, Any]:
        t = self.tree_ctrl.current_tree
        stype = self.tree_ctrl.structure_type
        if t is None:
            return {'type': stype, 'nodes': []}
        try:
            if stype == 'binary_tree':
                return {'type': stype, 'nodes': list(t.levelorder_traversal())}
            elif stype == 'bst':
                return {'type': stype, 'nodes': list(t.inorder_traversal())}
            elif stype == 'avl_tree':
                return {'type': stype, 'nodes': list(t.inorder_traversal())}
            elif stype == 'huffman_tree':
                return {'type': stype, 'nodes': []}
        except Exception:
            return {'type': stype, 'nodes': []}
        return {'type': stype, 'nodes': []}

    def _clear_logs(self):
        self.linear_view.messages.clear()
        self.linear_view.results.clear()
        self.linear_view.animations.clear()
        self.tree_view.messages.clear()
        self.tree_view.animations.clear()

    def run_cmd(self, cmd: str, context: str = None) -> bool:
        if context:
            self.dsl.set_context_target(context)
        ok = False
        try:
            ok = self.dsl.process_command(cmd)
        except Exception as e:
            print(f"[Runner] Exception running '{cmd}': {e}")
            ok = False
        return ok

    def record_case(self, name: str, passed: bool, details: Dict[str, Any]):
        self.cases.append({'name': name, 'passed': bool(passed), 'details': details})
        status = 'PASS' if passed else 'FAIL'
        print(f"\n[Case:{status}] {name}")
        if details:
            print(f"  details: {details}")


def run_correct_cases(r: TestRunner):
    # Linear - ArrayList 基本操作
    r._clear_logs()
    r.run_cmd("create arraylist with 1,2,3 size 3", context='linear')
    r.run_cmd("insert 4 at 2 in arraylist", context='linear')
    r.run_cmd("get at 2 from arraylist", context='linear')
    r.run_cmd("delete at 1 from arraylist", context='linear')
    elems = r._linear_elements()
    r.record_case("Linear-ArrayList basic ops", elems == [1,4,3], {
        'final_elements': elems,
        'messages': list(r.linear_view.messages)
    })

    # Linear - LinkedList 基本操作
    r._clear_logs()
    r.run_cmd("create linkedlist with 5,6", context='linear')
    r.run_cmd("insert 7 at 1 in linkedlist", context='linear')
    r.run_cmd("get at 1 from linkedlist", context='linear')
    r.run_cmd("delete at 0 from linkedlist", context='linear')
    elems = r._linear_elements()
    r.record_case("Linear-LinkedList basic ops", elems == [7,6], {
        'final_elements': elems,
        'messages': list(r.linear_view.messages)
    })

    # Linear - Stack 基本操作
    r._clear_logs()
    r.run_cmd("create stack", context='linear')
    r.run_cmd("push 10 to stack", context='linear')
    r.run_cmd("push 20 to stack", context='linear')
    r.run_cmd("peek stack", context='linear')
    r.run_cmd("pop from stack", context='linear')
    elems = r._linear_elements()
    r.record_case("Linear-Stack basic ops", elems == [10], {
        'final_elements': elems,
        'messages': list(r.linear_view.messages)
    })

    # Tree - BinaryTree 构建与遍历
    r._clear_logs()
    r.run_cmd("create binarytree", context='tree')
    r.run_cmd("insert 1 in binarytree", context='tree')
    # 先左后右，保证 levelorder 为 [1,2,3]
    r.run_cmd("insert 2 at 0 in binarytree", context='tree')
    r.run_cmd("insert 3 at 1 in binarytree", context='tree')
    r.run_cmd("traverse levelorder", context='tree')
    state = r._tree_state()
    r.record_case("Tree-BinaryTree build/traverse", state.get('nodes') == [1,2,3], {
        'final_nodes': state.get('nodes'),
        'messages': list(r.tree_view.messages)
    })

    # Tree - BST 构建、搜索、删除、遍历
    r._clear_logs()
    r.run_cmd("build bst with 50,30,70,20,40,60,80", context='tree')
    time.sleep(0.8)
    r.run_cmd("search 40 in bst", context='tree')
    time.sleep(0.3)
    r.run_cmd("delete 30 from bst", context='tree')
    time.sleep(0.8)
    r.run_cmd("traverse inorder", context='tree')
    time.sleep(0.3)
    state = r._tree_state()
    # inorder 升序且删除30后仍有六个元素
    passed = state.get('nodes') == sorted(state.get('nodes')) and 50 in state.get('nodes') and 30 not in state.get('nodes')
    r.record_case("Tree-BST build/search/delete/traverse", passed, {
        'final_nodes': state.get('nodes'),
        'messages': list(r.tree_view.messages)
    })

    # Tree - AVL 构建与遍历
    r._clear_logs()
    r.run_cmd("build avl with 10,20,30,40,50,25", context='tree')
    time.sleep(0.8)
    r.run_cmd("traverse preorder", context='tree')
    time.sleep(0.3)
    state = r._tree_state()
    passed = set(state.get('nodes')) >= {10,20,25,30,40,50}
    r.record_case("Tree-AVL build/traverse", passed, {
        'final_nodes_inorder': state.get('nodes'),
        'messages': list(r.tree_view.messages)
    })

    # Tree - Huffman 编解码
    r._clear_logs()
    r.run_cmd("build huffman with a:10,b:5,c:3", context='tree')
    # 先编码，再解码回原文
    ok_enc = r.run_cmd("encode \"abac\" using huffman", context='tree')
    # 直接读取模型进行 encode/decode 以断言正确性
    encoded = r.tree_ctrl.current_tree.encode("abac")
    decoded = r.tree_ctrl.current_tree.decode(encoded)
    r.record_case("Tree-Huffman encode/decode", ok_enc and decoded == "abac", {
        'encoded': encoded,
        'decoded': decoded,
        'messages': list(r.tree_view.messages)
    })


def run_error_cases(r: TestRunner):
    # Linear - 越界/非法操作
    r._clear_logs()
    r.run_cmd("create arraylist with 1,2,3 size 3", context='linear')
    r.run_cmd("insert 100 at 999 in arraylist", context='linear')
    msgs = [m for m in r.linear_view.messages if m[0] == '错误']
    r.record_case("Error-Linear insert out-of-bounds", len(msgs) >= 1, {'errors': msgs})

    r._clear_logs()
    r.run_cmd("create arraylist with 1,2,3", context='linear')
    # 负数索引：语法不支持，会解析失败（DSLController 返回 False）
    ok = r.run_cmd("get at -1 from arraylist", context='linear')
    r.record_case("Error-Linear get negative index (parse error)", ok is False, {
        'messages': list(r.linear_view.messages)
    })

    r._clear_logs()
    r.run_cmd("create linkedlist with 1,2", context='linear')
    r.run_cmd("delete at 10 from linkedlist", context='linear')
    msgs = [m for m in r.linear_view.messages if m[0] == '错误']
    r.record_case("Error-Linear delete out-of-bounds", len(msgs) >= 1, {'errors': msgs})

    r._clear_logs()
    r.run_cmd("create stack", context='linear')
    r.run_cmd("pop from stack", context='linear')
    msgs = [m for m in r.linear_view.messages if m[0] == '错误']
    r.record_case("Error-Linear pop empty stack", len(msgs) >= 1, {'errors': msgs})

    r._clear_logs()
    r.run_cmd("create stack", context='linear')
    r.run_cmd("peek stack", context='linear')
    r.run_cmd("pop from stack", context='linear')
    r.run_cmd("pop from stack", context='linear')  # 再次出栈应报错
    msgs = [m for m in r.linear_view.messages if m[0] == '错误']
    r.record_case("Error-Linear peek/pop flows", len(msgs) >= 1, {'errors': msgs})

    # Linear - 未知命令/结构
    r._clear_logs()
    ok = r.run_cmd("create queue", context='linear')
    r.record_case("Error-Linear unknown structure (parse error)", ok is False, {'messages': list(r.linear_view.messages)})

    # Tree - BinaryTree 路径错误/删除缺少路径/遍历类型错误
    r._clear_logs()
    r.run_cmd("create binarytree", context='tree')
    r.run_cmd("insert 1 in binarytree", context='tree')
    r.run_cmd("insert 5 at 2 in binarytree", context='tree')  # 非0/1路径应报错
    msgs = [m for m in r.tree_view.messages if m[0] == '错误']
    r.record_case("Error-Tree binary insert invalid path", len(msgs) >= 1, {'errors': msgs})

    r._clear_logs()
    r.run_cmd("create binarytree", context='tree')
    r.run_cmd("insert 1 in binarytree", context='tree')
    r.run_cmd("delete 1 from binarytree", context='tree')  # 未提供路径
    msgs = [m for m in r.tree_view.messages if m[0] == '错误' and '路径' in m[1]]
    r.record_case("Error-Tree binary delete without path", len(msgs) >= 1, {'errors': msgs})

    r._clear_logs()
    ok = r.run_cmd("traverse unknown", context='tree')
    r.record_case("Error-Tree traverse type invalid (parse error)", ok is False, {'messages': list(r.tree_view.messages)})

    # Tree - Huffman 编码未覆盖字符 / 非法解码串
    r._clear_logs()
    r.run_cmd("build huffman with a:5,b:3", context='tree')
    ok = r.run_cmd("encode \"ax\" using huffman", context='tree')  # x 不在频率表内，应报错
    msgs = [m for m in r.tree_view.messages if m[0] == '错误']
    r.record_case("Error-Tree huffman encode unknown char", (ok is False) or (len(msgs) >= 1), {'errors': msgs, 'ok': ok})

    r._clear_logs()
    ok = r.run_cmd("decode 010201 using huffman", context='tree')  # 解析阶段报错
    r.record_case("Error-Tree huffman decode invalid binary (parse error)", ok is False, {'messages': list(r.tree_view.messages)})

    # Tree - 未创建直接搜索
    r._clear_logs()
    ok = r.run_cmd("search 999 in bst", context='tree')
    msgs = [m for m in r.tree_view.messages if m[0] == '错误']
    r.record_case("Error-Tree search before create", ok is False or len(msgs) >= 1, {'errors': msgs})

    # Global - 清空所有结构
    r._clear_logs()
    ok = r.run_cmd("clear", context=None)
    r.record_case("Global clear all", ok is True, {'messages': list(r.tree_view.messages) + list(r.linear_view.messages)})


def run_boundary_cases(r: TestRunner):
    # Linear - ArrayList 扩容、首/尾插入
    r._clear_logs()
    r.run_cmd("create arraylist with 1,2,3 size 3", context='linear')
    r.run_cmd("insert 4 at 3 in arraylist", context='linear')  # 触发扩容或追加
    r.run_cmd("insert 0 at 0 in arraylist", context='linear')  # 首插
    elems = r._linear_elements()
    r.record_case("Boundary-Linear arraylist grow+edge insert", elems == [0,1,2,3,4], {'final_elements': elems})

    # Linear - LinkedList 尾插
    r._clear_logs()
    r.run_cmd("create linkedlist with 1,2", context='linear')
    r.run_cmd("insert 3 at 2 in linkedlist", context='linear')
    elems = r._linear_elements()
    r.record_case("Boundary-Linear linkedlist tail insert", elems == [1,2,3], {'final_elements': elems})

    # Linear - Stack 多次入栈触发扩容
    r._clear_logs()
    r.run_cmd("create stack", context='linear')
    for i in range(15):
        r.run_cmd(f"push {i} to stack", context='linear')
    elems = r._linear_elements()
    r.record_case("Boundary-Linear stack growth", len(elems) == 15 and elems[-1] == 14, {'size': len(elems)})

    # Tree - BinaryTree 深路径插入
    r._clear_logs()
    r.run_cmd("create binarytree", context='tree')
    r.run_cmd("insert 1 in binarytree", context='tree')
    # 逐步创建路径，确保每一步路径存在
    r.run_cmd("insert 2 at 0 in binarytree", context='tree')
    r.run_cmd("insert 3 at 0,0 in binarytree", context='tree')
    state = r._tree_state()
    r.record_case("Boundary-Tree binary deep path", len(state.get('nodes')) >= 3, {'final_nodes': state.get('nodes')})

    # Tree - AVL 四种旋转插入序列（仅验证包含性）
    r._clear_logs()
    r.run_cmd("create avl", context='tree')
    for v in [30,20,10]:  # LL
        r.run_cmd(f"insert {v} in avl", context='tree')
        time.sleep(0.2)
    r.run_cmd("clear avl", context='tree')
    time.sleep(0.3)
    r.run_cmd("create avl", context='tree')
    for v in [10,20,30]:  # RR
        r.run_cmd(f"insert {v} in avl", context='tree')
        time.sleep(0.2)
    r.run_cmd("clear avl", context='tree')
    time.sleep(0.3)
    r.run_cmd("create avl", context='tree')
    for v in [30,10,20]:  # LR
        r.run_cmd(f"insert {v} in avl", context='tree')
        time.sleep(0.2)
    r.run_cmd("clear avl", context='tree')
    time.sleep(0.3)
    r.run_cmd("create avl", context='tree')
    for v in [10,30,20]:  # RL
        r.run_cmd(f"insert {v} in avl", context='tree')
        time.sleep(0.2)
    state = r._tree_state()
    r.record_case("Boundary-Tree avl rotations", set(state.get('nodes')) >= {10,20,30}, {'final_nodes_inorder': state.get('nodes')})

    # Tree - BST 大数据构建
    r._clear_logs()
    seq = ",".join(str(i) for i in range(1, 101))
    r.run_cmd(f"build bst with {seq}", context='tree')
    time.sleep(1.5)
    r.run_cmd("traverse inorder", context='tree')
    time.sleep(0.5)
    state = r._tree_state()
    r.record_case("Boundary-Tree bst large build", len(state.get('nodes')) == 100, {'size': len(state.get('nodes'))})

    # Tree - Huffman 单字符频率与重复字符编码
    r._clear_logs()
    r.run_cmd("build huffman with a:10", context='tree')
    enc = r.tree_ctrl.current_tree.encode("aaaaaa")
    dec = r.tree_ctrl.current_tree.decode(enc)
    r.record_case("Boundary-Tree huffman single-char", dec == "aaaaaa", {'encoded': enc, 'decoded': dec})


def main():
    runner = TestRunner()
    print("\n===== 正确运行用例 =====")
    run_correct_cases(runner)
    print("\n===== 错误条件用例 =====")
    run_error_cases(runner)
    print("\n===== 边界数据用例 =====")
    run_boundary_cases(runner)

    # 汇总与分析
    total = len(runner.cases)
    passed = sum(1 for c in runner.cases if c['passed'])
    failed = total - passed
    print("\n===== 测试结果汇总 =====")
    print(f"总用例: {total}, 通过: {passed}, 失败: {failed}")

    # 简要分析（按类别）
    cats = {
        'correct': [c for c in runner.cases if c['name'].startswith('Linear') or c['name'].startswith('Tree-Huffman') or c['name'].startswith('Tree-BinaryTree') or c['name'].startswith('Tree-BST') or c['name'].startswith('Tree-AVL')],
        'error': [c for c in runner.cases if c['name'].startswith('Error') or c['name'].startswith('Global')],
        'boundary': [c for c in runner.cases if c['name'].startswith('Boundary')]
    }
    for k, arr in cats.items():
        p = sum(1 for c in arr if c['passed'])
        t = len(arr)
        print(f"类别 {k}: {p}/{t} 通过")

    # 如需更详细分析，可根据 runner.cases 输出具体失败详情
    failed_details = [c for c in runner.cases if not c['passed']]
    if failed_details:
        print("\n失败用例详情：")
        for c in failed_details:
            print(f"- {c['name']}: {c['details']}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())