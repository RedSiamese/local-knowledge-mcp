from typing import Annotated, List, Dict, Any, Optional
import os
import json
import asyncio

from mcp.server import Server
from mcp.server.stdio import stdio_server
# from mcp.server.http import serve_http
from mcp.types import (
    ErrorData, Tool, TextContent, Prompt, PromptArgument, 
    GetPromptResult, PromptMessage, INVALID_PARAMS, INTERNAL_ERROR
)
from mcp.shared.exceptions import McpError
from pydantic import BaseModel, Field

from .knowledge_service import KnowledgeService

# 定义请求模型
class AddKnowledgeModel(BaseModel):
    directory: Annotated[str, Field(description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）")]
    description: Annotated[str, Field(description="知识的描述，用于让大模型判断是否需要查询该条知识的细节")]
    detail: Annotated[Optional[str], Field(description="知识的具体内容", default=None)]
    detail_file: Annotated[Optional[str], Field(description="知识的具体内容的文件路径（相对于知识库文件目录的路径 或 绝对路径）", default=None)]
    detail_script: Annotated[Optional[str], Field(description="获取知识具体内容的脚本路径（相对于知识库文件目录的路径 或 绝对路径）", default=None)]

class UpdateKnowledgeModel(BaseModel):
    directory: Annotated[str, Field(description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）")]
    index: Annotated[int, Field(description="知识的序号（索引）")]
    description: Annotated[Optional[str], Field(description="知识的描述，用于让大模型判断是否需要查询该条知识的细节", default=None)]
    detail: Annotated[Optional[str], Field(description="知识的具体内容", default=None)]
    detail_file: Annotated[Optional[str], Field(description="知识的具体内容的文件路径（相对于知识库文件目录的路径 或 绝对路径）", default=None)]
    detail_script: Annotated[Optional[str], Field(description="获取知识具体内容的脚本路径（相对于知识库文件目录的路径 或 绝对路径）", default=None)]

class QueryKnowledgeModel(BaseModel):
    directory: Annotated[str, Field(description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）")]
    indices: Annotated[List[int], Field(description="要查询的知识序号列表")]

class ListKnowledgeModel(BaseModel):
    directory: Annotated[str, Field(description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）")]


async def serve():
    """运行本地知识MCP服务"""
    server = Server("local-knowledge")
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="list_knowledge",
                description="查询当前所有的知识描述，返回知识的序号和描述信息，用于判断是否需要查询具体知识细节。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                inputSchema=ListKnowledgeModel.model_json_schema(),
            ),
            Tool(
                name="query_knowledge",
                description="通过序号查询具体知识细节，返回指定序号的知识内容。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                inputSchema=QueryKnowledgeModel.model_json_schema(),
            ),
            Tool(
                name="add_knowledge",
                description="添加新的知识，可以提供知识描述、具体内容、内容文件路径或脚本路径。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                inputSchema=AddKnowledgeModel.model_json_schema(),
            ),
            Tool(
                name="update_knowledge",
                description="修改已有知识，根据序号更新知识的描述、内容、文件路径或脚本路径。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                inputSchema=UpdateKnowledgeModel.model_json_schema(),
            )
        ]
    
    @server.list_prompts()
    async def list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name="list_knowledge",
                description="查询当前所有的知识描述，返回知识的序号和描述信息，用于判断是否需要查询具体知识细节。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                arguments=[
                    PromptArgument(
                        name="directory", 
                        description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）", 
                        required=True
                    ),
                ],
            ),
            Prompt(
                name="query_knowledge",
                description="通过序号查询具体知识细节，获取完整的知识内容。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                arguments=[
                    PromptArgument(
                        name="directory", 
                        description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）", 
                        required=True
                    ),
                    PromptArgument(
                        name="indices", 
                        description="要查询的知识序号列表，例如 [0, 1, 2]", 
                        required=True
                    )
                ],
            ),
            Prompt(
                name="add_knowledge",
                description="添加新的知识，知识将按顺序添加到知识库中。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                arguments=[
                    PromptArgument(
                        name="directory", 
                        description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）", 
                        required=True
                    ),
                    PromptArgument(
                        name="description", 
                        description="知识的描述，用于让大模型判断是否需要查询该条知识的细节", 
                        required=True
                    ),
                    PromptArgument(
                        name="detail", 
                        description="知识的具体内容", 
                        required=False
                    ),
                    PromptArgument(
                        name="detail_file", 
                        description="知识的具体内容的文件路径（相对于知识库文件目录的路径 或 绝对路径）", 
                        required=False
                    ),
                    PromptArgument(
                        name="detail_script", 
                        description="获取知识具体内容的脚本路径（相对于知识库文件目录的路径 或 绝对路径）", 
                        required=False
                    ),
                ],
            ),
            Prompt(
                name="update_knowledge",
                description="修改已有知识，直接覆盖原有内容。需要传递知识库所在目录路径，如无特殊需求请传递当前工作目录（绝对路径）",
                arguments=[
                    PromptArgument(
                        name="directory", 
                        description="知识文件所在的目录路径，如无特殊需求请传递当前工作目录（绝对路径）", 
                        required=True
                    ),
                    PromptArgument(
                        name="index", 
                        description="知识的序号（索引）", 
                        required=True
                    ),
                    PromptArgument(
                        name="description", 
                        description="知识的描述，用于让大模型判断是否需要查询该条知识的细节", 
                        required=False
                    ),
                    PromptArgument(
                        name="detail", 
                        description="知识的具体内容", 
                        required=False
                    ),
                    PromptArgument(
                        name="detail_file", 
                        description="知识的具体内容的文件路径（相对于知识库文件目录的路径 或 绝对路径）", 
                        required=False
                    ),
                    PromptArgument(
                        name="detail_script", 
                        description="获取知识具体内容的脚本路径（相对于知识库文件目录的路径 或 绝对路径）", 
                        required=False
                    ),
                ],
            ),
        ]
        
    def get_knowledge_path(directory):
        """获取知识文件路径"""
        return os.path.join(directory, ".knowledge")
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        try:
            if name == "list_knowledge":
                try:
                    args = ListKnowledgeModel(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                knowledge_path = get_knowledge_path(args.directory)
                knowledge_service = KnowledgeService(knowledge_path)
                knowledge_descriptions = knowledge_service.query_all_knowledge()
                return [TextContent(
                    type="text", 
                    text=f"当前所有知识描述:\n{json.dumps(knowledge_descriptions, ensure_ascii=False, indent=2)}"
                )]
            
            elif name == "query_knowledge":
                try:
                    args = QueryKnowledgeModel(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                knowledge_path = get_knowledge_path(args.directory)
                knowledge_service = KnowledgeService(knowledge_path)
                details = knowledge_service.query_knowledge_detail(args.indices)
                result_text = "\n\n".join([f"知识 {idx}:\n{detail}" for idx, detail in zip(args.indices, details)])
                return [TextContent(type="text", text=result_text)]
            
            elif name == "add_knowledge":
                try:
                    args = AddKnowledgeModel(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                knowledge_path = get_knowledge_path(args.directory)
                knowledge_service = KnowledgeService(knowledge_path)
                result = knowledge_service.add_knowledge(
                    description=args.description,
                    detail=args.detail,
                    detail_file=args.detail_file,
                    detail_script=args.detail_script
                )
                
                return [TextContent(
                    type="text", 
                    text=f"添加知识成功，索引: {result['index']}"
                )]
            
            elif name == "update_knowledge":
                try:
                    args = UpdateKnowledgeModel(**arguments)
                except ValueError as e:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))
                
                knowledge_path = get_knowledge_path(args.directory)
                knowledge_service = KnowledgeService(knowledge_path)
                result = knowledge_service.update_knowledge(
                    index=args.index,
                    description=args.description,
                    detail=args.detail,
                    detail_file=args.detail_file,
                    detail_script=args.detail_script
                )
                
                status = "成功" if result["success"] else "失败"
                return [TextContent(
                    type="text", 
                    text=f"更新知识{status}"
                )]
            
            else:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=f"未知工具: {name}"))
        except McpError:
            raise
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"服务器错误: {str(e)}"))
    
    @server.get_prompt()
    async def get_prompt(name: str, arguments: dict | None) -> GetPromptResult:
        try:
            if name == "list_knowledge":
                if not arguments or "directory" not in arguments:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message="directory参数必须提供"))
                
                directory = arguments["directory"]
                knowledge_path = get_knowledge_path(directory)
                knowledge_service = KnowledgeService(knowledge_path)
                knowledge_descriptions = knowledge_service.query_all_knowledge()
                return GetPromptResult(
                    description="知识列表",
                    messages=[
                        PromptMessage(
                            role="user", 
                            content=TextContent(
                                type="text", 
                                text=f"知识列表:\n{json.dumps(knowledge_descriptions, ensure_ascii=False, indent=2)}"
                            )
                        )
                    ]
                )
            
            elif name == "query_knowledge":
                if not arguments or "indices" not in arguments or "directory" not in arguments:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message="indices和directory参数必须提供"))
                
                indices = arguments["indices"]
                if not isinstance(indices, list):
                    raise McpError(ErrorData(code=INVALID_PARAMS, message="indices必须是一个列表"))
                
                directory = arguments["directory"]
                knowledge_path = get_knowledge_path(directory)
                knowledge_service = KnowledgeService(knowledge_path)
                details = knowledge_service.query_knowledge_detail(indices)
                result_text = "\n\n".join([f"知识 {idx}:\n{detail}" for idx, detail in zip(indices, details)])
                
                return GetPromptResult(
                    description="知识详情",
                    messages=[
                        PromptMessage(
                            role="user", 
                            content=TextContent(type="text", text=result_text)
                        )
                    ]
                )
            
            elif name == "add_knowledge":
                if not arguments or "description" not in arguments or "directory" not in arguments:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message="description和directory参数必须提供"))
                
                directory = arguments["directory"]
                knowledge_path = get_knowledge_path(directory)
                knowledge_service = KnowledgeService(knowledge_path)
                result = knowledge_service.add_knowledge(
                    description=arguments["description"],
                    detail=arguments.get("detail"),
                    detail_file=arguments.get("detail_file"),
                    detail_script=arguments.get("detail_script")
                )
                
                return GetPromptResult(
                    description="添加知识",
                    messages=[
                        PromptMessage(
                            role="user", 
                            content=TextContent(
                                type="text", 
                                text=f"添加知识成功，索引: {result['index']}"
                            )
                        )
                    ]
                )
            
            elif name == "update_knowledge":
                if not arguments or "index" not in arguments or "directory" not in arguments:
                    raise McpError(ErrorData(code=INVALID_PARAMS, message="index和directory参数必须提供"))
                
                directory = arguments["directory"]
                knowledge_path = get_knowledge_path(directory)
                knowledge_service = KnowledgeService(knowledge_path)
                result = knowledge_service.update_knowledge(
                    index=arguments["index"],
                    description=arguments.get("description"),
                    detail=arguments.get("detail"),
                    detail_file=arguments.get("detail_file"),
                    detail_script=arguments.get("detail_script")
                )
                
                status = "成功" if result["success"] else "失败"
                return GetPromptResult(
                    description="更新知识",
                    messages=[
                        PromptMessage(
                            role="user", 
                            content=TextContent(type="text", text=f"更新知识{status}")
                        )
                    ]
                )
            
            else:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=f"未知提示: {name}"))
        except McpError:
            raise
        except Exception as e:
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"服务器错误: {str(e)}"))

    # 运行服务器
    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

