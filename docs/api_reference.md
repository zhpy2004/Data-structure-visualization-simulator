# 数据结构可视化模拟器 API 参考文档

## 模型 (Models)

### 线性结构

#### ArrayList (顺序表)
- `__init__(self, capacity=10)` - 初始化顺序表，默认容量为10
- `append(self, value)` - 在末尾添加元素
- `insert(self, index, value)` - 在指定位置插入元素
- `remove(self, index)` - 删除指定位置的元素
- `get(self, index)` - 获取指定位置的元素
- `size(self)` - 获取顺序表当前大小
- `is_empty(self)` - 判断顺序表是否为空
- `clear(self)` - 清空顺序表

#### LinkedList (链表)
- `__init__(self)` - 初始化链表
- `append(self, value)` - 在末尾添加元素
- `insert(self, index, value)` - 在指定位置插入元素
- `remove(self, index)` - 删除指定位置的元素
- `get(self, index)` - 获取指定位置的元素
- `size(self)` - 获取链表当前大小
- `is_empty(self)` - 判断链表是否为空
- `clear(self)` - 清空链表

#### Stack (栈)
- `__init__(self, capacity=10)` - 初始化栈，默认容量为10
- `push(self, value)` - 入栈操作
- `pop(self)` - 出栈操作
- `peek(self)` - 查看栈顶元素
- `size(self)` - 获取栈当前大小
- `is_empty(self)` - 判断栈是否为空
- `clear(self)` - 清空栈

### 树形结构

#### BinaryTree (二叉树)
- `__init__(self)` - 初始化二叉树
- `insert(self, value)` - 插入节点
- `remove(self, value)` - 删除节点
- `preorder_traversal(self)` - 前序遍历
- `inorder_traversal(self)` - 中序遍历
- `postorder_traversal(self)` - 后序遍历
- `levelorder_traversal(self)` - 层序遍历
- `get_tree_data(self)` - 获取树的数据表示
- `build_from_data(self, data)` - 从数据构建树

#### BST (二叉搜索树)
- `__init__(self)` - 初始化二叉搜索树
- `insert(self, value)` - 插入节点
- `remove(self, value)` - 删除节点
- `search(self, value)` - 搜索节点
- `preorder_traversal(self)` - 前序遍历
- `inorder_traversal(self)` - 中序遍历
- `postorder_traversal(self)` - 后序遍历
- `levelorder_traversal(self)` - 层序遍历
- `get_tree_data(self)` - 获取树的数据表示
- `build_from_data(self, data)` - 从数据构建树

#### AVLTree (AVL树)
- `__init__(self)` - 初始化AVL树
- `insert(self, value)` - 插入节点（自动平衡）
- `remove(self, value)` - 删除节点（自动平衡）
- `search(self, value)` - 搜索节点
- `height(self, node)` - 获取节点高度
- `balance_factor(self, node)` - 获取节点平衡因子
- `left_rotate(self, node)` - 左旋操作
- `right_rotate(self, node)` - 右旋操作
- `preorder_traversal(self)` - 前序遍历
- `inorder_traversal(self)` - 中序遍历
- `postorder_traversal(self)` - 后序遍历
- `levelorder_traversal(self)` - 层序遍历
- `get_tree_data(self)` - 获取树的数据表示
- `build_from_data(self, data)` - 从数据构建树
- `get_build_steps(self, values)` - 获取构建步骤（用于动画）

#### HuffmanTree (哈夫曼树)
- `__init__(self)` - 初始化哈夫曼树
- `build(self, frequencies)` - 构建哈夫曼树
- `build_with_steps(self, frequencies)` - 构建哈夫曼树并记录步骤
- `encode(self, text)` - 编码文本
- `decode(self, binary)` - 解码二进制码
- `get_codes(self)` - 获取哈夫曼编码表
- `get_frequency_data(self)` - 获取频率数据
- `get_tree_data(self)` - 获取树的数据表示

## 控制器 (Controllers)

### AppController
- `__init__(self, main_window)` - 初始化应用控制器
- `init_app(self)` - 初始化应用
- `save_structure(self)` - 保存当前数据结构
- `load_structure(self)` - 加载数据结构

（说明）控制器会通过信号与主窗口交互，保存/加载由视图触发的请求。

### LinearController
- `__init__(self, view)` - 初始化线性结构控制器
- `create_structure(self, structure_type, values)` - 创建线性结构
- `insert_element(self, value, index)` - 插入元素
- `remove_element(self, index)` - 删除元素
- `get_element(self, index)` - 获取元素
- `push_element(self, value)` - 入栈操作
- `pop_element(self)` - 出栈操作
- `peek_element(self)` - 查看栈顶元素
- `get_structure_data(self)` - 获取当前数据结构数据
- `load_structure(self, structure_type, data)` - 加载数据结构

