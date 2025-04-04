# Local Knowledge

Local Knowledge是一个基于Model Context Protocol (MCP)的服务，用于管理和提供本地知识库。

## 简介

本服务允许进行**有项目区分地、有作用域地**保存、更新和查询本地知识，将不同的知识作用于不同的工作区，以便大语言模型能够访问与当前工作区有关的知识。知识以JSON格式存储，并支持多种内容获取方式：直接内容、文件读取和脚本动态生成。

## 功能

- 列出所有知识描述
- 根据索引查询知识详情
- 添加新知识
- 更新已有知识

## 构建

```bash
# 构建安装包
python setup.py sdist bdist_wheel
```

## 安装

```bash
# 安装MCP依赖
pip install ./dist/local_knowledge-0.1.0-py3-none-any.whl
```

## 使用方法

### 配置

典型的cline mcp配置

```json
"mcpServers": {
  "local_knowledge": {
    "command": "python",
    "args": ["-m", "local_knowledge"]
  }
}
```

### 文件结构

知识库默认保存在工作目录的`.knowledge`文件中，以JSON格式存储。

由于每个工作目录的知识库文件是不同的，所以对于不同的工作区，可以访问不同的本地知识库

每条知识条目包含以下字段：

- `index`: 知识的唯一序号
- `description`: 知识的大体描述，用于让模型判断是否需要查询该条知识
- `detail`: (可选) 知识的具体内容
- `detail_file`: (可选) 知识内容的文件路径
- `detail_script`: (可选) 获取知识内容的脚本路径

### 字段协同工作机制

在查询知识详情时，系统会按照以下逻辑处理这些字段：

1. **description字段**：始终会被包含在返回结果中，作为知识的描述部分。

2. **detail字段**：如果存在，系统直接将其内容添加到结果中。这适用于简短且静态的知识内容。

3. **detail_file字段**：如果存在，系统会尝试读取指定文件的内容并添加到结果中。
   - 可以使用相对路径（相对于知识库文件目录）或绝对路径
   - 如果文件不存在或读取失败，会返回相应的错误信息

4. **detail_script字段**：如果存在，系统会：
   - 加载指定的Python脚本（可以是相对路径或绝对路径）
   - 调用脚本中的`detail()`函数
   - 将函数返回的内容添加到结果中
   - 如果脚本执行失败，会返回相应的错误信息

5. **优先级与组合**：这三种内容获取方式（detail、detail_file、detail_script）不互斥，可以同时存在。系统会按顺序处理并将所有获取到的内容组合成一个完整的知识详情返回。

示例：一个知识条目可能同时包含基本说明（detail）、详细文档（detail_file）和动态生成的最新数据（detail_script）。

```json
{
  "index": 1,
  "description": "产品A的规格说明",
  "detail": "产品A是一款高性能设备，支持...",
  "detail_file": "docs/productA_details.md",
  "detail_script": "scripts/get_latest_specs.py"
}
```

查询此条目时，返回的知识详情将包含：
- "产品A是一款高性能设备，支持..."（来自detail字段）
- productA_details.md文件的内容（来自detail_file字段）
- get_latest_specs.py脚本执行detail()函数返回的内容（来自detail_script字段）


## 提示词示例
.clinerules
``` 
每次用户有任务需求时，为了了解解决用户问题有哪些注意事项和可以参考的知识点，需要率先在local_knowledge mcp服务中进行查找，发现是否有需要遵循的规则或者与用户问题相关的可以利用的知识。
```


## MCP接口

### 工具

#### `list_knowledge`

列出所有知识的描述信息。

**参数**:
- `directory`: 知识文件所在的目录路径（绝对路径）

**返回**:
包含所有知识描述的列表。

#### `query_knowledge`

查询指定索引的知识详情。

**参数**:
- `directory`: 知识文件所在的目录路径（绝对路径）
- `indices`: 要查询的知识序号列表

**返回**:
查询到的知识详情列表。

#### `add_knowledge`

添加新的知识。

**参数**:
- `directory`: 知识文件所在的目录路径（绝对路径）
- `description`: 知识的描述
- `detail`: (可选) 知识的具体内容
- `detail_file`: (可选) 知识内容的文件路径
- `detail_script`: (可选) 获取知识内容的脚本路径

**返回**:
添加结果和知识索引。

#### `update_knowledge`

更新已有知识。

**参数**:
- `directory`: 知识文件所在的目录路径（绝对路径）
- `index`: 要更新的知识序号
- `description`: (可选) 更新后的知识描述
- `detail`: (可选) 更新后的知识内容
- `detail_file`: (可选) 更新后的知识文件路径
- `detail_script`: (可选) 更新后的知识脚本路径

**返回**:
更新结果。

