# stress_test.py
import requests
import time
import threading
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class StressTester:
    """压力测试类"""

    def __init__(self, base_url="http://localhost:8000", concurrency=5, requests=20):
        self.base_url = base_url
        self.concurrency = concurrency
        total_requests = requests
        self.session = requests.Session()
        self.results = []
        self.errors = []

    def _make_request(self, request_id, endpoint, method="GET", **kwargs):
        """执行单个请求"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            end_time = time.time()
            duration = end_time - start_time

            result = {
                "id": request_id,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "duration": duration,
                "success": response.status_code == 200,
                "timestamp": datetime.now().isoformat()
            }

            if response.status_code != 200:
                result["error"] = response.text[:200]
                self.errors.append(result)

            return result

        except Exception as e:
            end_time = time.time()
            duration = end_time - start_time
            result = {
                "id": request_id,
                "endpoint": endpoint,
                "status_code": None,
                "duration": duration,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.errors.append(result)
            return result

    def run_stress_test(self, endpoints):
        """运行压力测试"""
        logger.info("=" * 60)
        logger.info(f"开始压力测试")
        logger.info(f"并发数: {self.concurrency}")
        logger.info(f"测试端点: {endpoints}")
        logger.info("=" * 60)

        tasks = []
        request_id = 0

        with ThreadPoolExecutor(max_workers=self.concurrency) as executor:
            # 为每个端点生成请求
            futures = []
            for endpoint, count in endpoints.items():
                for i in range(count):
                    request_id += 1
                    futures.append(
                        executor.submit(self._make_request, request_id, endpoint)
                    )

            # 收集结果
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)

                # 实时进度
                if result["success"]:
                    logger.debug(f"请求 {result['id']}: {result['endpoint']} - {result['duration']:.3f}s")
                else:
                    logger.warning(f"请求 {result['id']} 失败: {result.get('error')}")

        self._analyze_results()

    def _analyze_results(self):
        """分析测试结果"""
        logger.info("=" * 60)
        logger.info("压力测试结果")
        logger.info("=" * 60)

        total = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total - successful

        # 计算响应时间统计
        durations = [r["duration"] for r in self.results if r["success"]]
        if durations:
            avg_duration = statistics.mean(durations)
            max_duration = max(durations)
            min_duration = min(durations)
            p95_duration = sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0]
        else:
            avg_duration = max_duration = min_duration = p95_duration = 0

        # 按端点统计
        endpoint_stats = {}
        for r in self.results:
            endpoint = r["endpoint"]
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {"total": 0, "success": 0, "durations": []}

            endpoint_stats[endpoint]["total"] += 1
            if r["success"]:
                endpoint_stats[endpoint]["success"] += 1
                endpoint_stats[endpoint]["durations"].append(r["duration"])

        # 输出结果
        logger.info(f"总请求数: {total}")
        logger.info(f"成功: {successful} ({successful / total * 100:.2f}%)")
        logger.info(f"失败: {failed} ({failed / total * 100:.2f}%)")
        logger.info(f"平均响应时间: {avg_duration:.3f}s")
        logger.info(f"最大响应时间: {max_duration:.3f}s")
        logger.info(f"最小响应时间: {min_duration:.3f}s")
        logger.info(f"95分位响应时间: {p95_duration:.3f}s")

        logger.info("\n端点统计:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = stats["success"] / stats["total"] * 100
            avg_dur = statistics.mean(stats["durations"]) if stats["durations"] else 0
            logger.info(f"  {endpoint}: {stats['total']}次, 成功率 {success_rate:.2f}%, 平均 {avg_dur:.3f}s")

        if self.errors:
            logger.info(f"\n错误详情 ({len(self.errors)}):")
            for err in self.errors[:5]:  # 只显示前5个
                logger.info(f"  请求 {err['id']}: {err.get('error', '未知错误')}")

        # 保存结果
        result_file = f"stress_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump({
                "summary": {
                    "total": total,
                    "successful": successful,
                    "failed": failed,
                    "success_rate": f"{successful / total * 100:.2f}%",
                    "avg_duration": avg_duration,
                    "max_duration": max_duration,
                    "min_duration": min_duration,
                    "p95_duration": p95_duration
                },
                "endpoint_stats": endpoint_stats,
                "errors": self.errors[:20]  # 只保存前20个错误
            }, f, indent=2)

        logger.info(f"\n详细结果已保存: {result_file}")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Watery Traders 压力测试")
    parser.add_argument("--url", default="http://localhost:8000", help="API基础URL")
    parser.add_argument("--concurrency", type=int, default=5, help="并发数")
    parser.add_argument("--requests", type=int, default=20, help="总请求数")
    parser.add_argument("--endpoint", choices=["root", "info", "screenshot", "all"], default="info")

    args = parser.parse_args()

    # 配置测试端点
    if args.endpoint == "root":
        endpoints = {"/": args.requests}
    elif args.endpoint == "info":
        endpoints = {"/device/info": args.requests}
    elif args.endpoint == "screenshot":
        endpoints = {"/ths/screenshot": args.requests}
    else:  # all
        endpoints = {
            "/": args.requests // 4,
            "/device/info": args.requests // 4,
            "/ths/screenshot": args.requests // 2
        }

    tester = StressTester(args.url, args.concurrency, args.requests)
    tester.run_stress_test(endpoints)


if __name__ == "__main__":
    main()