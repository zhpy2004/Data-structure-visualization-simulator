# 数据结构可视化模拟器 - DSL使用说明

## 概述

本项目实现了一个领域特定语言（DSL），用于操作和可视化各种数据结构。DSL支持线性结构（顺序表、链表、栈）和树形结构（二叉树、二叉搜索树、哈夫曼树）的操作。

## DSL语法结构

### 线性结构DSL语法

线性结构支持以下数据类型：`arraylist`（顺序表）、`linkedlist`（链表）、`stack`（栈）

#### 基本命令格式

```
# 创建结构
create arraylist|linkedlist|stack [with value1,value2,...]

# 插入操作
insert value at position in arraylist|linkedlist|stack

# 删除操作
delete value from arraylist|linkedlist|stack        # 按值删除
delete at position from arraylist|linkedlist|stack  # 按位置删除

# 查询操作
get value from arraylist|linkedlist|stack           # 按值查询
get at position from arraylist|linkedlist|stack     # 按位置查询

# 栈专用操作
push value to stack                                  # 入栈
pop from stack                                       # 出栈

# 清空操作
clear arraylist|linkedlist|stack
```

#### 线性结构命令示例

```
# 创建操作
create arraylist with 1,2,3,4,5
create linkedlist with 10,20,30
create stack

# 插入操作
insert 100 at 0 in arraylist
insert 50 at 2 in linkedlist

# 删除操作
delete 3 from arraylist          # 删除值为3的元素
delete at 1 from linkedlist      # 删除位置1的元素

# 查询操作
get 2 from arraylist             # 查询值为2的元素
get at 0 from linkedlist         # 查询位置0的元素

# 栈操作
push 42 to stack
pop from stack

# 清空操作
clear arraylist
```

### 树形结构DSL语法

树形结构支持以下数据类型：`binarytree`（二叉树）、`bst`（二叉搜索树）、`huffman`（哈夫曼树）

#### 基本命令格式

```
# 创建结构
create binarytree|bst|huffman [with value1,value2,...]

# 插入操作
insert value [at position1,position2,...] in binarytree|bst|huffman

# 删除操作
delete value [at position1,position2,...] from binarytree|bst|huffman

# 搜索操作
search value in binarytree|bst|huffman

# 遍历操作
traverse preorder|inorder|postorder|levelorder

# 哈夫曼树专用操作
build huffman with char:frequency,char:frequency,...
encode "text" using huffman
decode binary_string using huffman

# 清空操作
clear binarytree|bst|huffman
```

#### 树形结构命令示例

```
# 创建操作
create binarytree with 1,2,3,4,5
create bst with 50,30,70,20,40,60,80
create huffman

# 插入操作
insert 25 in bst                 # BST自动找位置插入
insert 15 at 0,0 in binarytree   # 在指定位置插入

# 删除操作
delete 30 from bst               # 从BST中删除值为30的节点
delete 5 at 1,0 from binarytree  # 从指定位置删除

# 搜索操作
search 40 in bst
search 3 in binarytree

# 遍历操作
traverse preorder                # 前序遍历
traverse inorder                 # 中序遍历
traverse postorder               # 后序遍历
traverse levelorder              # 层序遍历

# 哈夫曼树操作
build huffman with a:5,b:9,c:12,d:13,e:16,f:45
encode "hello" using huffman
decode 101010 using huffman

# 清空操作
clear bst
```

## 支持的命令详细说明

### 线性结构命令

#### 1. 创建命令 (create)
- **语法**: `create arraylist|linkedlist|stack [with value1,value2,...]`
- **功能**: 创建指定类型的线性结构，可选择性地初始化数据
- **示例**:
  ```
  create arraylist                    # 创建空的顺序表
  create linkedlist with 1,2,3       # 创建包含1,2,3的链表
  create stack with 10,20            # 创建包含10,20的栈
  ```

#### 2. 插入命令 (insert)
- **语法**: `insert value at position in structure_name`
- **功能**: 在指定位置插入元素
- **示例**:
  ```
  insert 100 at 0 in arraylist       # 在顺序表位置0插入100
  insert 50 at 2 in linkedlist       # 在链表位置2插入50
  ```

#### 3. 删除命令 (delete)
- **语法**: 
  - `delete value from structure_name` (按值删除)
  - `delete at position from structure_name` (按位置删除)
- **功能**: 删除指定的元素
- **示例**:
  ```
  delete 3 from arraylist             # 删除值为3的元素
  delete at 1 from linkedlist         # 删除位置1的元素
  ```

#### 4. 查询命令 (get)
- **语法**: 
  - `get value from structure_name` (按值查询)
  - `get at position from structure_name` (按位置查询)
