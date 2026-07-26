#!/usr/bin/env bash
# Watery Traders (OpenClaw Skill) · 环境检查脚本
# 用法：bash install.sh
# 作用：
#   1) 检查 python3 / adb 可用
#   2) pip install -r requirements.txt
#   3) 验证 mcp_server.py / ths/trader.py 可被 import
# 作用范围：
#   - 不启动任何服务（服务由 OpenClaw 通过 mcpServers 配置自动拉起）
#   - 不修改 ths/ 下任何代码
#   - 不修改 requirements.txt

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🌊 [Watery Traders] 环境检查启动..."
echo

# 1. Python 检查
echo "🐍 Step 1/4: Python 检查..."
PY_BIN=""
for candidate in python3.12 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PY_BIN="$(command -v "$candidate")"
    break
  fi
done

if [ -z "$PY_BIN" ]; then
  echo "   ❌ 未找到 python3，请先安装 Python 3.12+"
  exit 1
fi

PY_VER="$("$PY_BIN" -c 'import sys; print("%d.%d"%sys.version_info[:2])')"
PY_OK="$("$PY_BIN" -c 'import sys; print(1 if sys.version_info >= (3,12) else 0)')"

if [ "$PY_OK" != "1" ]; then
  echo "   ⚠️  当前 Python 版本: $PY_VER，建议 3.12+"
  read -rp "   是否继续？[y/N，默认 N]: " ans
  case "$ans" in
    y|Y) echo "   ⏭️  继续...";;
    *) echo "   🛑 已中止。请安装 Python 3.12+ 后重试。"; exit 1;;
  esac
else
  echo "   ✅ Python $PY_VER ($PY_BIN)"
fi

# 2. ADB 检查
echo
echo "📱 Step 2/4: ADB 检查..."
if ! command -v adb >/dev/null 2>&1; then
  echo "   ⚠️  adb 未安装"
  echo "   安装方式："
  echo "     - Ubuntu/Debian: sudo apt-get install adb"
  echo "     - macOS: brew install android-platform-tools"
  echo "     - Windows: https://developer.android.com/studio/releases/platform-tools"
  read -rp "   是否继续（不安装 ADB）？[y/N，默认 N]: " ans
  case "$ans" in
    y|Y) echo "   ⏭️  继续（仅完成依赖安装，不验证设备连接）";;
    *) echo "   🛑 已中止。"; exit 1;;
  esac
else
  ADB_VER="$(adb version | head -1)"
  echo "   ✅ $ADB_VER"
  # 顺手探测设备
  DEVICES="$(adb devices 2>/dev/null | tail -n +2 | grep -v '^$' || true)"
  if [ -n "$DEVICES" ]; then
    echo "   📡 已连接设备："
    echo "$DEVICES" | sed 's/^/      /'
  else
    echo "   ⚠️  未检测到设备，请确认 USB 调试或 WiFi 调试已开启"
  fi
fi

# 3. 依赖安装
echo
echo "📦 Step 3/4: 安装 Python 依赖..."
"$PY_BIN" -m pip install -r requirements.txt

# 4. 模块 import 烟雾测试
echo
echo "🔍 Step 4/4: 模块可导入性检查..."
"$PY_BIN" -c "import ths.config; print('   ✅ ths.config 可导入')"
"$PY_BIN" -c "import ths.trader; print('   ✅ ths.trader 可导入')"
"$PY_BIN" -c "import ths.app; print('   ✅ ths.app 可导入')"
"$PY_BIN" -c "import mcp_server; print('   ✅ mcp_server 可导入')"

echo
echo "============================================"
echo "✅ 环境检查通过！"
echo "============================================"
echo
echo "📂 项目位置: $SCRIPT_DIR"
echo
echo "📌 下一步："
echo "   1. 让 OpenClaw 加载本 skill（自动通过 mcpServers 启动 mcp_server.py）"
echo "   2. 验证 MCP 服务:"
echo "        curl http://localhost:19090/health"
echo "   3. 在飞书 DM 给 agent 发: \"看看账户\" 或 \"切换到模拟\""
echo
echo "🛡️  默认模式：simulate（模拟交易），切到 real 前 agent 会二次确认"
echo