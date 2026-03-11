# API 接口文档

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs` (Swagger UI)
- **格式**: JSON
- **编码**: UTF-8

## 响应格式

### 成功响应

```json
{
  "success": true,
  "data": { ... }
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误信息"
}
```

---

## 设备管理

### 获取设备信息

**GET** `/device/info`

获取已连接设备的基本信息。

### 重新连接设备

**POST** `/device/reconnect`

重新连接到安卓设备。

### 后退操作

**POST** `/device/back`

执行系统返回操作。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| times | int | 否 | 后退次数，默认1，最大10 |

### 返回手机首页

**POST** `/device/back_to_home`

一直返回直到回到手机主页。

---

## 同花顺控制

### 打开同花顺

**POST** `/ths/open`

启动同花顺APP。

### 关闭同花顺

**POST** `/ths/close`

关闭同花顺APP。

### 重启同花顺

**POST** `/ths/restart`

重启同花顺APP。

---

## 交易模式

### 设置交易模式

**POST** `/ths/set_mode`

切换模拟交易或实盘A股。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| mode | string | 是 | `simulate` 或 `real` |

### 获取当前模式

**GET** `/ths/mode`

---

## 账户信息

### 获取账户概览

**GET** `/ths/account`

获取账户总资产、浮动盈亏等信息。

**响应示例**:
```json
{
  "success": true,
  "mode": "simulate",
  "total_asset": "1,000,000.00",
  "float_profit": "50,000.00",
  "total_market_value": "800,000.00",
  "daily_profit": "10,000.00"
}
```

---

## 持仓管理

### 获取持仓列表

**GET** `/ths/positions`

获取所有持仓股票。

**响应示例**:
```json
{
  "success": true,
  "positions": [
    {"code": "600519", "name": "贵州茅台", "quantity": "100", "price": "1650.00"}
  ]
}
```

### 获取持仓详情

**GET** `/ths/position/{index}`

获取指定持仓的详细信息。

**参数**: index - 持仓索引，从0开始

---

## 交易操作

### 买入股票

**POST** `/ths/buy`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 股票代码（如600519） |
| price | string | 是 | 买入价格 |
| quantity | string | 是 | 买入数量 |
| mode | string | 否 | 交易模式，不填使用当前模式 |

### 卖出股票

**POST** `/ths/sell`

参数同上。

---

## 委托管理

### 获取委托记录

**GET** `/ths/orders`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| type | string | 否 | `today` 当日委托，`history` 历史委托，默认today |

### 撤单

**POST** `/ths/cancel`

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| index | int | 否 | 要撤销的委托索引，默认0 |

---

## 截图功能

### 截图

**POST** `/ths/screenshot`

截取当前手机屏幕。

---

## 调试工具

### 查找按钮

**GET** `/ths/buttons`

列出当前页面所有可点击的按钮。

### 导出UI结构

**POST** `/ths/dump_ui`

导出当前页面的UI层级结构（XML格式）。

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 参数错误 |
| 500 | 服务器内部错误 |
| 503 | 设备未连接 |
