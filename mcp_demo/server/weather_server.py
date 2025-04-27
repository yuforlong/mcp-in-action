#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 天气服务器

提供两个工具：
1. get_alerts: 获取美国某州的天气预警
2. get_forecast: 获取指定经纬度的天气预报
"""

from typing import Any, Dict, List, Optional
import asyncio
import httpx
from mcp.server.fastmcp import FastMCP

# 初始化 FastMCP 服务器
mcp = FastMCP("weather")

# 常量
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "mcp-weather-demo/1.0"

async def make_nws_request(url: str) -> Optional[Dict[str, Any]]:
    """
    向美国国家气象局 API 发送请求
    
    参数:
        url: API 请求的完整 URL
        
    返回:
        成功时返回 JSON 响应，失败时返回 None
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"API 请求错误: {e}")
            return None

def format_alert(feature: Dict[str, Any]) -> str:
    """
    将天气预警数据格式化为可读字符串
    
    参数:
        feature: 天气预警数据的特征对象
        
    返回:
        格式化后的预警信息
    """
    props = feature.get("properties", {})
    return f"""
事件: {props.get('event', '未知')}
区域: {props.get('areaDesc', '未知')}
严重程度: {props.get('severity', '未知')}
描述: {props.get('description', '无可用描述')}
指导意见: {props.get('instruction', '未提供具体指导意见')}
"""

@mcp.tool()
async def get_alerts(state: str) -> str:
    """
    获取美国某州的天气预警
    
    参数:
        state: 美国州的两字母代码 (例如 CA, NY)
        
    返回:
        格式化的预警信息字符串
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    
    if not data or "features" not in data:
        return "无法获取预警信息或未找到预警。"
    
    if not data["features"]:
        return f"当前 {state} 州没有活动预警。"
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """
    获取指定经纬度位置的天气预报
    
    参数:
        latitude: 位置的纬度
        longitude: 位置的经度
        
    返回:
        格式化的天气预报字符串
    """
    # 首先获取预报网格端点
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    
    if not points_data or "properties" not in points_data:
        return "无法获取该位置的预报数据。"
    
    # 从 points 响应中获取预报 URL
    try:
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await make_nws_request(forecast_url)
    except (KeyError, TypeError):
        return "无法获取预报端点。"
    
    if not forecast_data or "properties" not in forecast_data:
        return "无法获取详细预报。"
    
    # 将时段格式化为可读预报
    try:
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        
        for period in periods[:5]:  # 只显示接下来的 5 个时段
            forecast = f"""
{period.get('name', '未知时段')}:
温度: {period.get('temperature', '未知')}°{period.get('temperatureUnit', 'F')}
风况: {period.get('windSpeed', '未知')} {period.get('windDirection', '')}
预报: {period.get('detailedForecast', '无详细预报')}
"""
            forecasts.append(forecast)
        
        return "\n---\n".join(forecasts)
    except (KeyError, TypeError) as e:
        return f"解析预报数据时出错: {e}"

if __name__ == "__main__":
    print("正在启动 MCP 天气服务器...")
    print("提供工具: get_alerts, get_forecast")
    print("使用 Ctrl+C 停止服务器")
    
    # 初始化并运行服务器
    mcp.run(transport='stdio') 