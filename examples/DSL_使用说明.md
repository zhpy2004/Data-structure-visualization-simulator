# 数据结构可视化模拟器 - DSL使用说明

## 概述

本项目实现了一个领域特定语言（DSL），用于操作和可视化各种数据结构。DSL支持线性结构（顺序表、链表、栈）和树形结构（二叉树、二叉搜索树、哈夫曼树）的操作。

## DSL语法结构

### 线性结构DSL语法

```
# 创建结构
create arraylist|linkedlist|stack [with values]

# 插入操作
insert value at position in structure_name

# 删除操作
delete value|at position from structure_name

# 查询操作
get value|at position from structure_name

# 栈操作
push value to stack
pop from stack

# 清空操作
clear structure_name
```

### 树形结构DSL语法

```
# 创建结构
create binarytree|bst|huffman [with values]

# 插入操作
insert value [at position] in structure_name

# 删除操作
delete value [at position] from structure_name

# 搜索操作
search value in structure_name

# 遍历操作
traverse preorder|inorder|postorder|levelorder

# 哈夫曼树操作
build huffman with char:freq,char:freq,...
encode "text" using huffman
decode binary using huffman

# 清空操作
clear structure_name
```

## 测试结果总结

### ✅ 当前工作正常的功能

1. **哈夫曼树构建**
   - 命令: `build huffman with a:5,b:9,c:12,d:13,e:16,f:45`
   - 支持字符和数字作为键值

2. **命令类型识别**
   - 系统能够正确识别线性结构和树形结构命令
   - 自动分发到相应的解析器

3. **基本语法解析**
   - 哈夫曼树相关命令解析正常
   - 命令分类功能正常

### ❌ 需要修复的功能

1. **线性结构操作**
   - 创建、插入、删除、查询等基本操作存在解析问题
   - 转换器实现不完整

2. **树形结构操作**
   - 除哈夫曼树外的其他树操作存在问题
   - 遍历命令解析器参数传递错误

3. **错误处理**
   - 部分错误情况处理不当
   - 异常信息不够清晰

## 使用示例

### 成功示例

```python
# 导入解析器
from utils.dsl_parser import parse_tree_dsl, parse_dsl_command

# 构建哈夫曼树
result = parse_tree_dsl("build huffman with a:5,b:9,c:12,d:13,e:16,f:45")
print(result)

# 使用统一解析器识别命令类型
result, cmd_type = parse_dsl_command("build huffman with a:5,b:9")
print(f"命令类型: {cmd_type}")
print(f"解析结果: {result}")
```

### 当前限制

1. **语法限制**
   - 部分命令的参数解析存在问题
   - 错误处理机制不完善

2. **功能限制**
   - 线性结构的大部分操作暂时无法正常工作
   - 树形结构中除哈夫曼树外的操作需要修复

## 测试文件说明

### 1. `dsl_comprehensive_test.py`
- 全面的DSL功能测试
- 包含所有预期的DSL命令
- 用于发现解析器问题

### 2. `dsl_corrected_test.py`
- 使用正确语法的测试文件
- 分别测试线性和树形结构
- 更详细的错误分析

### 3. `dsl_working_test.py`
- 专门测试当前能够工作的功能
- 演示成功的DSL操作
- 提供使用示例

## 运行测试

```bash
# 运行全面测试
python examples/dsl_comprehensive_test.py

# 运行修正测试
python examples/dsl_corrected_test.py

# 运行工作功能测试
python examples/dsl_working_test.py
```

## 开发建议

### 需要修复的问题

1. **修复转换器参数传递**
   ```python
   # 当前问题: 参数传递不正确
   @v_args(inline=True)
   def traverse_type(self, t):
       return str(t)
   ```

2. **完善错误处理**
   - 添加更详细的错误信息
   - 改进异常处理机制

3. **统一返回格式**
   - 确保所有解析器返回一致的格式
   - 避免混合使用tuple和dict

### 扩展建议

1. **添加更多数据结构**
   - 队列、双端队列
   - 图结构
   - 堆结构

2. **增强DSL功能**
   - 批量操作命令
   - 条件操作
   - 循环操作

3. **改进用户体验**
   - 命令自动补全
   - 语法高亮
   - 实时错误提示

## 结论

当前的DSL实现具有基本的框架和部分工作功能，特别是哈夫曼树相关操作。但是需要进一步完善解析器实现，修复参数传递问题，并改进错误处理机制。建议优先修复线性结构操作和树形结构的基本操作，然后逐步扩展更高级的功能。