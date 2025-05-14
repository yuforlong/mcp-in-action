"""
MCP客户端应用程序入口
功能：基于Milvus向量数据库的MCP（模型上下文协议）客户端主程序
作用：提供命令行界面，用于构建知识库和查询知识库
主要功能：
1. 知识库构建：从文件或文本中提取内容，切段后存储到Milvus向量数据库
2. FAQ提取：从文本中自动提取常见问题答案对
3. 知识检索：通过提问检索相关知识，利用RAG技术生成回答
"""
import os
import sys
import asyncio
import argparse
from typing import Dict, List, Any, Optional
from loguru import logger

from app.knowledge_builder import KnowledgeBuilder
from app.knowledge_retriever import KnowledgeRetriever
from app.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, MAX_SEARCH_RESULTS

async def build_knowledge_base(args):
    """
    构建知识库：从文件或文本内容构建知识库
    参数：
        args: 命令行参数，包含文件路径/文本内容、元数据和分块参数
    """
    builder = KnowledgeBuilder(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap
    )
    
    try:
        metadata = {}
        if args.title:
            metadata["title"] = args.title
        if args.author:
            metadata["author"] = args.author
        if args.tags:
            metadata["tags"] = args.tags.split(",")
            
        # 从文件或文本构建知识库
        if args.file:
            logger.info(f"Building knowledge base from file: {args.file}")
            result = await builder.build_from_file(
                file_path=args.file,
                metadata=metadata,
                extract_faq=not args.no_faq
            )
        elif args.text:
            logger.info("Building knowledge base from provided text")
            result = await builder.build_from_text(
                text=args.text,
                metadata=metadata,
                extract_faq=not args.no_faq
            )
        else:
            logger.error("Either --file or --text must be provided")
            return
            
        # 打印结果
        logger.info(f"Stored {result['stored_chunks']}/{result['total_chunks']} chunks to knowledge base")
        if not args.no_faq:
            logger.info(f"Extracted and stored {result['extracted_faqs']} FAQs")
            
        # 正确关闭MCP客户端连接
        await builder.mcp_client.close()
            
    except Exception as e:
        logger.error(f"Error building knowledge base: {e}")
        # 确保即使在异常情况下客户端也能关闭
        try:
            await builder.mcp_client.close()
        except Exception as close_error:
            logger.error(f"Error closing MCP client: {close_error}")
        sys.exit(1)
        
async def query_knowledge_base(args):
    """
    查询知识库：根据用户提问检索知识并生成回答
    参数：
        args: 命令行参数，包含问题和最大检索结果数量
    """
    retriever = KnowledgeRetriever(
        max_search_results=args.max_results
    )
    
    try:
        logger.info(f"Querying knowledge base with question: {args.question}")
        answer = await retriever.query(args.question)
        
        # 打印答案
        print("\n" + "=" * 80)
        print("问题:", args.question)
        print("-" * 80)
        print("回答:", answer)
        print("=" * 80)
        
        # 正确关闭MCP客户端连接
        await retriever.mcp_client.close()
        
    except Exception as e:
        logger.error(f"Error querying knowledge base: {e}")
        # 确保即使在异常情况下客户端也能关闭
        try:
            await retriever.mcp_client.close()
        except Exception as close_error:
            logger.error(f"Error closing MCP client: {close_error}")
        sys.exit(1)

def print_usage_guide():
    """打印应用程序的详细使用指南"""
    print("\n" + "=" * 80)
    print("Milvus MCP Client 使用指南")
    print("=" * 80)
    
    print("\n构建知识库:")
    print("-" * 80)
    print("从文件构建知识库:")
    print("  python -m app.main build --file <文件路径>")
    print("\n从文件构建知识库并设置元数据:")
    print("  python -m app.main build --file <文件路径> --title \"文档标题\" --author \"作者\" --tags \"标签1,标签2\"")
    print("\n使用自定义分块大小:")
    print(f"  python -m app.main build --file <文件路径> --chunk-size {DEFAULT_CHUNK_SIZE*2} --chunk-overlap {DEFAULT_CHUNK_OVERLAP*2}")
    print("\n从文本构建知识库:")
    print("  python -m app.main build --text \"这是要处理的文本内容\" --title \"内容标题\"")
    print("\n不提取FAQ:")
    print("  python -m app.main build --file <文件路径> --no-faq")
    
    print("\n查询知识库:")
    print("-" * 80)
    print("基本查询:")
    print("  python -m app.main query --question \"您的问题\"")
    print("\n指定最大结果数:")
    print(f"  python -m app.main query --question \"您的问题\" --max-results {MAX_SEARCH_RESULTS*2}")
    
    print("\n" + "=" * 80)

def main():
    """
    应用程序入口点：解析命令行参数并执行相应的命令
    支持的命令：build(构建知识库)、query(查询知识库)、help(显示帮助)
    """
    parser = argparse.ArgumentParser(description="Milvus MCP Client for knowledge base management and querying")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 构建知识库命令
    build_parser = subparsers.add_parser("build", help="Build knowledge base from file or text")
    build_parser.add_argument("--file", type=str, help="Path to the file to process")
    build_parser.add_argument("--text", type=str, help="Text content to process")
    build_parser.add_argument("--title", type=str, help="Title of the document")
    build_parser.add_argument("--author", type=str, help="Author of the document")
    build_parser.add_argument("--tags", type=str, help="Comma-separated tags for the document")
    build_parser.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE, help="Size of text chunks")
    build_parser.add_argument("--chunk-overlap", type=int, default=DEFAULT_CHUNK_OVERLAP, help="Overlap between chunks")
    build_parser.add_argument("--no-faq", action="store_true", help="Disable FAQ extraction")
    
    # 查询知识库命令
    query_parser = subparsers.add_parser("query", help="Query the knowledge base")
    query_parser.add_argument("--question", type=str, required=True, help="Question to ask")
    query_parser.add_argument("--max-results", type=int, default=MAX_SEARCH_RESULTS, help="Maximum number of search results")
    
    # 帮助命令
    help_parser = subparsers.add_parser("help", help="Show detailed usage guide")
    
    # 解析参数
    args = parser.parse_args()
    
    # 执行命令
    if args.command == "build":
        asyncio.run(build_knowledge_base(args))
    elif args.command == "query":
        asyncio.run(query_knowledge_base(args))
    elif args.command == "help":
        print_usage_guide()
    else:
        print_usage_guide()
        
if __name__ == "__main__":
    main() 