- **功能**: 查询指定的元素
- **示例**:
  ```
  get 2 from arraylist                # 查询值为2的元素
  get at 0 from linkedlist            # 查询位置0的元素
  ```

#### 5. 栈操作命令 (push/pop)
- **语法**: 
  - `push value to stack` (入栈)
  - `pop from stack` (出栈)
- **功能**: 栈的专用操作
- **示例**:
  ```
  push 42 to stack                    # 将42压入栈
  pop from stack                      # 弹出栈顶元素
  ```

#### 6. 清空命令 (clear)
- **语法**: `clear structure_name`
- **功能**: 清空指定的数据结构
- **示例**:
  ```
  clear arraylist                     # 清空顺序表
  clear stack                         # 清空栈
  ```

### 树形结构命令

#### 1. 创建命令 (create)
- **语法**: `create binarytree|bst|huffman [with value1,value2,...]`
- **功能**: 创建指定类型的树结构
- **示例**:
  ```
  create binarytree with 1,2,3,4      # 创建包含1,2,3,4的二叉树
  create bst with 50,30,70            # 创建包含50,30,70的二叉搜索树
  create huffman                      # 创建空的哈夫曼树
  ```

#### 2. 插入命令 (insert)
- **语法**: `insert value [at position1,position2,...] in structure_name`
- **功能**: 在树中插入节点
- **示例**:
  ```
  insert 25 in bst                    # 在BST中插入25（自动找位置）
  insert 15 at 0,0 in binarytree      # 在二叉树指定位置插入15
  ```

#### 3. 删除命令 (delete)
- **语法**: `delete value [at position1,position2,...] from structure_name`
- **功能**: 从树中删除节点
- **示例**:
  ```
  delete 30 from bst                  # 从BST中删除值为30的节点
  delete 5 at 1,0 from binarytree     # 从指定位置删除节点
  ```

#### 4. 搜索命令 (search)
- **语法**: `search value in structure_name`
- **功能**: 在树中搜索指定值
- **示例**:
  ```
  search 40 in bst                    # 在BST中搜索40
  search 3 in binarytree              # 在二叉树中搜索3
  ```

#### 5. 遍历命令 (traverse)
- **语法**: `traverse preorder|inorder|postorder|levelorder`
- **功能**: 按指定方式遍历树
- **示例**:
  ```
  traverse preorder                   # 前序遍历
  traverse inorder                    # 中序遍历
  traverse postorder                  # 后序遍历
  traverse levelorder                 # 层序遍历
  ```

#### 6. 哈夫曼树专用命令

##### 构建哈夫曼树 (build huffman)
- **语法**: `build huffman with char:frequency,char:frequency,...`
- **功能**: 根据字符频率构建哈夫曼树
- **示例**:
  ```
  build huffman with a:5,b:9,c:12,d:13,e:16,f:45
  ```

##### 编码命令 (encode)
- **语法**: `encode "text" using huffman`
- **功能**: 使用哈夫曼树编码文本
- **示例**:
  ```
  encode "hello" using huffman
  ```

##### 解码命令 (decode)
- **语法**: `decode binary_string using huffman`
- **功能**: 使用哈夫曼树解码二进制字符串
- **示例**:
  ```
  decode 101010 using huffman
  ```

#### 7. 清空命令 (clear)
- **语法**: `clear structure_name`
- **功能**: 清空指定的树结构
- **示例**:
  ```
  clear bst                           # 清空二叉搜索树
  clear binarytree                    # 清空二叉树
  ```

## 完整使用示例

### 线性结构操作示例

```python
# 导入解析器
from utils.dsl_parser import parse_linear_dsl, parse_dsl_command

# 1. 顺序表操作
parse_linear_dsl("create arraylist with 1,2,3,4,5")
parse_linear_dsl("insert 100 at 0 in arraylist")
parse_linear_dsl("delete 3 from arraylist")
parse_linear_dsl("get at 2 from arraylist")
parse_linear_dsl("clear arraylist")

# 2. 链表操作
parse_linear_dsl("create linkedlist with 10,20,30")
parse_linear_dsl("insert 50 at 1 in linkedlist")
parse_linear_dsl("delete at 2 from linkedlist")
parse_linear_dsl("get 20 from linkedlist")

# 3. 栈操作
parse_linear_dsl("create stack")
parse_linear_dsl("push 42 to stack")
parse_linear_dsl("push 84 to stack")
parse_linear_dsl("pop from stack")
```

### 树形结构操作示例

