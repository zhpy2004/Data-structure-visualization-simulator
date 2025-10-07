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