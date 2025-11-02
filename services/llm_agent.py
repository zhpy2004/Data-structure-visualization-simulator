#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
LLM Agent (Heuristic Fallback)

方案一：将自然语言（中文/英文）转换为本项目的 DSL 命令或脚本。
当前实现为规则/正则驱动的启发式转换，后续可以在具备 API Key 的环境下接入外部 LLM。

核心入口：LLMAgent.generate_dsl(nl_text, context_target) -> str | None
返回为 DSL 文本（单条或多条，支持用换行或分号分隔），失败返回 None。
"""

import os
import re
import json
from typing import List, Optional, Tuple
import requests


def _normalize_separators(s: str) -> str:
    return s.replace('，', ',').replace('、', ',').replace('；', ';')


def _extract_int_list(text: str) -> List[int]:
    text = _normalize_separators(text)
    nums = re.findall(r"[-+]?\d+", text)
    return [int(n) for n in nums]


def _extract_huffman_pairs(text: str) -> List[Tuple[str, int]]:
    text = _normalize_separators(text)
    pairs = []
    # 支持 a:5,b:2,c:1 或 a: 5
    for m in re.finditer(r"([A-Za-z0-9])\s*:\s*(\d+)", text):
        pairs.append((m.group(1), int(m.group(2))))
    return pairs


def _cn_struct_to_dsl(name: str) -> Optional[str]:
    n = name.lower()
    mapping = {
        '顺序表': 'arraylist', '数组': 'arraylist', '数组表': 'arraylist',
        '链表': 'linkedlist',
        '栈': 'stack',
        '二叉树': 'binarytree', 'binarytree': 'binarytree', 'binary_tree': 'binarytree',
        'bst': 'bst', '二叉搜索树': 'bst', '搜索二叉树': 'bst',
        'avl': 'avl', '平衡二叉树': 'avl', 'avl树': 'avl',
        '哈夫曼': 'huffman', '哈夫曼树': 'huffman'
    }
    return mapping.get(n) or (n if n in ('arraylist','linkedlist','stack','binarytree','bst','avl','huffman') else None)


def _cn_traverse_to_dsl(name: str) -> Optional[str]:
    n = name.lower()
    mapping = {
        '先序': 'preorder', '前序': 'preorder',
        '中序': 'inorder',
        '后序': 'postorder',
        '层序': 'levelorder', '按层': 'levelorder', '广度': 'levelorder',
        'preorder': 'preorder', 'inorder': 'inorder', 'postorder': 'postorder', 'levelorder': 'levelorder'
    }
    return mapping.get(n)


class LLMAgent:
    """启发式 NL→DSL 转换器。后续可接外部 LLM 替换本地规则。"""

    def __init__(self):
        # 外部 LLM 配置（支持环境变量与本地文件 API及URL.txt）
        self.provider = os.environ.get('LLM_PROVIDER')  # openai / openrouter / ollama
        self.api_key = os.environ.get('LLM_API_KEY')
        self.base_url = os.environ.get('LLM_BASE_URL')  # 例如 https://free.v36.cm 或 https://free.v36.cm/v1/
        self.model = os.environ.get('LLM_MODEL', 'gpt-4o-mini')

        # 若未设置环境变量，尝试从项目根目录的 API及URL.txt 读取
        if not (self.api_key and self.base_url):
            url, key = self._load_free_chatgpt_config()
            if url and not self.base_url:
                self.base_url = url
            if key and not self.api_key:
                self.api_key = key
        # 默认提供方按 openai 处理（该免费服务兼容 OpenAI 格式）
        if not self.provider:
            self.provider = 'openai'

    def _load_free_chatgpt_config(self) -> Tuple[Optional[str], Optional[str]]:
        """从项目根的 API及URL.txt 读取 URL 与 API Key。
        文件示例：
            URL: https://free.v36.cm
            API：sk-xxxx
        """
        try:
            root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            cfg_path = os.path.join(root, 'API及URL.txt')
            if not os.path.isfile(cfg_path):
                return None, None
            url = None
            key = None
            with open(cfg_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    line_norm = line.replace('：', ':')
                    if not line:
                        continue
                    if line_norm.startswith('URL:'):
                        url = line_norm.split(':', 1)[1].strip()
                    elif line_norm.startswith('API:'):
                        key = line_norm.split(':', 1)[1].strip()
            return url, key
        except Exception:
            return None, None

    def _normalize_base_url(self, base_url: str) -> str:
        """确保 base_url 以 /v1/ 结尾，满足 OpenAI 兼容接口路径。"""
        if not base_url:
            return 'https://free.v36.cm/v1/'
        u = base_url.strip()
        # 去掉尾部斜杠
        if u.endswith('/'):
            u = u[:-1]
        # 附加 /v1
        if not u.endswith('/v1'):
            u = u + '/v1'
        # 统一添加末尾斜杠
        if not u.endswith('/'):
            u = u + '/'
        return u

    def _call_llm_openai(self, nl_text: str, context_target: Optional[str]) -> Optional[str]:
        """调用兼容 OpenAI 的 Chat Completions 接口（优先使用官方 SDK，失败回退 requests）。"""
        # 仅当有 API Key 时启用
        if not self.api_key:
            print("[LLMAgent] External LLM not configured (missing API key); skipping.")
            return None

        base_url = self._normalize_base_url(self.base_url or 'https://free.v36.cm')
        model = self.model or 'gpt-4o-mini'

        # 基本调用日志（不输出敏感信息）
        try:
            nl_preview = (nl_text or "")[:160].replace("\n", " ")
            print(f"[LLMAgent] Calling external LLM (provider={self.provider or 'openai'}, model={model})")
            print(f"[LLMAgent] Base URL: {base_url}")
            print(f"[LLMAgent] NL preview: {nl_preview}")
        except Exception:
            pass

        system_prompt = (
            "You are a DSL translator for a Data Structure Visualization Simulator.\n"
            "Strict output rules:\n"
            "- Return ONLY valid DSL commands/scripts; no explanations, no comments.\n"
            "- Return plain text only; DO NOT use code blocks.\n"
            "- Keywords and structure names are lowercase.\n"
            "- Values are integers; paths are comma-separated integers; encode text uses double quotes.\n"
            "- Multiple commands may be separated by ';' or newlines.\n"
            "Logical constraints & sequencing:\n"
            "- Always initialize before operations: issue 'create STRUCTURE_TYPE [...]' or 'build ...' FIRST, then 'insert/delete/get/search/traverse/push/pop/peek/encode/decode'.\n"
            "- 'build bst/avl with ...' counts as creation for BST/AVL; subsequent operations must follow after build.\n"
            "- Huffman 'encode'/'decode' requires a built huffman tree; if NL does not provide frequencies or prior build, add 'build huffman ...' before 'encode'/'decode' when frequencies are present. Do NOT invent frequencies.\n"
            "- 'traverse' is valid only for binarytree and requires an existing binarytree (via 'create').\n"
            "- Stack operations ('push/pop/peek') require an existing stack (via 'create stack' if needed).\n"
            "- ArrayList/LinkedList operations ('insert/delete/get') require the list to be created first.\n"
            "- Keep commands type-consistent within one script (linear or tree) unless NL explicitly mixes; for mixed requests, ensure each type is created before its operations.\n"
            "- After 'clear', re-create required structures before further operations.\n"
            "Context:\n"
            "- Target context may be 'linear' (arraylist/linkedlist/stack) or 'tree' (binarytree/bst/avl/huffman). Respect it.\n"
            "Complete DSL reference:\n"
            "Global:\n"
            "- clear\n"
            "Linear (arraylist/linkedlist/stack):\n"
            "- create STRUCTURE_TYPE [with v1,v2,...] [size N]\n"
            "- insert VALUE at POSITION in STRUCTURE_NAME\n"
            "- delete VALUE from STRUCTURE_NAME\n"
            "- delete at POSITION from STRUCTURE_NAME\n"
            "- get VALUE from STRUCTURE_NAME\n"
            "- get at POSITION from STRUCTURE_NAME\n"
            "- push VALUE to stack\n"
            "- pop from stack\n"
            "- peek stack\n"
            "Tree (binarytree/bst/avl/huffman):\n"
            "- create STRUCTURE_TYPE [with v1,v2,...]\n"
            "- traverse TRAVERSE_TYPE [in binarytree]  (TRAVERSE_TYPE ∈ {preorder,inorder,postorder,levelorder}; binarytree only)\n"
            "BinaryTree (level-order construction; path semantics: 0=left,1=right):\n"
            "- insert VALUE [at p1,p2,...] in binarytree\n"
            "- delete VALUE [at p1,p2,...] from binarytree\n"
            "BST:\n"
            "- build bst with v1,v2,...\n"
            "- insert VALUE in bst\n"
            "- delete VALUE from bst\n"
            "- search VALUE in bst\n"
            "AVL:\n"
            "- build avl with v1,v2,...\n"
            "- insert VALUE in avl\n"
            "- delete VALUE from avl\n"
            "- search VALUE in avl\n"
            "Huffman:\n"
            "- build huffman with c1:freq1,c2:freq2,...\n"
            "- encode \"TEXT\" using huffman\n"
            "- decode BINARY using huffman\n"
            "Tree dot-prefix style (supported: create/insert/delete/search/traverse/clear):\n"
            "- tree.binary_tree.create v1,v2,...\n"
            "- tree.binary_tree.insert VALUE at p1,p2\n"
            "- tree.binary_tree.traverse TRAVERSE_TYPE\n"
            "- tree.bst.create v1,v2,...\n"
            "- tree.bst.insert VALUE\n"
            "- tree.bst.search VALUE\n"
            "- tree.bst.delete VALUE\n"
            "Note:\n"
            "- 'build' uses non-prefix writing only (e.g., 'build bst with ...').\n"
            "- 'traverse' is only valid for binarytree.\n"
            "Examples:\n"
            "create arraylist size 10\n"
            "create arraylist with 1,2,3 size 10\n"
            "insert 99 at 2 in arraylist\n"
            "delete at 1 from linkedlist\n"
            "get at 0 from arraylist\n"
            "push 10 to stack; peek stack\n"
            "create binarytree with 1,2,3,4; traverse inorder in binarytree\n"
            "insert 6 at 0,1 in binarytree; delete 6 at 0,1 from binarytree\n"
            "build bst with 10,5,7,3,12,15,18; search 7 in bst\n"
            "build avl with 30,20,40,10,25,50; insert 25 in avl\n"
            "build huffman with a:5,b:2,c:1; encode \"abac\" using huffman\n"
        )
        user_prompt = f"Context={context_target or 'auto'}\nNL: {nl_text}\nReturn DSL only."

        # 优先使用 OpenAI SDK（新版本）
        try:
            print("[LLMAgent] Using OpenAI SDK ...")
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key, base_url=base_url)
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
            )
            dsl = (resp.choices[0].message.content or "").strip()
            try:
                dsl_preview = (dsl.splitlines()[0] if dsl else "")[:160]
                print(f"[LLMAgent] LLM responded via SDK. DSL length={len(dsl)}")
                print(f"[LLMAgent] DSL preview: {dsl_preview}")
            except Exception:
                pass
            return dsl or None
        except Exception as e:
            print(f"[LLMAgent] SDK call failed: {type(e).__name__}: {e}. Falling back to HTTP.")
            # 回退到 HTTP 请求
            try:
                print("[LLMAgent] Calling via HTTP /chat/completions ...")
                url = base_url.rstrip('/') + '/chat/completions'
                headers = {"Authorization": f"Bearer {self.api_key}"}
                body = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "temperature": 0,
                }
                r = requests.post(url, headers=headers, json=body, timeout=30)
                r.raise_for_status()
                data = r.json()
                # OpenAI 兼容响应结构
                dsl = (
                    (data.get("choices") or [{}])[0]
                    .get("message", {})
                    .get("content", "")
                    .strip()
                )
                try:
                    dsl_preview = (dsl.splitlines()[0] if dsl else "")[:160]
                    print(f"[LLMAgent] LLM responded via HTTP. DSL length={len(dsl)}")
                    print(f"[LLMAgent] DSL preview: {dsl_preview}")
                except Exception:
                    pass
                return dsl or None
            except Exception as e2:
                print(f"[LLMAgent] HTTP call failed: {type(e2).__name__}: {e2}.")
                return None

    def generate_dsl(self, nl_text: str, context_target: Optional[str] = None) -> Optional[str]:
        """将自然语言转换为 DSL 脚本。

        Args:
            nl_text: 自然语言文本（中文/英文）
            context_target: 可选的上下文目标 'linear' 或 'tree'，用于约束生成类型

        Returns:
            DSL 文本（单条或多条），失败时返回 None
        """
        text = nl_text.strip()
        if not text:
            return None

        # 统一标点符号
        text = _normalize_separators(text)

        # 若具备外部 LLM 配置，优先尝试调用外部服务生成 DSL
        if (self.provider or '').lower() in ('openai', 'openrouter') or self.base_url or self.api_key:
            print("[LLMAgent] LLM configured; trying external call first.")
            dsl_via_llm = self._call_llm_openai(text, context_target)
            if dsl_via_llm:
                print("[LLMAgent] External LLM produced DSL; skip heuristic.")
                return dsl_via_llm
            else:
                print("[LLMAgent] External LLM returned empty or failed; falling back to heuristic.")

        # 全局清空
        if re.fullmatch(r"清空(全部|所有|工作区)?", text):
            return "clear"

        # 若未指定上下文，先按关键词估计上下文
        if context_target is None:
            lowered = text.lower()
            if any(k in lowered for k in ['二叉树', 'bst', 'avl', '哈夫曼', '遍历', 'huffman']):
                context_target = 'tree'
            else:
                context_target = 'linear'

        if context_target == 'linear':
            dsl = self._linear_nl_to_dsl(text)
            if dsl:
                return dsl
            # 线性失败，尝试树匹配（有些用户未切页）
            dsl = self._tree_nl_to_dsl(text)
            if dsl:
                return dsl
            return None
        else:
            dsl = self._tree_nl_to_dsl(text)
            if dsl:
                return dsl
            # 树失败，尝试线性匹配
            dsl = self._linear_nl_to_dsl(text)
            if dsl:
                return dsl
            return None

    # —— 线性结构：启发式规则 ——
    def _linear_nl_to_dsl(self, text: str) -> Optional[str]:
        # 创建（容量+初始值）
        m = re.search(r"创建\s*(顺序表|链表|栈|arraylist|linkedlist|stack)(?:\s*(?:容量|size)\s*(\d+))?(?:\s*(?:值为|包含|with)\s*([0-9,\s]+))?", text, re.IGNORECASE)
        if m:
            st = _cn_struct_to_dsl(m.group(1) or '')
            cap = m.group(2)
            vals = m.group(3)
            parts = []
            if st:
                parts.append(f"create {st}")
            if vals:
                vs = [str(v) for v in _extract_int_list(vals)]
                if vs:
                    parts.append(f"with {','.join(vs)}")
            if cap:
                parts.append(f"size {cap}")
            return ' '.join(parts) if parts else None

        # 插入：插入 X 在位置 P 到/在 结构
        m = re.search(r"插入\s*(\d+)\s*(?:到|在)?\s*(?:位置)?\s*(\d+)\s*(?:到|在)?\s*(顺序表|链表|arraylist|linkedlist)?", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            pos = int(m.group(2))
            st = _cn_struct_to_dsl(m.group(3) or 'arraylist') or 'arraylist'
            return f"insert {val} at {pos} in {st}"

        # 删除：按位置
        m = re.search(r"删除\s*(?:在)?\s*位置\s*(\d+)\s*从\s*(顺序表|链表|arraylist|linkedlist)", text, re.IGNORECASE)
        if m:
            pos = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'arraylist'
            return f"delete at {pos} from {st}"

        # 删除：按值
        m = re.search(r"删除\s*(\d+)\s*从\s*(顺序表|链表|arraylist|linkedlist)", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'arraylist'
            return f"delete {val} from {st}"

        # 获取：按位置/按值
        m = re.search(r"获取\s*(?:在)?\s*位置\s*(\d+)\s*从\s*(顺序表|链表|arraylist|linkedlist)", text, re.IGNORECASE)
        if m:
            pos = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'arraylist'
            return f"get at {pos} from {st}"
        m = re.search(r"获取\s*(\d+)\s*从\s*(顺序表|链表|arraylist|linkedlist)", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'arraylist'
            return f"get {val} from {st}"

        # 栈：push/pop/peek
        m = re.search(r"(?:入栈|压栈|push)\s*(\d+)", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            return f"push {val} to stack"
        if re.search(r"(?:出栈|弹栈|pop)", text, re.IGNORECASE):
            return "pop from stack"
        if re.search(r"(?:查看栈顶|栈顶|peek)", text, re.IGNORECASE):
            return "peek stack"

        return None

    # —— 树结构：启发式规则 ——
    def _tree_nl_to_dsl(self, text: str) -> Optional[str]:
        # 构建 BST/AVL
        m = re.search(r"(?:构建|建立|build)\s*(BST|二叉搜索树)\s*(?:值为|with)?\s*([0-9,\s]+)", text, re.IGNORECASE)
        if m:
            vals = [str(v) for v in _extract_int_list(m.group(2) or '')]
            return f"build bst with {','.join(vals)}" if vals else None
        m = re.search(r"(?:构建|建立|build)\s*(AVL|平衡二叉树)\s*(?:值为|with)?\s*([0-9,\s]+)", text, re.IGNORECASE)
        if m:
            vals = [str(v) for v in _extract_int_list(m.group(2) or '')]
            return f"build avl with {','.join(vals)}" if vals else None

        # 创建二叉树
        m = re.search(r"创建\s*(二叉树|binarytree)\s*(?:值为|with)?\s*([0-9,\s]+)?", text, re.IGNORECASE)
        if m:
            vals = [str(v) for v in _extract_int_list(m.group(2) or '')]
            return f"create binarytree with {','.join(vals)}" if vals else "create binarytree"

        # 插入/删除（树）：value + in structure + optional path
        m = re.search(r"插入\s*(\d+)\s*(?:到|在)?\s*(BST|AVL|二叉树|binarytree)\s*(?:路径|path)?\s*([0-1,\s]+)?", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'bst'
            path = m.group(3)
            if (st == 'binarytree') and path:
                steps = [s for s in _extract_int_list(path)]
                return f"insert {val} at {','.join(map(str, steps))} in binarytree"
            return f"insert {val} in {st}"

        m = re.search(r"删除\s*(\d+)\s*(?:从|在)?\s*(BST|AVL|二叉树|binarytree)\s*(?:路径|path)?\s*([0-1,\s]+)?", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'bst'
            path = m.group(3)
            if (st == 'binarytree') and path:
                steps = [s for s in _extract_int_list(path)]
                return f"delete {val} at {','.join(map(str, steps))} from binarytree"
            return f"delete {val} from {st}"

        # 搜索
        m = re.search(r"搜索\s*(\d+)\s*在\s*(BST|AVL)", text, re.IGNORECASE)
        if m:
            val = int(m.group(1))
            st = _cn_struct_to_dsl(m.group(2)) or 'bst'
            return f"search {val} in {st}"

        # 遍历（仅二叉树）
        m = re.search(r"(?:遍历|traverse)\s*(先序|前序|中序|后序|层序|preorder|inorder|postorder|levelorder)(?:\s*在\s*(二叉树))?", text, re.IGNORECASE)
        if m:
            tt = _cn_traverse_to_dsl(m.group(1)) or 'preorder'
            return f"traverse {tt} in binarytree"

        # 哈夫曼：build/encode/decode
        m = re.search(r"(?:构建|建立|build)\s*(哈夫曼|哈夫曼树|huffman)\s*(?:频率|with)?\s*([A-Za-z0-9:,\s]+)", text, re.IGNORECASE)
        if m:
            pairs = _extract_huffman_pairs(m.group(2) or '')
            if not pairs:
                return None
            return "build huffman with " + ",".join([f"{c}:{f}" for c, f in pairs])

        m = re.search(r"(?:哈夫曼)?\s*编码\s*\"?([^\"\n]+)\"?(?:\s*使用\s*(哈夫曼|huffman))?", text, re.IGNORECASE)
        if m:
            txt = m.group(1).strip()
            return f"encode \"{txt}\" using huffman"

        m = re.search(r"(?:哈夫曼)?\s*解码\s*([01]+)(?:\s*使用\s*(哈夫曼|huffman))?", text, re.IGNORECASE)
        if m:
            binary = m.group(1)
            return f"decode {binary} using huffman"

        return None