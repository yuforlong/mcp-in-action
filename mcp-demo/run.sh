#!/bin/bash
# 运行 MCP 演示程序的脚本

# 确保脚本可执行
# chmod +x run.sh

# 设置颜色
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}   MCP 演示程序启动脚本   ${NC}"
echo -e "${BLUE}=====================================${NC}"
echo

# 检查 Python 版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}检测到 Python 版本:${NC} ${python_version}"

# 检查 Python 版本是否符合要求
required_version="3.10.0"
if [[ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]]; then
    echo -e "${RED}错误: 需要 Python 3.10.0 或更高版本${NC}"
    exit 1
fi

# 检查虚拟环境
if [[ ! -d "venv_mcp-demo" ]]; then
    echo -e "${BLUE}创建虚拟环境...${NC}"
    python3 -m venv venv_mcp-demo
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}创建虚拟环境失败${NC}"
        exit 1
    fi
    echo -e "${GREEN}虚拟环境创建成功${NC}"
fi

# 激活虚拟环境
echo -e "${BLUE}激活虚拟环境...${NC}"
source venv_mcp-demo/bin/activate
if [[ $? -ne 0 ]]; then
    echo -e "${RED}激活虚拟环境失败${NC}"
    exit 1
fi

# 安装依赖
echo -e "${BLUE}检查并安装依赖...${NC}"
pip install -r requirements.txt
if [[ $? -ne 0 ]]; then
    echo -e "${RED}安装依赖失败${NC}"
    exit 1
fi
echo -e "${GREEN}依赖安装完成${NC}"

# 检查和风天气 API 密钥
if [[ -z "${QWEATHER_API_KEY}" ]]; then
    echo -e "${YELLOW}警告: 未设置 QWEATHER_API_KEY 环境变量${NC}"
    echo -e "${YELLOW}您需要设置 QWEATHER_API_KEY 才能使用天气服务${NC}"
    echo -e "${YELLOW}请执行以下命令设置 API 密钥:${NC}"
    echo -e "${GREEN}export QWEATHER_API_KEY=\"你的API密钥\"${NC}"
    
    # 询问是否继续
    read -p "是否仍要继续启动程序? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}退出程序${NC}"
        deactivate
        exit 0
    fi
fi

# 运行客户端
echo -e "${BLUE}启动 MCP 客户端...${NC}"
echo -e "${BLUE}客户端将自动启动并连接到服务器${NC}"
echo -e "${BLUE}=====================================${NC}"
python client/mcp_client.py

# 退出虚拟环境
deactivate 