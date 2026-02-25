# test_ths_api_pytest.py
import pytest
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any
import os
from pathlib import Path

# 配置
BASE_URL = "http://localhost:8000"
SCREENSHOT_DIR = Path("./test_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


# ==================== 测试类 ====================

class TestThsAPI:
    """同花顺API测试类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.base_url = BASE_URL
        self.session = requests.Session()
        # 测试服务是否可用
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            assert response.status_code == 200
            print(f"\n✅ 服务连接成功: {self.base_url}")
        except Exception as e:
            pytest.skip(f"服务未启动: {e}")

    def request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """发送请求"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, timeout=30, **kwargs)
        assert response.status_code == 200, f"HTTP {response.status_code}"
        return response.json()

    # ==================== 基础测试 ====================

    def test_root(self):
        """测试根路径"""
        data = self.request("GET", "/")
        assert data is not None
        assert "name" in data
        assert "version" in data
        print(f"\n✅ 根路径测试通过: {data.get('name')} v{data.get('version')}")

    def test_device_info(self):
        """测试设备信息"""
        data = self.request("GET", "/device/info")
        assert data.get("success") is True
        info = data.get("info", {})
        assert "product" in info
        print(f"\n✅ 设备信息: {info.get('product')} - {info.get('model')}")
        print(f"   屏幕: {info.get('screen')}, 电量: {info.get('battery')}%")

    def test_device_reconnect(self):
        """测试设备重连"""
        data = self.request("POST", "/device/reconnect")
        assert data.get("success") is True
        print(f"\n✅ 设备重连成功, 模式: {data.get('trade_mode')}")

    # ==================== 后退导航测试 ====================

    def test_back(self):
        """测试后退"""
        data = self.request("POST", "/device/back?times=1")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")

    def test_back_to_home(self):
        """测试返回首页"""
        data = self.request("POST", "/device/back_to_home")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")

    def test_back_to_trade_main(self):
        """测试返回交易主页面"""
        data = self.request("POST", "/ths/back_to_trade_main")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")

    # ==================== 应用控制测试 ====================

    def test_open_ths(self):
        """测试打开同花顺"""
        data = self.request("POST", "/ths/open")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")
        time.sleep(2)

    def test_close_ths(self):
        """测试关闭同花顺"""
        data = self.request("POST", "/ths/close")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")

    def test_restart_ths(self):
        """测试重启同花顺"""
        data = self.request("POST", "/ths/restart")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")
        time.sleep(3)

    # ==================== 交易模式测试 ====================

    @pytest.mark.parametrize("mode", ["simulate", "real"])
    def test_set_mode(self, mode):
        """测试设置交易模式"""
        data = self.request("POST", f"/ths/set_mode?mode={mode}")
        assert data.get("success") is True
        print(f"\n✅ {data.get('message')}")
        time.sleep(1)

    def test_get_mode(self):
        """测试获取交易模式"""
        data = self.request("GET", "/ths/mode")
        assert data.get("success") is True
        print(f"\n✅ 当前模式: {data.get('mode_text')} ({data.get('mode')})")

    # ==================== 账户测试 ====================

    def test_account_summary(self):
        """测试获取账户概览"""
        data = self.request("GET", "/ths/account")
        assert data.get("success") is True
        print(f"\n✅ 账户概览:")
        print(f"   总资产: {data.get('total_asset')}")
        print(f"   浮动盈亏: {data.get('float_profit')}")
        print(f"   总市值: {data.get('total_market_value')}")
        print(f"   当日盈亏: {data.get('daily_profit')}")

    # ==================== 持仓测试 ====================

    def test_positions(self):
        """测试获取持仓列表"""
        data = self.request("GET", "/ths/positions")
        assert data.get("success") is True
        positions = data.get("positions", [])
        print(f"\n✅ 获取到 {len(positions)} 条持仓记录")

        for i, pos in enumerate(positions[:3]):
            print(f"   {i + 1}. {pos.get('code')} {pos.get('name')} "
                  f"{pos.get('quantity')}股 {pos.get('profit')}")

    def test_position_detail(self):
        """测试获取持仓详情"""
        # 先获取持仓列表
        data = self.request("GET", "/ths/positions")
        if not data.get("positions"):
            pytest.skip("没有持仓记录")

        # 获取第一个持仓的详情
        data = self.request("GET", "/ths/position/0")
        assert data.get("success") is True
        pos = data.get("position", {})
        print(f"\n✅ 持仓详情:")
        print(f"   代码: {pos.get('code')}")
        print(f"   名称: {pos.get('name')}")
        print(f"   持仓: {pos.get('quantity')}股")
        print(f"   成本: {pos.get('cost_price')}")
        print(f"   现价: {pos.get('current_price')}")
        print(f"   盈亏: {pos.get('profit')} ({pos.get('profit_ratio')})")

    # ==================== 截图测试 ====================

    def test_screenshot(self):
        """测试截图"""
        data = self.request("POST", "/ths/screenshot")
        assert data.get("success") is True
        assert "path" in data
        print(f"\n✅ 截图成功: {data.get('path')}")

    # ==================== 调试工具测试 ====================

    def test_buttons(self):
        """测试查找按钮"""
        data = self.request("GET", "/ths/buttons")
        assert data.get("success") is True
        buttons = data.get("buttons", [])
        count = data.get("count", 0)
        print(f"\n✅ 找到 {count} 个可点击按钮")

        # 显示前5个按钮
        texts = [b.get('text') for b in buttons[:5] if b.get('text')]
        if texts:
            print(f"   示例: {', '.join(texts)}")

    def test_dump_ui(self):
        """测试导出UI结构"""
        data = self.request("POST", "/ths/dump_ui")
        assert data.get("success") is True
        print(f"\n✅ UI结构已导出: {data.get('path')}")

    def test_click(self):
        """测试点击"""
        data = self.request("POST", "/ths/click?text=交易")
        assert data.get("success") is True
        print(f"\n✅ 点击成功")

    def test_activity(self):
        """测试获取Activity"""
        data = self.request("GET", "/ths/activity")
        assert data.get("success") is True
        print(f"\n✅ 当前Activity: {data.get('activity')}")

    # ==================== 委托测试 ====================

    @pytest.mark.parametrize("order_type", ["today", "history"])
    def test_orders(self, order_type):
        """测试获取委托记录"""
        data = self.request("GET", f"/ths/orders?type={order_type}")
        assert data.get("success") is True
        orders = data.get("orders", [])
        print(f"\n✅ {order_type}委托: 找到 {len(orders)} 条记录")


# ==================== 单独的测试函数 ====================

def test_service_health():
    """测试服务健康状态"""
    response = requests.get(f"{BASE_URL}/", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") in ["connected", "disconnected"]
    print(f"\n✅ 服务状态: {data.get('status')}")


# ==================== 测试套件 ====================

class TestTradeFlow:
    """交易流程测试（需要谨慎执行）"""

    @pytest.mark.skip(reason="需要手动确认")
    def test_buy_flow(self):
        """测试买入流程"""
        tester = TestThsAPI()
        tester.setup_method()

        # 1. 打开同花顺
        tester.test_open_ths()
        time.sleep(2)

        # 2. 设置模拟模式
        data = tester.request("POST", "/ths/set_mode?mode=simulate")
        assert data.get("success") is True

        # 3. 获取账户概览
        data = tester.request("GET", "/ths/account")
        assert data.get("success") is True
        print(f"\n买入前总资产: {data.get('total_asset')}")

        # 4. 执行买入
        data = tester.request(
            "POST",
            "/ths/buy?code=600519&price=1500&quantity=100&mode=simulate"
        )
        assert data.get("success") is True
        print(f"\n✅ 买入成功")

        # 5. 再次获取账户概览
        time.sleep(2)
        data = tester.request("GET", "/ths/account")
        print(f"买入后总资产: {data.get('total_asset')}")

    @pytest.mark.skip(reason="需要手动确认")
    def test_sell_flow(self):
        """测试卖出流程"""
        tester = TestThsAPI()
        tester.setup_method()

        # 1. 打开同花顺
        tester.test_open_ths()
        time.sleep(2)

        # 2. 设置模拟模式
        data = tester.request("POST", "/ths/set_mode?mode=simulate")
        assert data.get("success") is True

        # 3. 获取持仓
        data = tester.request("GET", "/ths/positions")
        if not data.get("positions"):
            pytest.skip("没有持仓")

        # 4. 执行卖出
        data = tester.request(
            "POST",
            "/ths/sell?code=600519&price=1600&quantity=100&mode=simulate"
        )
        assert data.get("success") is True
        print(f"\n✅ 卖出成功")


# ==================== pytest fixtures ====================

@pytest.fixture(scope="session")
def api_tester():
    """创建API测试器"""
    tester = TestThsAPI()
    tester.setup_method()
    return tester


@pytest.fixture
def ensure_ths_open(api_tester):
    """确保同花顺已打开"""
    api_tester.test_open_ths()
    time.sleep(2)
    yield
    # 测试结束后不关闭，留给其他测试使用


# ==================== 测试分组 ====================

class TestBasicFunctions:
    """基础功能测试组"""

    def test_basic_flow(self, api_tester):
        """测试基础流程"""
        api_tester.test_root()
        api_tester.test_device_info()
        api_tester.test_activity()
        api_tester.test_screenshot()


class TestNavigationFunctions:
    """导航功能测试组"""

    def test_navigation_flow(self, api_tester, ensure_ths_open):
        """测试导航流程"""
        api_tester.test_click()
        time.sleep(1)
        api_tester.test_back_to_trade_main()
        api_tester.test_back()
        api_tester.test_back_to_home()


class TestAccountFunctions:
    """账户功能测试组"""

    def test_account_flow(self, api_tester, ensure_ths_open):
        """测试账户流程"""
        # 进入交易页面
        api_tester.test_click()
        time.sleep(2)

        # 测试账户功能
        api_tester.test_account_summary()
        api_tester.test_positions()

        # 如果有持仓，测试详情
        data = api_tester.request("GET", "/ths/positions")
        if data.get("positions"):
            api_tester.test_position_detail()


# ==================== 主函数 ====================

if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "--tb=short"])