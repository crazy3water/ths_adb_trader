---
name: watery-traders
description: 同花顺自动化交易系统。通过 uiautomator2 控制安卓手机上的同花顺 APP 执行模拟或实盘交易。触发词"交易/下单/买卖/账户/持仓/撤单"。本 skill 不做选股、不预测股价、不提供策略推荐；它只负责执行用户明确给出的交易动作。
trigger_keywords: ["交易", "下单", "买卖", "买入", "卖出", "账户", "持仓", "委托", "撤单", "同花顺", "实盘", "模拟交易"]
---

# 🌊 Watery Traders · 同花顺自动化交易（OpenClaw Skill）

> [!WARNING]
> **真实交易风险**：本 skill 通过手机上的同花顺 APP 直接下单，可执行**实盘交易**（真实资金）或**模拟交易**（模拟资金）。  
> 任何"买入/卖出/撤单"动作都会真的进入同花顺账户。Agent 必须默认 **simulate（模拟）模式**，未明确指令"切换实盘"前，不得把 `trade_mode` 改成 `real`。

> [!CAUTION]
> **运行前必读**：
> - 物理依赖：安卓手机 + 同花顺 APP 已登录 + USB/WiFi ADB 已连接
> - 联网依赖：手机和电脑在同一局域网（WiFi 调试模式）或 USB 已授权
> - 数字资源：每次买卖约 1 分钟，单次操作不可中断
> - 本 skill **不**做基本面/技术面分析；不做选股；不预测股价；不提供策略

---

## 🧩 工具调用协议

### 1. 启动 MCP 服务（首次安装后）

skill 启动时由 OpenClaw 自动执行 `mcpServers` 块中的命令，无需手动启动。

注意：本 skill 的源代码仓库名为 **`ths_adb_trader`**（不是 `watery-traders`）。  
`git clone` 下来的默认目录是 `ths_adb_trader/`，可根据需要重命名到任意位置（例如 `~/app/watery_traders/`、`~/.openclaw/skills/watery-traders/` 等）。

```bash
# 克隆（默认目录 ths_adb_trader/）
git clone https://github.com/crazy3water/ths_adb_trader.git

# 或者直接装到 OpenClaw skills 目录
git clone https://github.com/crazy3water/ths_adb_trader.git \
  ~/.openclaw/skills/watery-traders

# 进入目录（路径以你克隆的实际位置为准）
cd <REPO_DIR>   # 例如: cd ~/app/watery_traders  或  cd ths_adb_trader/

# OpenClaw 通过 mcpServers 启动 mcp_server.py：
python mcp_server.py
# 默认监听 :19090
```

健康检查：

```bash
curl http://localhost:19090/health
# {"status":"ok","device_connected":true|false}
```

### 2. 调用 MCP 工具（OpenClaw agent 透传）

agent 通过 MCP 协议调用 `mcp_server.py` 注册的 16 个工具，全部位于 `http://localhost:19090/mcp/tools/call` 端点。

| 工具名 | 入参 | 用途 |
|---|---|---|
| `get_account` | `{}` | 账户总资产 / 浮动盈亏 / 市值 |
| `get_positions` | `{}` | 当前持仓列表 |
| `get_position_detail` | `{index: int}` | 单只持仓详情（index 从 0 开始）|
| `buy_stock` | `{code, price?, quantity, mode?}` | 买入股票（mode 不传则用当前 trade_mode）|
| `sell_stock` | `{code, price?, quantity, mode?}` | 卖出股票（mode 不传则用当前 trade_mode）|
| `get_orders` | `{order_type: "today"|"history"}` | 当日/历史委托 |
| `cancel_order` | `{index: int}` | 撤单（index 从 0 开始）|
| `set_trade_mode` | `{mode: "simulate"|"real"}` | **关键**：切换交易模式 |
| `get_trade_mode` | `{}` | 查询当前交易模式 |
| `screenshot` | `{name?}` | 截屏（base64 返回）|
| `open_ths` | `{}` | 打开同花顺 APP |
| `close_ths` | `{}` | 关闭同花顺 APP |
| `get_device_info` | `{}` | 手机型号 / Android 版本 / 电量 |
| `back` | `{times: int=1}` | 系统返回键 |
| `dump_ui` | `{}` | 导出当前页面 XML（调试用）|
| `find_buttons` | `{}` | 查找当前页面按钮（调试用）|

完整 schema（JSON Schema）通过 `GET http://localhost:19090/mcp/tools` 获取。

---

## 🔹 触发词 → 工具映射（自然语言路由）

