# 测试timer装饰器
from ths.trader import ThsTrader


def test_timer():
    """测试timer装饰器是否正常工作"""
    print("=== 测试timer装饰器 ===")
    
    # 创建Trader实例
    trader = ThsTrader()
    
    # 调用带有@timer装饰器的方法
    print("\n调用get_account_summary方法...")
    result = trader.get_account_summary()
    
    # 打印结果
    print(f"\n方法执行结果: {result['success']}")
    if result['success']:
        print(f"总资产: {result['total_asset']}")
        print(f"浮动盈亏: {result['float_profit']}")


if __name__ == "__main__":
    test_timer()