```python
# 导入解析器
from utils.dsl_parser import parse_tree_dsl, parse_dsl_command

# 1. 二叉树操作
parse_tree_dsl("create binarytree with 1,2,3,4,5")
parse_tree_dsl("insert 6 at 2,0 in binarytree")
parse_tree_dsl("search 3 in binarytree")
parse_tree_dsl("traverse inorder")

# 2. 二叉搜索树操作
parse_tree_dsl("create bst with 50,30,70,20,40,60,80")
parse_tree_dsl("insert 25 in bst")
parse_tree_dsl("delete 30 from bst")
parse_tree_dsl("search 40 in bst")
parse_tree_dsl("traverse preorder")

# 3. 哈夫曼树操作
parse_tree_dsl("build huffman with a:5,b:9,c:12,d:13,e:16,f:45")
parse_tree_dsl("encode \"hello\" using huffman")
parse_tree_dsl("decode 101010 using huffman")
```

### 统一解析器使用

```python
# 使用统一解析器自动识别命令类型
result, cmd_type = parse_dsl_command("create arraylist with 1,2,3")
print(f"命令类型: {cmd_type}")  # 输出: linear
print(f"解析结果: {result}")

result, cmd_type = parse_dsl_command("build huffman with a:5,b:9")
print(f"命令类型: {cmd_type}")  # 输出: tree
print(f"解析结果: {result}")
```

## 语法规则说明

### 数据类型和值

1. **数值**: 支持整数，如 `1`, `42`, `100`
2. **字符**: 用于哈夫曼树，如 `a`, `b`, `c`
3. **字符串**: 用双引号包围，如 `"hello"`, `"world"`
4. **二进制**: 用于哈夫曼解码，如 `101010`, `110011`
5. **位置**: 用逗号分隔的数字序列，如 `0,1`, `2,0,1`

### 关键字说明

#### 结构类型关键字
- **线性结构**: `arraylist`, `linkedlist`, `stack`
- **树形结构**: `binarytree`, `bst`, `huffman`

#### 操作关键字
- **基本操作**: `create`, `insert`, `delete`, `get`, `search`, `clear`
- **栈操作**: `push`, `pop`
- **遍历操作**: `traverse`
- **哈夫曼操作**: `build`, `encode`, `decode`

#### 遍历类型关键字
- `preorder`: 前序遍历
- `inorder`: 中序遍历
- `postorder`: 后序遍历
- `levelorder`: 层序遍历

#### 连接词
- `with`: 用于指定初始数据
- `at`: 用于指定位置
- `in`/`from`: 用于指定目标结构
- `to`: 用于栈的push操作
- `using`: 用于哈夫曼编码/解码

## 错误处理

### 常见错误类型

1. **语法错误**: 命令格式不正确
   ```
   错误: create arraylist 1,2,3        # 缺少 with 关键字
   正确: create arraylist with 1,2,3
   ```

2. **类型错误**: 使用了不支持的数据结构类型
   ```
   错误: create queue with 1,2,3       # queue 不是支持的类型
   正确: create arraylist with 1,2,3
   ```

3. **参数错误**: 参数格式不正确
   ```
   错误: build huffman with a5,b9      # 缺少冒号分隔符
   正确: build huffman with a:5,b:9
   ```

### 错误信息格式

解析器返回的错误信息格式：
```python
{
    "error": "解析错误: 具体错误描述",
    "command": "error"
}
```

## 最佳实践

### 1. 命令编写建议

- 使用小写字母编写所有关键字
- 在数值之间使用逗号分隔，不要添加空格
- 字符串必须用双引号包围
- 位置参数用逗号分隔，表示树中的路径

### 2. 调试技巧

```python
# 使用统一解析器检查命令类型
result, cmd_type = parse_dsl_command(your_command)
if cmd_type == "unknown":
    print("命令类型无法识别，请检查语法")
elif "error" in result:
    print(f"解析错误: {result['error']}")
else:
    print(f"解析成功: {result}")
```

### 3. 性能优化

- 对于大量数据，建议分批创建和操作
- 复杂的树操作建议先创建基本结构，再逐步插入节点
- 哈夫曼树建议一次性提供完整的字符频率表

## 扩展功能建议

### 1. 批量操作
```
# 未来可能支持的批量操作
batch insert 1,2,3,4,5 in arraylist
batch delete 2,4 from arraylist
```

### 2. 条件操作
```
# 未来可能支持的条件操作
if exists 3 in arraylist then delete 3 from arraylist
```

### 3. 复合操作
```
# 未来可能支持的复合操作
create arraylist with 1,2,3 then insert 4 at 0 then sort
```

## 总结

本DSL系统提供了完整的数据结构操作语法，支持线性结构和树形结构的各种操作。通过统一的语法规则和清晰的命令格式，用户可以方便地进行数据结构的创建、操作和可视化。建议在使用时遵循最佳实践，并注意错误处理，以获得最佳的使用体验。