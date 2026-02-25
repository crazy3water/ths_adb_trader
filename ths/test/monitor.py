# monitor.py
import requests
import time
import json
import csv
from datetime import datetime
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Monitor:
    """持续监控类"""

    def __init__(self, base_url="http://localhost:8000", interval=60, output_dir="monitor_data"):
        self.base_url = base_url
        self.interval = interval
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # CSV文件
        self.csv_file = self.output_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.csv"
        self._init_csv()

    def _init_csv(self):
        """初始化CSV文件"""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'device_connected', 'device_model', 'android_version',
                    'screen_width', 'screen_height', 'battery_level', 'response_time'
                ])

    def _write_csv(self, data):
        """写入CSV"""
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                data['timestamp'],
                data['device_connected'],
                data.get('device_model', ''),
                data.get('android_version', ''),
                data.get('screen_width', 0),
                data.get('screen_height', 0),
                data.get('battery_level', 0),
                data.get('response_time', 0)
            ])

    def check_device(self):
        """检查设备状态"""
        start_time = time.time()

        try:
            response = requests.get(f"{self.base_url}/device/info", timeout=10)
            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    info = data.get("info", {})
                    return {
                        "success": True,
                        "device_connected": True,
                        "device_model": info.get("model"),
                        "android_version": info.get("android"),
                        "screen_width": int(info.get("screen", "0x0").split("x")[0]) if "x" in info.get("screen",
                                                                                                        "") else 0,
                        "screen_height": int(info.get("screen", "0x0").split("x")[1]) if "x" in info.get("screen",
                                                                                                         "") else 0,
                        "battery_level": info.get("battery"),
                        "response_time": response_time
                    }

            return {
                "success": False,
                "device_connected": False,
                "response_time": response_time
            }

        except Exception as e:
            return {
                "success": False,
                "device_connected": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    def run(self, duration=None):
        """运行监控"""
        logger.info("=" * 60)
        logger.info("开始持续监控")
        logger.info(f"监控间隔: {self.interval}秒")
        logger.info(f"输出目录: {self.output_dir}")
        if duration:
            logger.info(f"监控时长: {duration}秒")
        logger.info("=" * 60)

        start_time = time.time()
        check_count = 0
        error_count = 0

        try:
            while True:
                # 检查是否超时
                if duration and (time.time() - start_time) > duration:
                    logger.info("监控时长到达，停止监控")
                    break

                check_count += 1
                logger.info(f"第 {check_count} 次检查...")

                # 执行检查
                result = self.check_device()

                # 记录结果
                result['timestamp'] = datetime.now().isoformat()
                self._write_csv(result)

                if result.get('success'):
                    logger.info(
                        f"✅ 设备在线 - 电量: {result.get('battery_level')}% - 响应: {result['response_time']:.3f}s")
                else:
                    error_count += 1
                    logger.warning(f"❌ 设备离线 - 响应: {result['response_time']:.3f}s")

                # 等待下一次检查
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("用户中断监控")

        finally:
            # 输出统计
            logger.info("=" * 60)
            logger.info("监控统计")
            logger.info("=" * 60)
            logger.info(f"总检查次数: {check_count}")
            logger.info(f"成功次数: {check_count - error_count}")
            logger.info(f"失败次数: {error_count}")
            logger.info(f"成功率: {(check_count - error_count) / check_count * 100:.2f}%")
            logger.info(f"数据文件: {self.csv_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Watery Traders 持续监控")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--interval", type=int, default=60, help="监控间隔(秒)")
    parser.add_argument("--duration", type=int, help="监控时长(秒)")
    parser.add_argument("--output", default="monitor_data", help="输出目录")

    args = parser.parse_args()

    monitor = Monitor(args.url, args.interval, args.output)
    monitor.run(args.duration)


if __name__ == "__main__":
    main()