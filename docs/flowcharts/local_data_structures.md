# 局部数据结构说明（核心模型）

本节描述项目中最常用的局部数据结构及其要点，便于理解控制器与动画的行为。

## 线性结构

ArrayList（顺序表）采用 Python list 进行顺序存储，可选 `capacity` 用于容量控制并支持初始化值；越界与容量校验由控制器处理。典型操作包括 `insert(index, value)`、`delete(index)`、`get(index)` 以及清空和重建。

LinkedList（链表）由 `Node` 节点构成，节点包含 `Node.value` 与 `Node.next` 指针，结构体内部保留头指针。常见操作为按位置或按值的插入与删除、`get(index)` 查询；遍历同时用于动画绘制与索引查找。

Stack（栈）基于 Python list 实现，提供 `push(value)`、`pop()` 与 `peek()` 等操作；越界和空栈提示由控制器与视图共同处理。

## 树形结构

BinaryTree（二叉树）以 `TreeNode` 为节点，节点包含 `TreeNode.value`、`TreeNode.left` 与 `TreeNode.right`。BinaryTree 支持按层序创建以及按路径进行插入或删除（路径 0/1 分别表示左/右）。常见操作包括 `insert(value, path)`、`delete(value, path)` 与 `traverse(type)`，遍历类型包含 `preorder`、`inorder`、`postorder` 与 `levelorder`。

BST（二叉搜索树）使用 `TreeNode` 作为节点，通过按序插入的 `build` 方法生成并保持“左小右大”的搜索性质。常见操作包括 `insert(value)`、`delete(value)` 与 `search(value)`，构建与插入的过程与动画节奏队列配合。

AVLTree（平衡二叉树）以 `AVLNode` 为节点，节点包含 `AVLNode.value`、`AVLNode.left/right` 与 `AVLNode.height`。在插入或删除后通过旋转与高度更新维持平衡。常见操作包括 `build(values)`、`insert(value)`、`delete(value)` 与 `search(value)`，动画重点展示旋转和重平衡过程。

HuffmanTree（哈夫曼树）以 `HuffmanNode` 为节点，节点包含 `HuffmanNode.char`、`HuffmanNode.freq` 与 `left/right`，依据字符频率构建最优前缀码树。常见操作包括 `build(pairs)`（如 `a:5,b:2`）、`encode(text)` 与 `decode(binary)`，视图支持路径高亮以展示编码过程。

## 关联与记录

控制器与视图通过信号联动，如 `operation_triggered` 与 `dsl_command_triggered`。`OperationRecorder` 记录 DSL 与按钮动作，并以“清空、创建、构建”等边界维护最近历史；在自然语言转换到 DSL 的流程中，`LLMAgent` 会引用历史文本以增强提示效果。