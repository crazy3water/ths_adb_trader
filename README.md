# Watery Traders - 同花顺自动化交易系统

[English](./README_EN.md) | 中文

## 项目介绍

Watery Traders 是一个通过 uiautomator2 控制安卓手机上的同花顺APP进行自动化交易的 Python 系统。该项目提供 RESTful API 和 MCP (Model Context Protocol) 支持，可以与 AI 助手（如 Claude Desktop）集成实现智能化交易。

⚠️ **风险提示**：本系统用于自动化交易，使用前请充分测试并了解相关风险。作者不对任何交易损失负责。

## 功能特性

- 📱 **设备控制**：通过 USB 或 WiFi 连接安卓手机
- 📊 **账户查询**：获取账户总资产、浮动盈亏、持仓市值
- 💰 **交易操作**：买入、卖出、撤单
- 📈 **持仓管理**：查看持仓列表、持仓详情
- 📝 **委托查询**：当日委托、历史委托查询
- 🖼️ **截图功能**：随时查看手机屏幕状态
- 🤖 **MCP支持**：支持 Claude Desktop 等 AI 助手调用

## 技术栈

- **Python** 3.12+
- **uiautomator2** - 安卓设备自动化控制
- **FastAPI** - RESTful API 服务
- **MCP** - Model Context Protocol (可选)

## 环境要求

1. **Python 3.12** 或更高版本
2. **安卓手机**一台（已安装同花顺APP）
3. **ADB** 已配置（USB调试或WiFi调试）
4. **同花顺APP** 已登录账号

## 快速开始

### 1. 克隆项目

```bash
git clone http://192.168.3.14:3000/watery/watery_traders.git
cd watery_traders
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置设备

编辑 `ths/config.py`：

```python
DEVICE_SERIAL = "192.168.3.6:5555"  # 改为你的手机IP和端口
```

### 4. 安装同花顺APP到手机

确保手机已并登录账号。

### 5.安装同花顺 启动服务

```bash
python -m ths.app
```

服务将在 `http://localhost:8000` 启动。

API文档：`http://localhost:8000/docs`

## API 端点

### 设备管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /device/info | 获取设备信息 |
| POST | /device/reconnect | 重新连接设备 |
| POST | /device/back | 后退操作 |
| POST | /device/back_to_home | 返回手机首页 |

### 同花顺控制

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /ths/open | 打开同花顺 |
| POST | /ths/close | 关闭同花顺 |
| POST | /ths/restart | 重启同花顺 |

### 交易操作

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ths/account | 获取账户概览 |
| GET | /ths/positions | 获取持仓列表 |
| GET | /ths/position/{index} | 获取持仓详情 |
| POST | /ths/buy | 买入股票 |
| POST | /ths/sell | 卖出股票 |
| POST | /ths/cancel | 撤单 |

### 委托查询

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /ths/orders | 获取委托记录 |
| POST | /ths/set_mode | 设置交易模式 |

### 调试工具

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /ths/screenshot | 截图 |
| GET | /ths/buttons | 查找按钮 |
| POST | /ths/dump_ui | 导出UI结构 |

## 使用示例

### 买入股票

```bash
curl -X POST "http://localhost:8000/ths/buy?code=600519&price=1500&quantity=100"
```

### 查询持仓

```bash
curl -X GET "http://localhost:8000/ths/positions"
```

### 切换到模拟交易

```bash
curl -X POST "http://localhost:8000/ths/set_mode?mode=simulate"
```

## MCP 使用

如果你想通过 Claude Desktop 等 AI 助手调用：

### 1. 安装 MCP

```bash
pip install mcp
```

### 2. 启动 MCP 服务

```bash
python mcp_server.py
```

### 3. 配置 Claude Desktop

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "watery-traders": {
      "command": "python",
      "args": ["/path/to/watery_traders/mcp_server.py"]
    }
  }
}
```

## 目录结构

```
watery_traders/
├── README.md                 # 项目说明
├── README_EN.md              # 英文版说明
├── requirements.txt           # Python依赖
├── main.py                   # 入口文件
├── mcp_server.py              # MCP服务器 (可选)
├── mcp_config.json            # MCP配置 (可选)
├── ths/
│   ├── __init__.py
│   ├── config.py             # 配置文件
│   ├── trader.py             # 核心交易类
│   ├── app.py                # FastAPI服务
│   └── test/                 # 测试目录
│       ├── test_api.py
│       └── stress_test.py
├── docs/                     # 文档目录
│   ├── API.md
│   └── ARCHITECTURE.md
└── screenshots/              # 截图保存目录
```

## 注意事项

1. **风险提示**：自动化交易存在风险，请谨慎使用
2. **网络要求**：手机和电脑需要在同一网络
3. **APP权限**：确保同花顺已授予必要权限
4. **交易限额**：建议先用模拟交易测试
5. **日志查看**：日志保存在 `logs/` 目录

## 常见问题

### Q: 连接不上手机怎么办？
A: 确保手机已开启USB调试或WiFi调试，检查ADB连接状态。

### Q: 买入失败怎么办？
A: 检查股票代码是否正确，价格和数量是否在有效范围内。

### Q: 如何切换模拟/实盘？
A: 使用 `/ths/set_mode?mode=simulate` 或 `mode=real`。

## 许可证

MIT License
