# DSL 命令参考（按数据类型分类）

本参考列出可视化模拟器支持的 DSL 命令，按数据类型（线性 / 树形）归类。命令关键字与结构名均为小写。数值为整数；路径用逗号分隔的数字序列。

## 脚本模式（多行）

- 支持在输入框中编写多行脚本，每行一条命令。
- 也支持使用 `;` 分隔同一行中的多条命令。
- 允许注释：以 `#` 或 `//` 开头的行会被忽略。
- 执行范围：除全局 `clear` 外，在当前选项卡对应的数据结构类型内执行；跨类型命令会被拒绝。

历史记录与上下文说明：
- 界面按钮操作会自动映射为 DSL 并记录，便于复现与复制；脚本执行的 DSL 同样会进入历史。
- 历史按“边界”截取：全局 `clear` 或当前上下文的 `create/build` 之后的记录。
- 合并视图会合并线性与树形记录并按时间排序；较新的全局 `clear` 会作为边界行包含在合并视图中。
- 时间戳仅显示时间 `HH:MM:SS`；合并视图每行前显示上下文标签，例如：
  - `12:34:56 [linear] insert 5 at 1 in arraylist`
  - `12:35:01 [tree] build bst with 8,3,10,1,6`
  - `12:36:10 [global] clear`

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

提示：历史界面的合并视图会将 `clear` 显示为 `[global] clear`，并与时间戳一同排序显示。

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

界面显示提示：历史对话框采用彩色高亮（时间戳灰色、上下文标签分色、行首动词加粗紫色、数字绿色、引号文本橙色），等宽字体 20px，支持复制。

## 自然语言与 DSL 入口

- 自然语言：无前缀。直接在控制台输入中文/英文描述，系统会将其转换为 DSL，并在输出区预览后执行。
- DSL：需使用前缀 `DSL:`。示例：`DSL: create arraylist size 10`、`DSL: build bst with 10,5,7,3`。
- 常见自然语言表达示例：
  - `创建顺序表 值为 1,2,3`
  - `插入 99 在 位置 2 到 顺序表`
  - `入栈 10`、`出栈`、`查看栈顶`
  - `构建 BST 值为 5,2,7,3,9`
  - `构建 AVL 值为 10,20,30,40`
  - `创建 二叉树 值为 1,2,3`
  - `遍历 中序 在 二叉树`
  - `构建 哈夫曼 频率 a:5,b:2,c:1`
  - `编码 "abc" 使用 哈夫曼`、`解码 010011 使用 哈夫曼`

### 注意事项

- 若无明确上下文，系统将根据当前选项卡（线性/树形结构）推断目标；也会根据关键词（如 BST/AVL/哈夫曼/遍历）自动切换到树形规则。
- 词汇支持中英文同义词：如 “顺序表/数组”→`arraylist`，“链表”→`linkedlist`，“栈”→`stack`，“二叉树”→`binarytree`，“二叉搜索树/BST”→`bst`，“平衡二叉树/AVL”→`avl`，“哈夫曼(树)”→`huffman`；遍历支持 “先序/中序/后序/层序”。
- 当前实现为启发式规则转换，复杂表达可能无法完全识别；可尝试更明确的语句，或直接使用带前缀的 DSL 命令（`DSL:`）。