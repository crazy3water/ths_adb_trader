# app.py (修正版本)
from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import base64
import logging
from datetime import datetime
from trader import ThsTrader
from config import config
import uvicorn
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="同花顺交易API",
    description="通过uiautomator2操控同花顺进行自动化交易",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化交易对象
try:
    trader = ThsTrader()
    logger.info("✅ 交易模块初始化成功")
except Exception as e:
    logger.error(f"❌ 初始化失败: {e}")
    trader = None


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "同花顺交易API",
        "version": "2.0.0",
        "environment": "watery_traders",
        "python_version": "3.12",
        "device": config.DEVICE_SERIAL,
        "trade_mode": trader.trade_mode if trader else "unknown",
        "status": "connected" if trader and trader.d else "disconnected"
    }


# ==================== 设备管理 ====================

@app.get("/device/info")
async def device_info():
    """获取设备信息"""
    if not trader or not trader.d:
        raise HTTPException(status_code=500, detail="设备未连接")

    info = trader.d.info
    return {
        "success": True,
        "info": {
            "product": info.get('productName'),
            "model": info.get('model'),
            "android": info.get('version'),
            "screen": f"{info.get('displayWidth')}x{info.get('displayHeight')}",
            "battery": info.get('battery', {}).get('level'),
            "trade_mode": trader.trade_mode,
            "activity": trader.get_current_activity()
        }
    }


@app.post("/device/reconnect")
async def reconnect():
    """重新连接设备"""
    global trader
    try:
        trader = ThsTrader()
        return {"success": True, "message": "重新连接成功", "trade_mode": trader.trade_mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 后退导航 ====================

@app.post("/device/back")
async def back(
        times: int = Query(1, description="后退次数", ge=1, le=10)
):
    """后退操作"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    success = trader.back(times)
    return {
        "success": success,
        "times": times,
        "message": f"已后退{times}次"
    }


@app.post("/device/back_to_home")
async def back_to_home():
    """返回手机首页"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    success = trader.back_to_home()
    return {
        "success": success,
        "message": "已返回首页" if success else "返回首页失败"
    }


@app.post("/ths/back_to_trade_main")
async def back_to_trade_main():
    """返回交易主页面"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    success = trader.back_to_trade_main()
    return {
        "success": success,
        "message": "已返回交易主页面" if success else "返回交易主页面失败"
    }


# ==================== 应用控制 ====================

@app.post("/ths/open")
async def open_ths():
    """打开同花顺"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")
    return trader.open_app()


@app.post("/ths/close")
async def close_ths():
    """关闭同花顺"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")
    return trader.close_app()


@app.post("/ths/restart")
async def restart_ths():
    """重启同花顺"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")
    return trader.restart_app()


# ==================== 交易模式 ====================

@app.post("/ths/set_mode")
async def set_trade_mode(
        mode: str = Query(..., description="交易模式: simulate(模拟) 或 real(实盘A股)")
):
    """设置交易模式"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    if mode not in ["simulate", "real"]:
        raise HTTPException(status_code=400, detail="mode必须是simulate或real")

    success = trader.set_trade_mode(mode)
    return {
        "success": success,
        "mode": trader.trade_mode,
        "message": f"已切换到{'模拟交易' if mode == 'simulate' else '实盘A股'}"
    }


@app.get("/ths/mode")
async def get_trade_mode():
    """获取当前交易模式"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    return {
        "success": True,
        "mode": trader.trade_mode,
        "mode_text": "模拟交易" if trader.trade_mode == "simulate" else "实盘A股"
    }


# ==================== 账户信息 ====================

@app.get("/ths/account")
async def get_account_summary():
    """获取账户概览（总资产、浮动盈亏、总市值、当日盈亏）"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    result = trader.get_account_summary()
    return result


# ==================== 持仓管理 ====================

@app.get("/ths/positions")
async def get_positions():
    """获取持仓列表"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    result = trader.get_positions()
    return result


# 修正：使用 Path 而不是 Query  for 路径参数
@app.get("/ths/position/{index}")
async def get_position_detail(
        index: int = Path(..., description="持仓索引", ge=0)
):
    """获取单个持仓详情"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    result = trader.get_position_detail(index)
    return result


# ==================== 交易操作 ====================

@app.post("/ths/buy")
async def buy_stock(
        code: str = Query(..., description="股票代码"),
        price: str = Query(..., description="买入价格"),
        quantity: str = Query(..., description="买入数量"),
        mode: Optional[str] = Query(None, description="交易模式: simulate或real，不填使用当前模式")
):
    """买入股票"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    if mode and mode not in ["simulate", "real"]:
        raise HTTPException(status_code=400, detail="mode必须是simulate或real")

    return trader.buy(code, price, quantity, mode)


