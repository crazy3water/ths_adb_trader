# Watery Traders - 同花顺自动化交易系统

[![GitHub Stars](https://img.shields.io/github/stars/yourusername/watery-traders.svg?style=social&label=Star)](https://github.com/yourusername/watery-traders)
[![GitHub Forks](https://img.shields.io/github/forks/yourusername/watery-traders.svg?style=social&label=Fork)](https://github.com/yourusername/watery-traders)
[![GitHub Issues](https://img.shields.io/github/issues/yourusername/watery-traders)](https://github.com/yourusername/watery-traders/issues)
[![GitHub License](https://img.shields.io/github/license/yourusername/watery-traders)](https://github.com/yourusername/watery-traders/blob/main/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)

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
2. **安卓手机**一台（已安装同花顺APP并登录账号）
3. **ADB** 已配置（USB调试或WiFi调试）
4. **同花顺APP** 已登录账号（建议先在模拟交易环境测试）

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/watery-traders.git
cd watery-traders
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装和配置ADB

#### ADB安装指南

##### Windows系统
1. 下载 [Android Platform Tools](https://developer.android.com/studio/releases/platform-tools)
2. 解压到任意目录（如 `C:\platform-tools`）
3. 将该目录添加到系统环境变量 `PATH`
4. 验证安装：打开命令提示符输入 `adb version`，若显示版本信息则安装成功

##### macOS系统
1. 安装 Homebrew（如果未安装）：`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. 安装 ADB：`brew install android-platform-tools`
3. 验证安装：`adb version`

##### Linux系统
1. Ubuntu/Debian：`sudo apt-get install adb`
2. Fedora：`sudo dnf install android-tools`
3. 验证安装：`adb version`

#### 配置ADB连接

##### USB调试模式
1. 手机开启开发者选项（设置 → 关于手机 → 连续点击版本号7次）
2. 开启USB调试（设置 → 开发者选项 → USB调试）
3. 用USB线连接手机和电脑
4. 手机上同意USB调试授权
5. 验证连接：`adb devices`，若显示设备序列号则连接成功

##### WiFi调试模式（推荐）
1. 先通过USB连接手机，确保ADB可用
2. 启用WiFi调试：`adb tcpip 5555`
3. 断开USB连接
4. 查询手机IP地址（设置 → WLAN → 已连接网络 → IP地址）
5. 通过IP连接：`adb connect 手机IP:5555`
6. 验证连接：`adb devices`，若显示IP地址则连接成功

### 4. 修改配置文件

编辑 `ths/config.py` 配置文件：

```python
# 设备配置
DEVICE_SERIAL = "192.168.3.6:5555"  # 改为你的设备序列号或WiFi连接地址

# 同花顺配置
THS_PACKAGE = "com.hexin.plat.android"  # 通常不需要修改

# 截图配置
SCREENSHOT_DIR = BASE_DIR / "screenshots"  # 截图保存目录

# 超时配置（秒）
DEFAULT_TIMEOUT = 10
PAGE_LOAD_TIMEOUT = 3
```

### 5. 启动服务

```bash
# 启动REST API服务
python main.py

# 或启动MCP服务
python main.py --mcp

# 或同时启动两个服务
python main.py --both
```

- REST API服务：`http://localhost:8000`
- API文档：`http://localhost:8000/docs`（自动生成的Swagger UI）
- MCP服务：`http://localhost:19090`（可选）

## API 端点

### 核心接口说明

> ⏱️ **重要提示**：买入和卖出操作经过测试需要约1分钟左右才能完成，请合理安排交易间隔。

### 设备管理

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | /device/info | - | 获取设备信息（型号、系统版本、屏幕尺寸等） |
| POST | /device/reconnect | - | 重新连接设备 |
| POST | /device/back | times: int（后退次数） | 后退指定次数 |
| POST | /device/back_to_home | - | 返回手机首页 |
| POST | /ths/back_to_trade_main | - | 返回同花顺交易主页面 |

### 应用控制

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| POST | /ths/open | - | 打开同花顺APP |
| POST | /ths/close | - | 关闭同花顺APP |
| POST | /ths/restart | - | 重启同花顺APP |

### 交易模式

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| POST | /ths/set_mode | mode: str（simulate/real） | 设置交易模式（模拟/实盘） |
| GET | /ths/mode | - | 获取当前交易模式 |

### 账户信息

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | /ths/account | - | 获取账户概览（总资产、浮动盈亏、总市值等） |

### 持仓管理

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | /ths/positions | - | 获取持仓列表 |
| GET | /ths/position/{index} | index: int（持仓索引） | 获取单个持仓详情 |

### 交易操作

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| POST | /ths/buy | code: str（股票代码）<br>price: str（买入价格）<br>quantity: str（买入数量）<br>mode: str（可选，交易模式） | 买入股票（约1分钟完成） |
| POST | /ths/sell | code: str（股票代码）<br>price: str（卖出价格）<br>quantity: str（卖出数量）<br>mode: str（可选，交易模式） | 卖出股票（约1分钟完成） |

### 委托管理

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | /ths/orders | type: str（today/history） | 获取委托记录（当日/历史） |
| POST | /ths/cancel | index: int（委托索引） | 撤销指定委托 |

### 调试工具

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| POST | /ths/screenshot | - | 截图并返回base64编码 |
| GET | /screenshots/{filename} | filename: str（截图文件名） | 获取指定截图文件 |
| GET | /ths/buttons | - | 查找当前页面所有按钮（调试用） |
| POST | /ths/dump_ui | - | 导出当前页面UI结构（调试用） |
| POST | /ths/click | text: str（按钮文字）<br>timeout: int（超时时间） | 点击指定文字的按钮（调试用） |
| GET | /ths/activity | - | 获取当前Activity（调试用） |

## 简洁API清单

### 核心功能
- `GET /ths/account` - 获取账户信息
- `GET /ths/positions` - 查看持仓列表
- `POST /ths/buy?code=600519&price=1500&quantity=100` - 买入股票（约1分钟）
- `POST /ths/sell?code=600519&price=1600&quantity=100` - 卖出股票（约1分钟）

### 模式控制
- `POST /ths/set_mode?mode=simulate` - 切换到模拟交易
- `POST /ths/set_mode?mode=real` - 切换到实盘交易
- `GET /ths/mode` - 获取当前交易模式

### 导航功能
- `POST /device/back?times=1` - 后退指定次数
- `POST /device/back_to_home` - 返回手机首页
- `POST /ths/back_to_trade_main` - 返回交易主页面

### 委托管理
- `GET /ths/orders?type=today` - 当日委托查询
- `POST /ths/cancel?index=0` - 撤销第1个委托

## 使用示例

### 买入股票

```bash
# 买入贵州茅台，价格1500元，数量100股
curl -X POST "http://localhost:8000/ths/buy?code=600519&price=1500&quantity=100"
```

### 查询持仓

```bash
# 获取当前持仓列表
curl -X GET "http://localhost:8000/ths/positions"
```

### 切换到模拟交易

```bash
# 切换交易模式到模拟交易
curl -X POST "http://localhost:8000/ths/set_mode?mode=simulate"
```

### 撤单

```bash
# 撤销第1个委托（索引从0开始）
curl -X POST "http://localhost:8000/ths/cancel?index=0"
```

### 获取设备信息

```bash
# 获取当前连接的设备信息
curl -X GET "http://localhost:8000/device/info"
```

## MCP 使用 (可选)

MCP (Model Context Protocol) 支持允许 Claude Desktop 等 AI 助手直接调用本系统的功能。

### 1. 安装 MCP 依赖

```bash
# 安装 MCP 支持
pip install sse-starlette
```

### 2. 启动 MCP 服务

```bash
# 启动 MCP 服务（端口19090）
python main.py --mcp

# 或同时启动 REST API 和 MCP 服务
python main.py --both
```

### 3. 配置 Claude Desktop

在 Claude Desktop 配置中添加：

```json
{
  "mcpServers": {
    "watery-traders": {
      "command": "python",
      "args": ["/path/to/watery-traders/main.py", "--mcp"]
    }
  }
}
```

### 4. 使用 Claude Desktop 调用

配置完成后，你可以直接在 Claude Desktop 中使用自然语言指令：

```
请帮我查询账户信息
帮我买入100股贵州茅台，价格1500元
查看我的持仓列表
```

## 目录结构

```
watery-traders/
├── README.md                 # 项目说明
├── requirements.txt          # Python依赖
├── main.py                   # 主入口文件
├── mcp_server.py             # MCP服务器实现
├── mcp_config.json           # MCP配置文件
├── ths/                      # 同花顺自动化核心包
│   ├── __init__.py           # 包初始化
│   ├── config.py             # 配置文件
│   ├── trader.py             # 核心交易类
│   ├── app.py                # FastAPI服务实现
│   ├── utils.py              # 工具函数
│   └── test/                 # 测试目录
├── docs/                     # 文档目录
├── logs/                     # 日志保存目录
└── screenshots/              # 截图保存目录
```

## 注意事项

### 1. 交易风险提示
- ⚠️ **风险提示**：自动化交易存在风险，实盘交易前请务必充分测试
- 💡 **建议**：先用模拟交易功能测试所有操作，确保系统正常工作
- ⏱️ **交易耗时**：买入和卖出操作经过测试需要约1分钟左右才能完成，请合理安排交易间隔
- 📊 **交易限制**：遵守同花顺APP的交易规则和限制

### 2. 技术要求
- 📶 **网络要求**：WiFi调试模式下，手机和电脑需要在同一局域网内
- 📱 **设备要求**：建议使用性能较好的安卓手机，避免因设备卡顿影响交易
- 📱 **APP版本**：确保同花顺APP为最新版本，部分旧版本可能不兼容
- 🔧 **ADB稳定性**：ADB连接可能会不定期断开，建议定期检查连接状态

### 3. 安全建议
- 🔒 **账户安全**：不要将账户密码硬编码到代码中
- 🛡️ **权限控制**：限制API服务的访问权限，避免未授权访问
- 📝 **日志管理**：定期查看日志文件，及时发现异常情况
- 📂 **备份数据**：定期备份重要数据和配置文件

## 常见问题

### Q: 连接不上手机怎么办？
A: 请按照以下步骤排查：
1. 检查手机是否已开启开发者选项和USB调试
2. 验证ADB是否正常工作：`adb devices`
3. 检查手机是否同意了USB调试授权
4. WiFi调试模式下，确保手机和电脑在同一网络
5. 尝试重新连接：`adb reconnect` 或重启服务

### Q: 买入/卖出操作失败怎么办？
A: 请检查以下事项：
1. 股票代码是否正确（深圳A股需带后缀.SZ，上海A股需带后缀.SH）
2. 价格是否在当日涨跌停范围内
3. 数量是否符合交易单位要求（通常为100股的整数倍）
4. 账户是否有足够的资金或持仓
5. 查看日志文件获取详细错误信息

### Q: 交易模式如何切换？
A: 使用以下API接口切换交易模式：
- 切换到模拟交易：`POST /ths/set_mode?mode=simulate`
- 切换到实盘交易：`POST /ths/set_mode?mode=real`
- 获取当前模式：`GET /ths/mode`

### Q: 如何查看交易执行状态？
A: 可以通过以下方式查看：
1. 调用 `GET /ths/orders?type=today` 查询当日委托
2. 使用 `POST /ths/screenshot` 截图查看手机屏幕状态
3. 查看日志文件获取详细执行信息

## 贡献指南

欢迎提交Issue和Pull Request！

### 开发流程
1. Fork 本仓库
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交Pull Request

### 开发规范
- 代码风格：使用 black 格式化代码
- 类型注解：为所有函数添加类型注解
- 文档：为新功能添加详细文档
- 测试：为新功能添加单元测试

## 许可证

本项目采用 MIT License 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，欢迎通过以下方式联系：

- GitHub Issues：[提交问题](https://github.com/yourusername/watery-traders/issues)
- Email：your.email@example.com

## 致谢

感谢以下开源项目的支持：

- [uiautomator2](https://github.com/openatx/uiautomator2) - 安卓设备自动化
- [FastAPI](https://github.com/tiangolo/fastapi) - 现代化的Python Web框架
- [ADB](https://developer.android.com/studio/command-line/adb) - Android调试桥

---

**Watery Traders** - 让股票交易更智能、更高效！ 🚀
