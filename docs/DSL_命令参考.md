# DSL 命令参考（按数据类型分类）

本参考列出可视化模拟器支持的 DSL 命令，按数据类型（线性 / 树形）归类。命令关键字与结构名均为小写。数值为整数；路径用逗号分隔的数字序列。

## 脚本模式（多行）

- 支持在输入框中编写多行脚本，每行一条命令。
- 也支持使用 `;` 分隔同一行中的多条命令。
- 允许注释：以 `#` 或 `//` 开头的行会被忽略。
- 执行范围：除全局 `clear` 外，在当前选项卡对应的数据结构类型内执行；跨类型命令会被拒绝。

示例：
```
# 初始化顺序表并插入元素
create arraylist size 10
insert 1 at 0 in arraylist
insert 2 at 1 in arraylist; insert 3 at 2 in arraylist
```


## 线性结构（arraylist / linkedlist / stack）

通用结构名：`arraylist`、`linkedlist`、`stack`

- create
  - 语法：`create STRUCTURE_TYPE [with v1,v2,...] [size N]`
  - 示例：`create arraylist size 20`、`create arraylist with 1,2,3 size 10`
- clear
  - 语法：`clear`
  - 说明：清除当前工作区所有已创建的数据结构（线性与树形）
  - 示例：`clear`

ArrayList / LinkedList（顺序表 / 链表）
- insert
  - 语法：`insert VALUE at POSITION in STRUCTURE_NAME`
  - 示例：`insert 99 at 1 in arraylist`
- delete
  - 语法：`delete VALUE from STRUCTURE_NAME` 或 `delete at POSITION from STRUCTURE_NAME`
  - 示例：`delete 99 from linkedlist`、`delete at 2 from arraylist`
- get
  - 语法：`get VALUE from STRUCTURE_NAME` 或 `get at POSITION from STRUCTURE_NAME`
  - 示例：`get at 0 from linkedlist`

Stack（栈）
- push
  - 语法：`push VALUE to stack`
  - 示例：`push 4 to stack`
- pop
  - 语法：`pop from stack`
  - 示例：`pop from stack`
- peek
  - 语法：`peek stack`
  - 示例：`peek stack`

## 树形结构（binarytree / bst / avl / huffman）

通用结构名：`binarytree`、`bst`、`avl`、`huffman`

通用命令
- create
  - 语法：`create STRUCTURE_TYPE [with v1,v2,...]`
  - 示例：`create binarytree with 1,2,3,4`
- traverse
  - 语法：`traverse TRAVERSE_TYPE [in binarytree]`
  - 类型：`preorder` / `inorder` / `postorder` / `levelorder`
  - 说明：遍历命令仅支持普通二叉树（binarytree），在 BST/AVL/Huffman 上不支持。
  - 示例：`traverse inorder in binarytree`
- clear
  - 语法：`clear`
  - 说明：清除当前工作区所有已创建的数据结构（线性与树形）
  - 示例：`clear`

BinaryTree（二叉树，按层序构造）
- insert（支持路径插入）
  - 语法：`insert VALUE [at p1,p2,...] in binarytree`
  - 示例：`insert 1 in binarytree`（未指定路径按层序插入），`insert 6 at 0,1 in binarytree`
  - 路径语义：`0` 表示左，`1` 表示右；路径为空表示根位置。
- delete（支持路径删除）
  - 语法：`delete VALUE [at p1,p2,...] from binarytree`
  - 示例：`delete 6 at 0,1 from binarytree`
  - 说明：若提供路径，将按路径定位节点；不提供路径时按值匹配（如模型支持）。

BST（二叉搜索树）
- build
  - 语法：`build bst with v1,v2,...`
  - 示例：`build bst with 10,5,7,3,12,15,18`
- insert
  - 语法：`insert VALUE in bst`
  - 示例：`insert 7 in bst`
- delete
  - 语法：`delete VALUE from bst`
  - 示例：`delete 5 from bst`
- search
  - 语法：`search VALUE in bst`
  - 示例：`search 7 in bst`

AVL（平衡二叉树）
- build
  - 语法：`build avl with v1,v2,...`
  - 示例：`build avl with 30,20,40,10,25,50`
- insert
  - 语法：`insert VALUE in avl`
  - 示例：`insert 25 in avl`
- delete
  - 语法：`delete VALUE from avl`
  - 示例：`delete 20 from avl`
- search
  - 语法：`search VALUE in avl`
  - 示例：`search 25 in avl`

Huffman（哈夫曼树）
- build
  - 语法：`build huffman with c1:freq1,c2:freq2,...`
  - 示例：`build huffman with a:5,b:2,c:1`
- encode
  - 语法：`encode "TEXT" using huffman`
  - 示例：`encode "abac" using huffman`
- decode
  - 语法：`decode BINARY using huffman`
  - 示例：`decode 010111 using huffman`

## 带前缀的树命令（点号风格）

可选的前缀风格：`tree.<structure>.<command>`。支持：`create`、`insert`、`delete`、`search`、`traverse`、`clear`。

- 示例（BinaryTree）
  - `tree.binary_tree.create 1,2,3`
  - `tree.binary_tree.insert 6 at 0,1`
  - `tree.binary_tree.traverse inorder`
- 示例（BST）
  - `tree.bst.create 10,5,7,3,12,15,18`
  - `tree.bst.insert 7`
  - `tree.bst.search 7`
  - `tree.bst.delete 5`

注意：`build` 命令使用非前缀写法（如 `build bst with ...`、`build avl with ...`、`build huffman with ...`）。

提示：点号风格中的 `traverse` 仅支持 `tree.binary_tree.traverse`。

## 常见错误与提示

- 线性结构名称不支持下划线：`array_list` 会报错，应使用 `arraylist`。
 - BinaryTree 插入需先新建：未新建时插入会报错；新建后未指定路径按层序插入根或后续节点；若提供路径但位置无效会提示“路径无效”。
- `search` 主要支持 BST/AVL；在 BinaryTree/Huffman 上可能不支持或无意义。
- `traverse` 仅支持 BinaryTree；在 BST/AVL/Huffman 上不支持遍历命令。
- 所有命令关键字与结构名均为小写；值为整数，路径为逗号分隔整数序列；`encode` 文本需使用双引号。
 - 未新建结构直接操作：未执行 `create` 的情况下，`insert`/`delete`/`get`/`push`/`pop`/`peek`/`traverse`/`search`/`clear` 等命令会提示“请先创建数据结构”，不会自动创建空结构。