@app.post("/ths/sell")
async def sell_stock(
        code: str = Query(..., description="股票代码"),
        price: str = Query(..., description="卖出价格"),
        quantity: str = Query(..., description="卖出数量"),
        mode: Optional[str] = Query(None, description="交易模式: simulate或real，不填使用当前模式")
):
    """卖出股票"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    if mode and mode not in ["simulate", "real"]:
        raise HTTPException(status_code=400, detail="mode必须是simulate或real")

    return trader.sell(code, price, quantity, mode)


# ==================== 委托管理 ====================

@app.get("/ths/orders")
async def get_orders(
        type: str = Query("today", description="委托类型: today(当日) 或 history(历史)")
):
    """获取委托记录"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    if type not in ["today", "history"]:
        raise HTTPException(status_code=400, detail="type必须是today或history")

    result = trader.get_orders(type)
    return result


@app.post("/ths/cancel")
async def cancel_order(
        index: int = Query(0, description="要撤销的委托索引", ge=0)
):
    """撤单"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    result = trader.cancel_order(index)
    return result


# ==================== 截图 ====================

@app.post("/ths/screenshot")
async def take_screenshot():
    """截图"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    path = trader.screenshot()

    # 读取图片转为base64
    with open(path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    return {
        "success": True,
        "path": path,
        "image_base64": img_base64[:200] + "..."  # 预览
    }


@app.get("/screenshots/{filename}")
async def get_screenshot(
        filename: str = Path(..., description="截图文件名")
):
    """获取截图文件"""
    file_path = config.SCREENSHOT_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "文件不存在"}


# ==================== 调试工具 ====================

@app.get("/ths/buttons")
async def find_buttons():
    """查找所有按钮（调试用）"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    buttons = trader.find_buttons()
    return {
        "success": True,
        "count": len(buttons),
        "buttons": buttons[:20]  # 只返回前20个
    }


@app.post("/ths/dump_ui")
async def dump_ui():
    """导出UI结构"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    path = trader.dump_ui()
    return {
        "success": True,
        "path": path
    }


@app.post("/ths/click")
async def click_button(
        text: str = Query(..., description="按钮文字"),
        timeout: int = Query(5, description="超时时间")
):
    """点击指定文字的按钮"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    success = trader.click_by_text(text, timeout)
    return {"success": success, "text": text}


@app.get("/ths/activity")
async def get_activity():
    """获取当前Activity"""
    if not trader:
        raise HTTPException(status_code=500, detail="设备未连接")

    activity = trader.get_current_activity()
    return {
        "success": True,
        "activity": activity
    }


if __name__ == "__main__":
    print("=" * 60)
    print("🌊 Watery Traders - 同花顺交易API v2.0")
    print("=" * 60)
    print(f"环境: watery_traders (Python 3.12)")
    print(f"设备: {config.DEVICE_SERIAL}")
    print(f"交易模式: {trader.trade_mode if trader else 'unknown'}")
    print(f"截图目录: {config.SCREENSHOT_DIR}")
    print("=" * 60)
    print("后退功能:")
    print("  - POST /device/back?times=1    # 后退指定次数")
    print("  - POST /device/back_to_home     # 返回手机首页")
    print("  - POST /ths/back_to_trade_main  # 返回交易主页面")
    print("=" * 60)
    print("交易模式:")
    print("  - POST /ths/set_mode?mode=simulate  # 切换到模拟交易")
    print("  - POST /ths/set_mode?mode=real      # 切换到实盘A股")
    print("  - GET /ths/mode                      # 获取当前模式")
    print("=" * 60)
    print("账户持仓:")
    print("  - GET /ths/account        # 获取账户概览")
    print("  - GET /ths/positions       # 获取持仓列表")
    print("  - GET /ths/position/0      # 获取第1个持仓详情")
    print("=" * 60)
    print("交易操作:")
    print("  - POST /ths/buy?code=600519&price=1500&quantity=100")
    print("  - POST /ths/sell?code=600519&price=1600&quantity=100")
    print("=" * 60)
    print("委托管理:")
    print("  - GET /ths/orders?type=today    # 当日委托")
    print("  - POST /ths/cancel?index=0       # 撤销第1个委托")
    print("=" * 60)
    print("调试工具:")
    print("  - GET /ths/buttons        # 查找所有按钮")
    print("  - POST /ths/dump_ui        # 导出UI结构")
    print("  - POST /ths/screenshot      # 截图")
    print("=" * 60)
    print("API文档: http://localhost:8000/docs")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)