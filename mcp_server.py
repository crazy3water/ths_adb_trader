#!/usr/bin/env python3
"""
Watery Traders MCP Server
基于 Model Context Protocol 的交易服务器

使用方式:
    python mcp_server.py

或与 Claude Desktop 配合使用:
    1. 启动服务: python mcp_server.py
    2. 在 Claude Desktop 配置中添加 MCP 服务器
"""

import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from ths.trader import ThsTrader
from ths.config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP 协议常量
SERVER_NAME = "watery-traders"
SERVER_VERSION = "1.0.0"

# 初始化
app = FastAPI(title="Watery Traders MCP Server")

# 全局交易对象
trader: Optional[ThsTrader] = None


def init_trader() -> bool:
    """初始化交易对象"""
    global trader
    try:
        trader = ThsTrader()
        logger.info("✅ 交易模块初始化成功")
        return True
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        return False


@app.on_event("startup")
async def startup():
    """启动时初始化"""
    init_trader()


@app.get("/")
async def root():
    """MCP 服务信息"""
    return {
        "name": SERVER_NAME,
        "version": SERVER_VERSION,
        "description": "同花顺自动化交易 MCP 服务"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "ok" if trader and trader.d else "error",
        "device_connected": trader is not None and trader.d is not None
    }


# ==================== MCP Tools ====================

def get_tools() -> List[Dict[str, Any]]:
    """返回所有可用的工具定义"""
    return [
        {
            "name": "get_account",
            "description": "获取账户概览信息，包括总资产、浮动盈亏、市值等",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "get_positions",
            "description": "获取当前所有持仓股票列表",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "get_position_detail",
            "description": "获取指定持仓的详细信息",
            "inputSchema": {
                "type": "object",
                "properties": {"index": {"type": "integer", "description": "持仓索引，从0开始"}},
                "required": ["index"]
            }
        },
        {
            "name": "buy_stock",
            "description": "买入股票",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "股票代码，如 600519"},
                    "price": {"type": "string", "description": "买入价格"},
                    "quantity": {"type": "string", "description": "买入数量"},
                    "mode": {"type": "string", "description": "交易模式: simulate(模拟) 或 real(实盘)"}
                },
                "required": ["code", "price", "quantity"]
            }
        },
        {
            "name": "sell_stock",
            "description": "卖出股票",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "股票代码"},
                    "price": {"type": "string", "description": "卖出价格"},
                    "quantity": {"type": "string", "description": "卖出数量"},
                    "mode": {"type": "string", "description": "交易模式"}
                },
                "required": ["code", "price", "quantity"]
            }
        },
        {
            "name": "get_orders",
            "description": "获取委托买卖记录",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "order_type": {"type": "string", "description": "委托类型: today(当日) 或 history(历史)"}
                },
                "required": []
            }
        },
        {
            "name": "cancel_order",
            "description": "撤销指定委托",
            "inputSchema": {
                "type": "object",
                "properties": {"index": {"type": "integer", "description": "要撤销的委托索引，从0开始"}},
                "required": ["index"]
            }
        },
        {
            "name": "set_trade_mode",
            "description": "切换交易模式",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "description": "交易模式: simulate(模拟) 或 real(实盘)"}
                },
                "required": ["mode"]
            }
        },
        {
            "name": "get_trade_mode",
            "description": "获取当前交易模式",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "screenshot",
            "description": "截取当前手机屏幕",
            "inputSchema": {
                "type": "object",
                "properties": {"name": {"type": "string", "description": "截图文件名（可选）"}},
                "required": []
            }
        },
        {
            "name": "open_ths",
            "description": "打开同花顺APP",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "close_ths",
            "description": "关闭同花顺APP",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "get_device_info",
            "description": "获取已连接设备的信息",
            "inputSchema": {"type": "object", "properties": {}, "required": []}
        },
        {
            "name": "back",
            "description": "执行返回操作",
            "inputSchema": {
                "type": "object",
                "properties": {"times": {"type": "integer", "description": "返回次数", "default": 1}},
                "required": []
            }
        }
    ]


# ==================== MCP 路由 ====================

@app.get("/mcp/tools")
async def list_tools():
    """列出所有可用工具"""
    return {"tools": get_tools()}


@app.post("/mcp/tools/call")
async def call_tool(request: Dict[str, Any]):
    """调用指定工具"""
    if not trader or not trader.d:
        raise HTTPException(status_code=503, detail="设备未连接")
    
    tool_name = request.get("name")
    arguments = request.get("arguments", {})
    
    logger.info(f"调用工具: {tool_name}, 参数: {arguments}")
    
    try:
        if tool_name == "get_account":
            result = trader.get_account_summary()
        elif tool_name == "get_positions":
            result = trader.get_positions()
        elif tool_name == "get_position_detail":
            result = trader.get_position_detail(arguments.get("index", 0))
        elif tool_name == "buy_stock":
            result = trader.buy(arguments.get("code"), arguments.get("price"), arguments.get("quantity"), arguments.get("mode"))
        elif tool_name == "sell_stock":
            result = trader.sell(arguments.get("code"), arguments.get("price"), arguments.get("quantity"), arguments.get("mode"))
        elif tool_name == "get_orders":
            result = trader.get_orders(arguments.get("order_type", "today"))
        elif tool_name == "cancel_order":
            result = trader.cancel_order(arguments.get("index", 0))
        elif tool_name == "set_trade_mode":
            success = trader.set_trade_mode(arguments.get("mode", "simulate"))
            result = {"success": success, "mode": arguments.get("mode")}
        elif tool_name == "get_trade_mode":
            result = {"success": True, "mode": trader.trade_mode}
        elif tool_name == "screenshot":
            path = trader.screenshot(arguments.get("name"))
            result = {"success": True, "path": path}
        elif tool_name == "open_ths":
            result = trader.open_app()
        elif tool_name == "close_ths":
            result = trader.close_app()
        elif tool_name == "get_device_info":
            info = trader.d.info
            result = {"success": True, "info": {"model": info.get('model'), "android": info.get('version')}}
        elif tool_name == "back":
            result = {"success": trader.back(arguments.get("times", 1)), "times": arguments.get("times", 1)}
        else:
            raise HTTPException(status_code=400, detail=f"未知工具: {tool_name}")
        
        return {"success": True, "result": result}
        
    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        return {"success": False, "error": str(e)}


# ==================== 启动入口 ====================

if __name__ == "__main__":
    print("=" * 50)
    print("🌊 Watery Traders - MCP Server")
    print(f"版本: {SERVER_VERSION}")
    print(f"设备: {config.DEVICE_SERIAL}")
    print("=" * 50)
    print("MCP 端点:")
    print("  - GET  /mcp/tools         # 列出工具")
    print("  - POST /mcp/tools/call    # 调用工具")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=19090)