### TreeController
- `__init__(self, view)` - 初始化树形结构控制器
- `create_structure(self, structure_type, values)` - 创建树形结构
- `insert_node(self, value)` - 插入节点
- `remove_node(self, value)` - 删除节点
- `search_node(self, value)` - 搜索节点
- `traverse_tree(self, traverse_type)` - 遍历树
- `encode_text(self, text)` - 编码文本
- `decode_binary(self, binary)` - 解码二进制码
- `get_structure_data(self)` - 获取当前数据结构数据
- `load_structure(self, structure_type, data)` - 加载数据结构
- `_build_huffman_tree(self, frequencies)` - 构建哈夫曼树
- `show_avl_build_animation(self, values)` - 显示AVL树构建动画
- `_update_avl_animation(self)` - 更新AVL树动画
- `_next_avl_step(self)` - AVL树动画下一步
- `_prev_avl_step(self)` - AVL树动画上一步

## 视图 (Views)

### MainWindow
- `__init__(self)` - 初始化主窗口
- `_init_ui(self)` - 初始化UI
- `_connect_signals(self)` - 连接信号和槽
- `show_message(self, message)` - 显示消息
- `_show_history_dialog(self, title, context)` - 显示历史记录对话框
  - `context`：`"linear"` / `"tree"` / `None`（合并视图）
  - 说明：使用 HTML 富文本渲染历史记录，包含时间戳（仅 `HH:MM:SS`）、上下文标签（合并视图下显示 `[linear]`、`[tree]`、`[global]`），动词加粗紫色、数字绿色、引号文本橙色；等宽字体字号 20px；只读但支持复制

菜单项（菜单栏）
- `历史`（同级于 `文件`、`帮助`）
  - `查看线性历史` → 打开 `context="linear"` 的历史对话框
  - `查看树形历史` → 打开 `context="tree"` 的历史对话框
  - `查看全部历史` → 打开合并视图（`context=None`）

### LinearView
- `__init__(self)` - 初始化线性结构视图
- `_init_ui(self)` - 初始化UI
- `_connect_signals(self)` - 连接信号和槽
- `update_view(self, structure_data)` - 更新视图
- `clear_view(self)` - 清空视图
- `show_message(self, message)` - 显示消息

### TreeView
- `__init__(self)` - 初始化树形结构视图
- `_init_ui(self)` - 初始化UI
- `_connect_signals(self)` - 连接信号和槽
- `update_view(self, structure_data)` - 更新视图
- `clear_view(self)` - 清空视图
- `show_message(self, message)` - 显示消息
- `show_animation(self, animation_data)` - 显示动画
- `_structure_changed(self, index)` - 处理数据结构类型变更
- `show_avl_build_animation(self, values)` - 显示AVL树构建动画
- `_update_avl_animation(self)` - 更新AVL树动画显示
- `_next_avl_step(self)` - AVL树动画下一步
- `_prev_avl_step(self)` - AVL树动画上一步

## 工具类 (Utils)

### DSLParser
- `parse(self, code)` - 解析DSL代码
- `execute(self, controller)` - 执行解析后的命令

### VisualizationHelper
- `draw_tree(self, tree_data, canvas)` - 绘制树
- `draw_linear(self, linear_data, canvas)` - 绘制线性结构
- `animate_traversal(self, steps, canvas)` - 动画展示遍历过程
- `animate_search(self, steps, canvas)` - 动画展示搜索过程
- `animate_huffman_build(self, steps, canvas)` - 动画展示哈夫曼树构建过程
- `animate_avl_build(self, steps, canvas)` - 动画展示AVL树构建过程
- `draw_avl_rotation(self, rotation_data, canvas)` - 绘制AVL树旋转操作
- `show_balance_factors(self, tree_data, canvas)` - 显示节点平衡因子

## 服务 (Services)

### OperationRecorder
- `record_dsl(dsl_text, context, success=True, source="dsl")` - 记录一条 DSL 操作到指定上下文（`linear`/`tree`/`global`）
- `record_linear_action(action_type, params, structure_type, executed=True)` - 将线性结构界面按钮操作映射为 DSL 并记录
- `record_tree_action(action_type, params, structure_type, executed=True)` - 将树形结构界面按钮操作映射为 DSL 并记录
- `get_history(context)` → `List[str]` - 获取指定上下文的历史 DSL 文本列表（按边界过滤）
- `get_history_text(context)` → `str` - 获取指定上下文的历史 DSL 文本（按行拼接）
- `get_history_entries(context)` → `List[Dict[str, Any]]` - 获取带时间戳与上下文的历史条目（字段：`dsl`、`ts`、`ctx`），合并视图按时间排序并包含最近的全局 `clear` 作为边界（若适用）
- `get_history_text_with_ts(context)` → `str` - 获取带时间戳（仅 `HH:MM:SS`）的历史文本；合并视图在每行前显示 `[ctx]` 标签

说明与边界规则：
- 历史按“边界”截取：全局 `clear` 或当前上下文的 `create/build` 事件之后的记录
- 合并视图会合并 `linear` 与 `tree` 的记录并按时间排序；若较新的全局 `clear` 出现在边界之后，则作为边界行包含在合并视图中
- 记录仅保存在内存中，应用重启后清空