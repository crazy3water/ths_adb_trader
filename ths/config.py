# config.py
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent


class Config:
    # 设备配置
    DEVICE_SERIAL = "SM02G4061994156"  # 当前连接的手机

    # 同花顺配置
    THS_PACKAGE = "com.hexin.plat.android"

    # 截图配置
    SCREENSHOT_DIR = BASE_DIR / "screenshots"

    # 超时配置（秒）
    DEFAULT_TIMEOUT = 10
    PAGE_LOAD_TIMEOUT = 3

    # 创建目录
    SCREENSHOT_DIR.mkdir(exist_ok=True)


config = Config()