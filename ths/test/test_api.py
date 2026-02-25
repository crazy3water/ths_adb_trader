# test_api.py
import requests
import json
import time
import base64
from datetime import datetime
from typing import Dict, Any, List
import unittest
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WateryTradersTest:
    """Watery Traders API 测试类"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def _request(self, method, endpoint, **kwargs):
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败: {e}")
            return None

    def _record_result(self, test_name, success, data=None, error=None):
        """记录测试结果"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "error": error
        }
        self.test_results.append(result)

        if success:
            logger.info(f"✅ {test_name} 通过")
        else:
            logger.error(f"❌ {test_name} 失败: {error}")

        return result

    def test_root(self):
        """测试根路径"""
        try:
            response = self._request("GET", "/")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("根路径测试", True, data)
            else:
                return self._record_result("根路径测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("根路径测试", False, error=str(e))

    def test_device_info(self):
        """测试设备信息"""
        try:
            response = self._request("GET", "/device/info")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return self._record_result("设备信息测试", True, data)
                else:
                    return self._record_result("设备信息测试", False, error="设备未连接")
            else:
                return self._record_result("设备信息测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("设备信息测试", False, error=str(e))

    def test_device_reconnect(self):
        """测试设备重连"""
        try:
            response = self._request("POST", "/device/reconnect")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("设备重连测试", data.get("success"), data)
            else:
                return self._record_result("设备重连测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("设备重连测试", False, error=str(e))

    def test_open_ths(self):
        """测试打开同花顺"""
        try:
            response = self._request("POST", "/ths/open")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("打开同花顺测试", data.get("success", False), data)
            else:
                return self._record_result("打开同花顺测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("打开同花顺测试", False, error=str(e))

    def test_screenshot(self):
        """测试截图"""
        try:
            response = self._request("POST", "/ths/screenshot")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 验证base64图片
                    img_base64 = data.get("image_base64", "")
                    if img_base64 and len(img_base64) > 100:
                        return self._record_result("截图测试", True, {
                            "path": data.get("path"),
                            "image_size": len(img_base64)
                        })
                    else:
                        return self._record_result("截图测试", False, error="图片数据无效")
                else:
                    return self._record_result("截图测试", False, error="截图失败")
            else:
                return self._record_result("截图测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("截图测试", False, error=str(e))

    def test_find_buttons(self):
        """测试查找按钮"""
        try:
            response = self._request("GET", "/ths/buttons")
            if response and response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    button_count = data.get("count", 0)
                    buttons = data.get("buttons", [])

                    # 打印前10个按钮
                    logger.info(f"找到 {button_count} 个按钮:")
                    for i, btn in enumerate(buttons[:10]):
                        logger.info(f"  {i + 1}. {btn.get('text', '无文字')}")

                    return self._record_result("查找按钮测试", True, {
                        "count": button_count,
                        "sample": buttons[:5]
                    })
                else:
                    return self._record_result("查找按钮测试", False, error="获取按钮失败")
            else:
                return self._record_result("查找按钮测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("查找按钮测试", False, error=str(e))

    def test_click_button(self, button_text="交易"):
        """测试点击按钮"""
        try:
            response = self._request("POST", f"/ths/click?text={button_text}&timeout=5")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result(f"点击按钮测试({button_text})", data.get("success", False), data)
            else:
                return self._record_result(f"点击按钮测试({button_text})", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result(f"点击按钮测试({button_text})", False, error=str(e))

    def test_goto_trade(self):
        """测试进入交易页面"""
        return self.test_click_button("交易")

    def test_dump_ui(self):
        """测试导出UI结构"""
        try:
            response = self._request("POST", "/ths/dump_ui")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("导出UI测试", data.get("success", False), data)
            else:
                return self._record_result("导出UI测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("导出UI测试", False, error=str(e))

    def test_close_ths(self):
        """测试关闭同花顺"""
        try:
            response = self._request("POST", "/ths/close")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("关闭同花顺测试", data.get("success", False), data)
            else:
                return self._record_result("关闭同花顺测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("关闭同花顺测试", False, error=str(e))

    def test_buy_stock(self, code="600519", price="1500", quantity="100"):
        """测试买入股票（谨慎使用！）"""
        try:
            logger.warning(f"⚠️ 即将执行买入测试: {code} {price} {quantity}")
            confirm = input("确认执行买入测试? (yes/no): ")
            if confirm.lower() != 'yes':
                return self._record_result("买入测试", False, error="用户取消")

            response = self._request(
                "POST",
                f"/ths/buy?code={code}&price={price}&quantity={quantity}"
            )
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("买入测试", data.get("success", False), data)
            else:
                return self._record_result("买入测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("买入测试", False, error=str(e))

    def test_sell_stock(self, code="600519", price="1600", quantity="100"):
        """测试卖出股票（谨慎使用！）"""
        try:
            logger.warning(f"⚠️ 即将执行卖出测试: {code} {price} {quantity}")
            confirm = input("确认执行卖出测试? (yes/no): ")
            if confirm.lower() != 'yes':
                return self._record_result("卖出测试", False, error="用户取消")

            response = self._request(
                "POST",
                f"/ths/sell?code={code}&price={price}&quantity={quantity}"
            )
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("卖出测试", data.get("success", False), data)
            else:
                return self._record_result("卖出测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("卖出测试", False, error=str(e))

    def test_positions(self):
        """测试获取持仓"""
        try:
            response = self._request("GET", "/ths/positions")
            if response and response.status_code == 200:
                data = response.json()
                return self._record_result("持仓查询测试", data.get("success", False), data)
            else:
                return self._record_result("持仓查询测试", False,
                                           error=f"状态码: {response.status_code if response else '无响应'}")
        except Exception as e:
            return self._record_result("持仓查询测试", False, error=str(e))

    def run_all_tests(self, include_trade_tests=False):
        """运行所有测试"""
        logger.info("=" * 60)
        logger.info("开始运行所有测试")
        logger.info("=" * 60)

        # 基础测试
        self.test_root()
        self.test_device_info()
        self.test_device_reconnect()

        # 同花顺操作测试
        self.test_open_ths()
        time.sleep(2)

        self.test_screenshot()
        self.test_find_buttons()
        self.test_goto_trade()
        time.sleep(2)

        self.test_dump_ui()
        self.test_screenshot()

        # 交易测试（需要确认）
        if include_trade_tests:
            self.test_positions()
            # self.test_buy_stock()  # 默认注释掉，需要手动开启
            # self.test_sell_stock()  # 默认注释掉，需要手动开启

        self.test_close_ths()

        # 输出测试报告
        self.print_report()

        return self.test_results

    def print_report(self):
        """打印测试报告"""
        logger.info("=" * 60)
        logger.info("测试报告")
        logger.info("=" * 60)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed

        logger.info(f"总测试数: {total}")
        logger.info(f"通过: {passed} ✅")
        logger.info(f"失败: {failed} ❌")

        if failed > 0:
            logger.info("\n失败的测试:")
            for r in self.test_results:
                if not r["success"]:
                    logger.info(f"  ❌ {r['test']}: {r.get('error', '未知错误')}")

        logger.info("=" * 60)

        # 保存报告到文件
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total": total,
                    "passed": passed,
                    "failed": failed,
                    "pass_rate": f"{passed / total * 100:.2f}%" if total > 0 else "0%"
                },
                "results": self.test_results
            }, f, indent=2, ensure_ascii=False)

        logger.info(f"报告已保存: {report_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Watery Traders 测试脚本")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--test", choices=["all", "basic", "device", "ths", "trade"], default="basic")
    parser.add_argument("--include-trade", action="store_true", help="包含交易测试")
    parser.add_argument("--code", default="600519", help="股票代码")
    parser.add_argument("--price", default="1500", help="价格")
    parser.add_argument("--quantity", default="100", help="数量")

    args = parser.parse_args()

    tester = WateryTradersTest(args.url)

    if args.test == "all":
        tester.run_all_tests(include_trade_tests=args.include_trade)
    elif args.test == "basic":
        tester.test_root()
        tester.test_device_info()
        tester.print_report()
    elif args.test == "device":
        tester.test_device_info()
        tester.test_device_reconnect()
        tester.test_screenshot()
        tester.print_report()
    elif args.test == "ths":
        tester.test_open_ths()
        time.sleep(2)
        tester.test_find_buttons()
        tester.test_goto_trade()
        tester.test_screenshot()
        tester.test_dump_ui()
        tester.test_close_ths()
        tester.print_report()
    elif args.test == "trade":
        if args.include_trade:
            tester.test_open_ths()
            time.sleep(2)
            tester.test_goto_trade()
            tester.test_buy_stock(args.code, args.price, args.quantity)
            tester.test_positions()
            tester.test_close_ths()
            tester.print_report()
        else:
            logger.warning("请使用 --include-trade 参数来执行交易测试")


if __name__ == "__main__":
    main()