| 用户表述 | 工具调用 | 备注 |
|---|---|---|
| "看看账户" / "账户总资产" | `get_account` | 不修改任何状态 |
| "持仓" / "我持有哪些股票" | `get_positions` | 只读 |
| "这只票详情"（配合 index） | `get_position_detail({index: N})` | index 必须先通过 `get_positions` 拿到 |
| "今天的委托" | `get_orders({order_type: "today"})` | 只读 |
| "历史委托" | `get_orders({order_type: "history"})` | 只读 |
| "撤单"（默认第 1 个） | `cancel_order({index: 0})` | ⚠️ 修改状态 |
| "买入 600519 100 股，价格 1500" | `buy_stock({code:"600519", price:"1500", quantity:"100"})` | ⚠️ 修改状态 |
| "市价买入 600519 100 股" | `buy_stock({code:"600519", quantity:"100"})` | price 缺省走市价 |
| "卖出 002472 全部" | 先 `get_positions` 找该 code → `sell_stock(...)` | ⚠️ 修改状态 |
| "切换到模拟" | `set_trade_mode({mode:"simulate"})` | **修改 trade_mode** |
| "切换到实盘" | `set_trade_mode({mode:"real"})` | **高风险**，必须二次确认 |
| "现在什么模式" | `get_trade_mode` | 只读 |
| "截个图看看" | `screenshot({name: "..."})` | 只读 |
| "打开同花顺" | `open_ths` | 修改 APP 状态 |
| "手机啥型号" | `get_device_info` | 只读 |

---

## 🔒 安全前置协议（任何 modify 类动作必走）

### 模式检查（每次写入动作前）

```
1. 调 get_trade_mode 读当前模式
2. 若 mode == "real"：
   a. 调 screenshot 截图，告知用户当前实盘模式
   b. 必须显式再向用户确认："当前是实盘，确认要执行 [action] 吗？"
   c. 用户说"确认"才执行；用户说"取消"立即中止
3. 若 mode == "simulate"：
   a. 默认直接执行（用户没明确要求实盘，simulate 是默认安全模式）
   b. 除非用户明确说"实盘"，否则不要主动 set_trade_mode
```

### 写入动作清单（必须走前置协议）

- `set_trade_mode`（任何 mode）
- `buy_stock`（任何 mode）
- `sell_stock`（任何 mode）
- `cancel_order`（任何 mode）
- `open_ths` / `close_ths`（启动 APP 也算 modify 设备状态）

### 只读动作清单（无需前置）

`get_account`, `get_positions`, `get_position_detail`, `get_orders`, `get_trade_mode`, `get_device_info`, `screenshot`, `dump_ui`, `find_buttons`

---

## 🛠️ 安装（首次部署）

```bash
# 进入仓库根目录（路径以你克隆的实际位置为准）
cd <REPO_DIR>   # 例如: cd ths_adb_trader  或  cd ~/app/watery_traders
bash install.sh
```

脚本会做：

1. 检查 `python3` ≥ 3.12
2. 检查 `adb` 可用
3. `pip install -r requirements.txt`（uiautomator2 + fastapi + sse-starlette）
4. 验证 `mcp_server.py` 可被 import（不实际启动服务）

启动服务由 OpenClaw 在 `mcpServers` 配置中自动拉起，**不要**手动跑 `python mcp_server.py`，避免端口冲突。

---

## 📜 版本 & 范围记录

- **v1.0**（2026-07-26）：首版 OpenClaw skill 封装
  - 保留 `mcp_server.py` 不变（已是 MCP 协议）
  - 16 个 MCP 工具全部透传
  - 加 SKILL.md：触发词路由 + 安全前置协议 + 风险免责
  - 加 `install.sh`：环境检查（不动交易逻辑）
  - **不**修改 `trader.py` / `app.py` / `config.py` 任何 Python 代码
  - **不**修改 `requirements.txt`

---

## 🚫 绝对禁忌

- ❌ 主动调 `set_trade_mode({mode:"real"})` 切到实盘（除非用户**明确**说"切到实盘"）
- ❌ 在 mode 未确认的情况下执行 `buy_stock` / `sell_stock`
- ❌ 同一次对话里"未撤单"又"重复下单"——必须先 `get_orders` 查委托
- ❌ 把 `price` 默认填"市价"——必须用户说"市价"才缺省
- ❌ 自行编造股票代码、价格、数量——必须从用户原话取
- ❌ 选股 / 预测股价 / 提供策略——本 skill **不**做研究

## ✅ 必做

- ✅ 每次 modify 动作前调 `get_trade_mode`（并截图若实盘）
- ✅ 买入/卖出后调 `get_orders` 确认委托已提交
- ✅ 报错时调 `screenshot` + `dump_ui` 排查，不要盲重试
- ✅ 持仓价格、数量二次校验（防止误下大单）
- ✅ 默认 simulate 模式；切实盘前必须二次确认

---

## ⚠️ 免责声明

本 skill 由同花顺 APP UI 自动化驱动，依赖手机 ADB 连接、APP 版本、网络状况。任何环节中断、APP 改版、价格滑点、操作失误均可能导致实际交易结果与预期不符。  
**任何交易产生的盈亏由用户本人承担**。本 skill 作者与 OpenClaw 平台不对任何交易损失负责。  
**强烈建议先用 `simulate` 模式验证所有流程，再用 `real` 模式。**

---

## 📌 维护提示

老板级维护动作（agent 不主动做）：

- 改 `trader.py` 选择器（文字/xpath）：等 APP 改版后人工适配
- 改 `config.py` 的 `DEVICE_SERIAL`：换手机后人工改
- 改 `mcp_server.py` 的 tool schema：保持 OpenClaw / Claude Desktop 兼容
- 加新 MCP tool：先在 `mcp_server.py` 的 `get_tools()` 注册，再在本 SKILL.md 加映射