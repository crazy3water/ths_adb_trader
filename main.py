#!/usr/bin/env python3
"""
Watery Traders - 主入口文件
用于启动 REST API 服务和 MCP 服务

使用方法:
    python main.py              # 启动 REST API (端口 8000)
    python main.py --mcp       # 启动 MCP 服务 (端口 19090)
    python main.py --both      # 同时启动两个服务
"""

import argparse
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def start_api_server():
    """启动 REST API 服务"""
    import uvicorn
    from ths.app import app
    
    print("=" * 60)
    print("🌊 Watery Traders - REST API Server")
    print("=" * 60)
    print("服务地址: http://localhost:8000")
    print("API文档:  http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)


def start_mcp_server():
    """启动 MCP 服务"""
    import uvicorn
    from mcp_server import app as mcp_app
    from ths.config import config
    
    print("=" * 60)
    print("🌊 Watery Traders - MCP Server")
    print("=" * 60)
    print(f"服务地址: http://localhost:19090")
    print(f"设备:     {config.DEVICE_SERIAL}")
    print("=" * 60)
    print("MCP 端点:")
    print("  - GET  /mcp/tools         # 列出工具")
    print("  - POST /mcp/tools/call    # 调用工具")
    print("=" * 60)
    
    uvicorn.run(mcp_app, host="0.0.0.0", port=19090)


def start_both():
    """同时启动两个服务"""
    import multiprocessing
    
    def run_api():
        start_api_server()
    
    def run_mcp():
        start_mcp_server()
    
    print("=" * 60)
    print("🌊 Watery Traders - 双服务启动")
    print("=" * 60)
    print("REST API: http://localhost:8000")
    print("MCP:      http://localhost:19090")
    print("=" * 60)
    
    api_process = multiprocessing.Process(target=run_api, name="api-server")
    mcp_process = multiprocessing.Process(target=run_mcp, name="mcp-server")
    
    api_process.start()
    mcp_process.start()
    
    try:
        api_process.join()
        mcp_process.join()
    except KeyboardInterrupt:
        print("\n🛑 停止服务...")
        api_process.terminate()
        mcp_process.terminate()
        api_process.join()
        mcp_process.join()
        print("✅ 服务已停止")


def main():
    parser = argparse.ArgumentParser(description="Watery Traders 启动器")
    parser.add_argument(
        "--mcp", 
        action="store_true", 
        help="启动 MCP 服务 (端口 19090)"
    )
    parser.add_argument(
        "--both", 
        action="store_true", 
        help="同时启动 REST API 和 MCP 服务"
    )
    
    args = parser.parse_args()
    
    if args.mcp:
        start_mcp_server()
    elif args.both:
        start_both()
    else:
        start_api_server()


if __name__ == "__main__":
    main()
