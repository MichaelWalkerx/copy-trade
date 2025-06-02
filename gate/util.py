# coding: utf-8

import math
from gate.contract_quanto_multipliers import contract_quanto_multipliers

class TradingUtil:
    """
    交易相关的工具类
    """

    @staticmethod
    def calculate_contract_size(price: float, coin_name: str, order_amount: float) -> int:
        """
        计算给定金额可以开多少张合约

        Args:
            price: 币的价格
            coin_name: 币的名称 (例如 "BTC_USDT")
            order_amount: 开单金额

        Returns:
            可以开的合约张数 (整数，向下取整)
        """
        if coin_name not in contract_quanto_multipliers:
            print(f"Warning: Quanto multiplier not found for {coin_name}. Cannot calculate contract size.")
            return 0

        quanto_multiplier = float(contract_quanto_multipliers[coin_name])

        # 计算合约价值 (一张合约代表的币的数量)
        # contract_value_in_coins = 1 * quanto_multiplier # 这不是合约价值，quanto_multiplier是乘数

        # 计算一张合约的价值 (以USDT计价)
        contract_value_usdt = price * quanto_multiplier

        if contract_value_usdt <= 0:
             print(f"Error: Calculated contract value is zero or negative for {coin_name}. Cannot calculate contract size.")
             return 0

        # 计算可以开的合约张数
        # 张数 = 开单金额 / (一张合约的价值)
        contract_size = order_amount / contract_value_usdt

        # 向下取整，舍弃不足一张的部分
        print(f"使用 {order_usdt} USDT 开 {btc_name} 合约，在价格为 {btc_price} 时，可以开 {math.floor(contract_size)} 张合约。")
        return math.floor(contract_size)

if __name__ == '__main__':
    # 示例用法
    # 假设 BTC_USDT 的 quanto_multiplier 是 0.0001
    # 假设当前 BTC 价格是 40000 USDT
    # 假设开单金额是 1000 USDT

    btc_price = 104123.5
    btc_name = "BTC_USDT"
    order_usdt = 1

    # 为了测试，手动设置一个 quanto_multiplier 的值，实际应用中应该从文件中加载
    # 这里假设 contract_quanto_multipliers 字典已经加载
    # contract_quanto_multipliers = {"BTC_USDT": "0.0001"} # 实际代码中会从文件导入

    calculated_size = TradingUtil.calculate_contract_size(btc_price, btc_name, order_usdt)
