# # !/usr/bin/env python
# # coding: utf-8
# # 导入必要的模块
# import logging
# import time
# # 导入 Decimal 用于高精度计算，ROUND_UP 用于向上舍入，getcontext 用于获取和设置 Decimal 的上下文
# from decimal import Decimal as D, ROUND_UP, getcontext
#
# # 从 gate_api 库导入所需的类和异常
# from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder, Transfer, WalletApi
# from gate_api.exceptions import GateApiException
#
# # 从 gate_config 模块导入 RunConfig 类，用于配置运行参数
# from gate_config import RunConfig
#
# # 获取一个 logger 实例，用于记录日志
# logger = logging.getLogger(__name__)
#
#
# # 定义一个函数来演示期货交易操作
# def futures_demo(run_config):
#     # type: (RunConfig) -> None
#     # 设置结算币种为 USDT
#     settle = "usdt"
#     # 设置交易合约为 BTC_USDT
#     contract = "BTC_USDT"
#
#     # 初始化 API 客户端
#     # 设置 host 是可选的，默认为 https://api.gateio.ws/api/v4
#     # 使用 RunConfig 中的 api_key, api_secret 和 host_used 来配置客户端
#     config = Configuration(key=run_config.api_key, secret=run_config.api_secret, host=run_config.host_used)
#     # 创建 FuturesApi 实例，用于执行期货相关的 API 调用
#     futures_api = FuturesApi(ApiClient(config))
#
#     # 更新仓位杠杆
#     leverage = "3"
#     # 调用 update_position_leverage 方法更新指定合约的杠杆
#     # futures_api.update_position_leverage(settle, contract, leverage)
#
#     # 获取仓位大小
#     position_size = 0
#     try:
#         # 调用 get_position 方法获取指定合约的当前仓位信息
#         position = futures_api.get_position(settle, contract)
#         # 获取仓位的数量
#         position_size = position.size
#     except GateApiException as ex:
#         # 捕获 GateApiException 异常
#         # 如果异常标签不是 "POSITION_NOT_FOUND" (仓位未找到)，则重新抛出异常
#         if ex.label != "POSITION_NOT_FOUND":
#             raise ex
#
#
#
#     # 获取最新价格以计算所需保证金
#     # 调用 list_futures_tickers 方法获取指定合约的行情信息
#     tickers = futures_api.list_futures_tickers(settle, contract=contract)
#     # 确保返回的行情信息列表中只有一个元素
#     assert len(tickers) == 1
#     # 获取最新成交价格
#     last_price = tickers[0].last
#     # 记录最新价格日志
#     logger.info("last price of contract %s: %s", contract, last_price)
#
#     # 使用市价下单
#     # 创建一个 FuturesOrder 对象，指定合约、订单数量、价格为 "0" (表示市价)，tif 为 'ioc' (立即成交或取消)
#     order = FuturesOrder(contract=contract, size=order_size, price="0", tif='ioc')
#     try:
#         # 调用 create_futures_order 方法创建期货订单
#         order_response = futures_api.create_futures_order(settle, order)
#     except GateApiException as ex:
#         # 捕获 GateApiException 异常，记录错误日志并返回
#         logger.error("error encountered creating futures order: %s", ex)
#         return
#     # 记录订单创建成功的日志，包括订单 ID 和状态
#     logger.info("order %s created with status: %s", order_response.id, order_response.status)
#
#
#
#
#
#
# if __name__ == '__main__':
#     cfg = RunConfig("91b7b7897be9d71073fa898208f1c9aa","98cd59e4273d77a18219166b4fc27cad0dbefbe751f44f454458d1fca84941dc")
#     futures_demo(cfg)