from collections import deque


class AVLNode:
    def __init__(self, node_id: int, value: int):
        self.id = node_id
        self.value = int(value)
        self.left = None
        self.right = None
        self.parent = None
        self.height = 1


class AVLTree:
    def __init__(self):
        self.root = None
        self._next_id = 1

    # ---------- 基础工具 ----------
    def clear(self):
        self.root = None
        self._next_id = 1

    def _new_node(self, value: int) -> AVLNode:
        node = AVLNode(self._next_id, int(value))
        self._next_id += 1
        return node

    def _h(self, n: AVLNode) -> int:
        return n.height if n else 0

    def _update(self, n: AVLNode):
        if n:
            n.height = 1 + max(self._h(n.left), self._h(n.right))

    def _bf(self, n: AVLNode) -> int:
        return (self._h(n.left) - self._h(n.right)) if n else 0

    def _update_heights_all(self):
        def dfs(n):
            if not n:
                return 0
            lh = dfs(n.left)
            rh = dfs(n.right)
            n.height = 1 + max(lh, rh)
            return n.height
        dfs(self.root)

    # ---------- 旋转 ----------
    def _rotate_left(self, z: AVLNode) -> AVLNode:
        y = z.right
        t2 = y.left
        y.left = z
        z.right = t2
        if t2:
            t2.parent = z
        y.parent = z.parent
        if z.parent:
            if z.parent.left is z:
                z.parent.left = y
            else:
                z.parent.right = y
        else:
            self.root = y
        z.parent = y
        self._update(z)
        self._update(y)
        return y

    def _rotate_right(self, z: AVLNode) -> AVLNode:
        y = z.left
        t3 = y.right
        y.right = z
        z.left = t3
        if t3:
            t3.parent = z
        y.parent = z.parent
        if z.parent:
            if z.parent.left is z:
                z.parent.left = y
            else:
                z.parent.right = y
        else:
            self.root = y
        z.parent = y
        self._update(z)
        self._update(y)
        return y

    # ---------- 快照 ----------
    def _snapshot(self):
        nodes = []
        edges = []
        if not self.root:
            return {"nodes": nodes, "edges": edges, "type": "avl_tree"}
        q = deque([self.root])
        seen = set()
        while q:
            n = q.popleft()
            if not n or n in seen:
                continue
            seen.add(n)
            nodes.append({
                "id": n.id,
                "value": n.value,
                "parent_id": n.parent.id if n.parent else None,
                "height": n.height,
                "balance_factor": self._bf(n),
            })
            if n.left:
                edges.append({"source": n.id, "target": n.left.id})
                q.append(n.left)
            if n.right:
                edges.append({"source": n.id, "target": n.right.id})
                q.append(n.right)
        return {"nodes": nodes, "edges": edges, "type": "avl_tree"}

    # ---------- 查找路径（与二叉树同动画逻辑） ----------
    def find_insert_path(self, value: int):
        path = []
        v = int(value)
        n = self.root
        while n:
            path.append(n.value)
            if v < n.value:
                n = n.left
            else:
                n = n.right
        return path

    def find_delete_path(self, value: int):
        found, path = self.search(value)
        return path

    def search(self, value: int):
        v = int(value)
        path = []
        n = self.root
        while n:
            path.append(n.value)
            if v == n.value:
                return True, path
            if v < n.value:
                n = n.left
            else:
                n = n.right
        return False, path

    # ---------- 插入 ----------
    def insert(self, value: int):
        for step in self.insert_with_steps(value):
            pass

    def insert_with_steps(self, value: int):
        v = int(value)
        steps = []
        steps.append({
            "description": f"开始插入 {v}",
            "pending_node": {"id": -1, "value": v},
            "tree": self._snapshot(),
        })
        if not self.root:
            self.root = self._new_node(v)
            steps.append({
                "description": f"树为空，作为根节点插入 {v}",
                "highlight_nodes": [self.root.id],
                "tree": self._snapshot(),
            })
        else:
            n = self.root
            parent = None
            while n:
                parent = n
                if v < n.value:
                    n = n.left
                else:
                    n = n.right
            new_node = self._new_node(v)
            new_node.parent = parent
            if v < parent.value:
                parent.left = new_node
            else:
                parent.right = new_node
            # 更新高度
            cur = new_node
            while cur:
                self._update(cur)
                cur = cur.parent
            steps.append({
                "description": f"插入 {v} 完成，检查平衡",
                "highlight_nodes": [new_node.id],
                "tree": self._snapshot(),
            })
            # 逐步再平衡（按首次不平衡点，单步展示）
            self._update_heights_all()
            while True:
                z = self._first_unbalanced()
                if not z:
                    break
                bfz = self._bf(z)
                if bfz > 1:
                    # 左重
                    bfy = self._bf(z.left)
                    if bfy >= 0:
                        steps.append({
                            "description": f"节点 {z.value} 左重(LL)，右旋修复",
                            "highlight_nodes": [z.id, z.left.id if z.left else None],
                            "tree": self._snapshot(),
                        })
                        self._rotate_right(z)
                        self._update_heights_all()
                        steps.append({
                            "description": "完成右旋",
                            "tree": self._snapshot(),
                        })
                    else:
                        steps.append({
                            "description": f"节点 {z.value} 左右不平衡(LR)，先左旋子树再右旋",
                            "highlight_nodes": [z.id, z.left.id if z.left else None],
                            "tree": self._snapshot(),
                        })
                        self._rotate_left(z.left)
                        self._rotate_right(z)
                        self._update_heights_all()
                        steps.append({
                            "description": "完成 LR 旋转",
                            "tree": self._snapshot(),
                        })
                else:
                    # 右重
                    bfy = self._bf(z.right)
                    if bfy <= 0:
                        steps.append({
                            "description": f"节点 {z.value} 右重(RR)，左旋修复",
                            "highlight_nodes": [z.id, z.right.id if z.right else None],
                            "tree": self._snapshot(),
                        })
                        self._rotate_left(z)
                        self._update_heights_all()
                        steps.append({
                            "description": "完成左旋",
                            "tree": self._snapshot(),
                        })
                    else:
                        steps.append({
                            "description": f"节点 {z.value} 右左不平衡(RL)，先右旋子树再左旋",
                            "highlight_nodes": [z.id, z.right.id if z.right else None],
                            "tree": self._snapshot(),
                        })
                        self._rotate_right(z.right)
                        self._rotate_left(z)
                        self._update_heights_all()
                        steps.append({
                            "description": "完成 RL 旋转",
                            "tree": self._snapshot(),
                        })
        steps.append({"description": "插入完成", "tree": self._snapshot()})
        return steps

    def _first_unbalanced(self) -> AVLNode:
        if not self.root:
            return None
        q = deque([self.root])
        while q:
            n = q.popleft()
            if not n:
                continue
            bf = self._bf(n)
            if bf > 1 or bf < -1:
                return n
            if n.left:
                q.append(n.left)
            if n.right:
                q.append(n.right)
        return None

    # ---------- 删除 ----------
    def delete(self, value: int):
        for step in self.delete_with_steps(value) or []:
            pass

    def delete_with_steps(self, value: int):
        v = int(value)
        if not self.root:
            return []
        steps = [{
            "description": f"开始删除 {v}",
            "tree": self._snapshot(),
        }]
        # 查找目标
        target = self.root
        while target and target.value != v:
            if v < target.value:
                target = target.left
            else:
                target = target.right
        if not target:
            steps.append({"description": f"未找到 {v}", "tree": self._snapshot()})
            return steps
        steps.append({
            "description": f"找到节点 {v}，执行删除",
            "highlight_nodes": [target.id],
            "tree": self._snapshot(),
        })
        # 删除
        def transplant(u: AVLNode, v_node: AVLNode):
            if not u.parent:
                self.root = v_node
            elif u is u.parent.left:
                u.parent.left = v_node
            else:
                u.parent.right = v_node
            if v_node:
                v_node.parent = u.parent
        if not target.left and not target.right:
            transplant(target, None)
        elif not target.left:
            transplant(target, target.right)
        elif not target.right:
            transplant(target, target.left)
        else:
            # 两个孩子，用后继替换
            succ = target.right
            while succ.left:
                succ = succ.left
            steps.append({
                "description": f"节点有两个孩子，用后继 {succ.value} 替换",
                "highlight_nodes": [target.id, succ.id],
                "tree": self._snapshot(),
            })
            target.value = succ.value
            # 删除后继
            if succ.right:
                transplant(succ, succ.right)
            else:
                transplant(succ, None)
        # 再平衡
        self._update_heights_all()
        while True:
            z = self._first_unbalanced()
            if not z:
                break
            bfz = self._bf(z)
            if bfz > 1:
                bfy = self._bf(z.left)
                if bfy >= 0:
                    steps.append({
                        "description": f"删除后不平衡：{z.value} 左重(LL)，右旋",
                        "highlight_nodes": [z.id, z.left.id if z.left else None],
                        "tree": self._snapshot(),
                    })
                    self._rotate_right(z)
                    self._update_heights_all()
                    steps.append({"description": "完成右旋", "tree": self._snapshot()})
                else:
                    steps.append({
                        "description": f"删除后不平衡：{z.value} LR，先左旋子树再右旋",
                        "highlight_nodes": [z.id, z.left.id if z.left else None],
                        "tree": self._snapshot(),
                    })
                    self._rotate_left(z.left)
                    self._rotate_right(z)
                    self._update_heights_all()
                    steps.append({"description": "完成 LR 旋转", "tree": self._snapshot()})
            else:
                bfy = self._bf(z.right)
                if bfy <= 0:
                    steps.append({
                        "description": f"删除后不平衡：{z.value} 右重(RR)，左旋",
                        "highlight_nodes": [z.id, z.right.id if z.right else None],
                        "tree": self._snapshot(),
                    })
                    self._rotate_left(z)
                    self._update_heights_all()
                    steps.append({"description": "完成左旋", "tree": self._snapshot()})
                else:
                    steps.append({
                        "description": f"删除后不平衡：{z.value} RL，先右旋子树再左旋",
                        "highlight_nodes": [z.id, z.right.id if z.right else None],
                        "tree": self._snapshot(),
                    })
                    self._rotate_right(z.right)
                    self._rotate_left(z)
                    self._update_heights_all()
                    steps.append({"description": "完成 RL 旋转", "tree": self._snapshot()})
        steps.append({"description": "删除完成", "tree": self._snapshot()})
        return steps



    # ---------- 可视化数据 ----------
    def get_visualization_data(self):
        snap = self._snapshot()
        return {"type": "avl_tree", "nodes": snap.get("nodes", []), "edges": snap.get("edges", [])}

    # ---------- 遍历 ----------
    def inorder_traversal(self):
        res = []
        def dfs(n):
            if not n:
                return
            dfs(n.left)
            res.append(n.value)
            dfs(n.right)
        dfs(self.root)
        return res

    def preorder_traversal(self):
        res = []
        def dfs(n):
            if not n:
                return
            res.append(n.value)
            dfs(n.left)
            dfs(n.right)
        dfs(self.root)
        return res

    def postorder_traversal(self):
        res = []
        def dfs(n):
            if not n:
                return
            dfs(n.left)
            dfs(n.right)
            res.append(n.value)
        dfs(self.root)
        return res

    def levelorder_traversal(self):
        res = []
        if not self.root:
            return res
        q = deque([self.root])
        while q:
            n = q.popleft()
            res.append(n.value)
            if n.left:
                q.append(n.left)
            if n.right:
                q.append(n.right)
        return res

    def build_with_steps(self, values):
        values_list = list(values) if isinstance(values, (list, tuple)) else [values]
        steps = [{
            "description": f"初始化：准备插入值 {values_list}",
            "tree": self._snapshot(),
        }]
        # 重新开始构建
        self.clear()
        for v in values_list:
            insert_steps = self.insert_with_steps(v)
            steps.extend(insert_steps)
        steps.append({"description": "AVL树构建完成", "tree": self._snapshot()})
        return steps