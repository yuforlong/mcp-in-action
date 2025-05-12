#!/bin/bash

# 设置环境变量
export MCP_SERVER_HOST="http://localhost:8080/sse"
export LLM_API_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export LLM_MODEL="qwen-max"
export LLM_API_KEY=""  # 此处需要填入有效的API密钥
export LOG_LEVEL="INFO"  # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL

# 确保脚本可以接收命令行参数
if [ $# -lt 1 ]; then
    echo "用法: $0 <命令> [参数]"
    echo "可用命令:"
    echo "  import <文件路径>    - 导入文件到知识库"
    echo "  search <查询文本>    - 搜索知识库"
    echo "  chat <问题>          - 基于知识库进行对话"
    echo "  pdf2md <PDF文件>     - 将PDF转换为Markdown"
    exit 1
fi

COMMAND=$1
shift

# 设置Python虚拟环境（如果存在）
if [ -d "../env-mcp-rag" ]; then
    echo "激活虚拟环境..."
    source ../env-mcp-rag/bin/activate
fi

# 根据命令执行相应操作
case $COMMAND in
    import)
        if [ $# -lt 1 ]; then
            echo "错误: 请提供要导入的文件路径"
            exit 1
        fi
        FILE_PATH=$1
        echo "正在导入文件: $FILE_PATH"
        python knowledge_manager.py import "$FILE_PATH"
        ;;
    search)
        if [ $# -lt 1 ]; then
            echo "错误: 请提供搜索查询"
            exit 1
        fi
        QUERY="$*"
        echo "正在搜索: $QUERY"
        python knowledge_manager.py search "$QUERY"
        ;;
    chat)
        if [ $# -lt 1 ]; then
            echo "错误: 请提供问题"
            exit 1
        fi
        QUERY="$*"
        echo "对话: $QUERY"
        python knowledge_manager.py chat "$QUERY"
        ;;
    pdf2md)
        if [ $# -lt 1 ]; then
            echo "错误: 请提供PDF文件路径"
            exit 1
        fi
        PDF_PATH=$1
        OUTPUT_PATH=${2:-""}
        if [ -z "$OUTPUT_PATH" ]; then
            echo "将PDF转换为Markdown: $PDF_PATH"
            python import_file.py "$PDF_PATH"
        else
            echo "将PDF转换为Markdown: $PDF_PATH -> $OUTPUT_PATH"
            python import_file.py "$PDF_PATH" "$OUTPUT_PATH"
        fi
        ;;
    *)
        echo "错误: 未知命令 '$COMMAND'"
        echo "可用命令: import, search, chat, pdf2md"
        exit 1
        ;;
esac

# 如果使用了虚拟环境，可以在此处取消激活
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

exit 0 