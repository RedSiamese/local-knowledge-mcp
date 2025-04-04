# 本地知识服务 - 使用说明

## 简介

本服务用于保存和向大模型提供本地知识。知识以JSON格式存储，并通过MCP服务提供接口访问。

## 安装依赖

```bash
pip install mcp
```

## 启动服务

```bash
# 以HTTP服务器模式启动
python -m local_knowledge --port 8787 --file knowledge.json

# 以标准输入输出模式启动（用于与其他MCP服务集成）
python -m local_knowledge --stdio --file knowledge.json
```

可以通过环境变量自定义配置：
- `MCP_PORT`: 服务端口号（默认8787）
- `KNOWLEDGE_FILE`: 知识文件路径（默认knowledge.json）

## 作为库使用

```python
from local_knowledge import KnowledgeService, run_server, serve
import asyncio

# 使用知识服务
knowledge_service = KnowledgeService("knowledge.json")
knowledge_list = knowledge_service.query_all_knowledge()

# 启动HTTP服务器
run_server(port=8787, knowledge_file="knowledge.json")

# 或者启动标准输入输出模式的服务
asyncio.run(serve(knowledge_file="knowledge.json"))
```

## 工具和提示词说明

### 工具列表

本服务提供以下MCP工具：

1. `list_knowledge` - 列出所有知识的描述信息
2. `query_knowledge` - 查询指定索引的知识详情
3. `add_knowledge` - 添加新的知识
4. `update_knowledge` - 更新已有的知识

### 提示词列表

本服务提供以下MCP提示词：

1. `list_knowledge` - 列出所有知识的描述信息
2. `query_knowledge` - 查询指定索引的知识详情
3. `add_knowledge` - 添加新的知识
4. `update_knowledge` - 更新已有的知识

## 调用示例

### 列出所有知识描述

```python
# 工具调用
response = await mcp_client.call_tool("list_knowledge", {})

# 提示词调用
prompt_result = await mcp_client.get_prompt("list_knowledge", {})
```

### 查询知识详情

```python
# 工具调用
response = await mcp_client.call_tool("query_knowledge", {"indices": [0, 1, 2]})

# 提示词调用
prompt_result = await mcp_client.get_prompt("query_knowledge", {"indices": [0, 1, 2]})
```

### 添加知识

```python
# 工具调用
response = await mcp_client.call_tool("add_knowledge", {
    "description": "知识描述",
    "detail": "知识内容",  # 可选
    "detail_file": "/path/to/file.txt",  # 可选
    "detail_script": "/path/to/script.py"  # 可选
})

# 提示词调用
prompt_result = await mcp_client.get_prompt("add_knowledge", {
    "description": "知识描述",
    "detail": "知识内容",  # 可选
    "detail_file": "/path/to/file.txt",  # 可选
    "detail_script": "/path/to/script.py"  # 可选
})
```

### 修改知识

```python
# 工具调用
response = await mcp_client.call_tool("update_knowledge", {
    "index": 0,
    "description": "更新后的知识描述",
    "detail": "更新后的知识内容",  # 可选
    "detail_file": "/path/to/new_file.txt",  # 可选
    "detail_script": "/path/to/new_script.py"  # 可选
})

# 提示词调用
prompt_result = await mcp_client.get_prompt("update_knowledge", {
    "index": 0,
    "description": "更新后的知识描述",
    "detail": "更新后的知识内容",  # 可选
    "detail_file": "/path/to/new_file.txt",  # 可选
    "detail_script": "/path/to/new_script.py"  # 可选
})
```

## 知识脚本说明

如果为知识提供了detail_script字段，系统会尝试加载以索引命名的Python脚本（如1.py, 2.py等），并执行其中的detail()函数获取知识内容。

脚本示例：

```python
def detail():
    # 可以在这里实现动态生成知识内容的逻辑
    return "这是通过脚本动态生成的知识内容"
```

# local-knowledge

本地知识管理服务，用于保存和向大模型提供本地知识。

## 功能特点

- 支持多种文档格式（PDF、Word、Excel等）的解析和知识提取
- 提供本地知识库的检索和查询功能
- 集成与大语言模型的接口，实现知识增强
- 简单易用的命令行和API接口

## 安装方法

```bash
pip install local-knowledge
```

## 使用方法

### 命令行使用

```bash
# 启动服务
local-knowledge start

# 导入文档
local-knowledge import /path/to/document.pdf

# 查询知识
local-knowledge query "你的问题"
```

### API使用

```python
from local_knowledge import KnowledgeBase

# 初始化知识库
kb = KnowledgeBase()

# 导入文档
kb.import_document("/path/to/document.pdf")

# 查询知识
results = kb.query("你的问题")
```

## 依赖项

- langchain - 用于向量检索和知识管理
- fastapi - 提供API服务
- pymupdf, python-docx, openpyxl - 文档解析
- 其他依赖详见setup.py

## 许可证

MIT License
