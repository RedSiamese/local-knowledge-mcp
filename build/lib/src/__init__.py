"""
本地知识管理模块
提供知识的存储、查询和管理功能

主要组件:
- KnowledgeService: 知识存储和管理服务
- serve: 启动标准输入输出模式的MCP服务
- run_server: 启动HTTP服务器
"""

"""
本地知识服务入口点
允许直接使用 'python -m local_knowledge' 运行
"""

import os
import sys
import argparse
import asyncio
from .mcp_service import serve

def main():
    """解析命令行参数并启动服务"""
    parser = argparse.ArgumentParser(description='本地知识管理服务')
    # parser.add_argument('--port', type=int, default=8787, help='服务端口号 (默认: 8787)')
    parser.add_argument('--file', type=str, default='knowledge.json', help='知识文件路径 (默认: knowledge.json)')
    # parser.add_argument('--stdio', action='store_true', help='使用标准输入输出模式')
    
    args = parser.parse_args()
    
    # print(f"启动本地知识服务...")
    # print(f"- 端口: {args.port if not args.stdio else 'N/A (stdio模式)'}")
    # print(f"- 知识文件: {args.file}")
    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动服务时发生错误: {str(e)}")
        sys.exit(1)
