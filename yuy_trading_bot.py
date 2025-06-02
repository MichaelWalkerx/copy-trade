# 导入所需的库
import math # 导入数学库
# from binance.um_futures import UMFutures # 从binance库导入UMFutures类，用于与币安U本位合约API交互
import time # 导入time库，用于处理时间相关操作
import logging # 导入logging库，用于记录日志
# import pandas as pd # 导入pandas库，用于数据处理和分析 (在此代码中未使用)
# import openpyxl # 导入openpyxl库，用于读写Excel文件 (在此代码中未使用)
from gate.gateApi import 查询账户余额,获取仓位列表,变更杠杆倍数,获取指定币的价格,gate开单
# 从config模块导入配置信息，包括api_key, api_secret
from config import api_key,api_secret,followed_leader_id,my_leader_id
from logUtil import print___leader_position,print___leader_detail
# 从binanceApi模块导入币安相关的API函数
from binanceApi import fetch_portfolio, fetch_userinfo, fetch_leader_detail, fetch_leverage, adjust_leverage
from gate.util import TradingUtil


#https://www.binance.com/zh-CN/copy-trading/lead-details/3962663535186762752?timeRange=90D

# 同步间隔时长 例如每隔1s同步仓位 时间过长会导致滑点过大 过短请求过于频繁
sync_wait_time = 1 # 同步仓位的等待时间（秒）

# binance API key 开启读取权限就行 主要用来读取开仓前的ticker价格 用于滑点判断

# um_futures_client = UMFutures(api_key, api_secret) # 初始化币安U本位合约客户端 (当前被注释掉，未启用)

# 滑点控制 这个不太好把握 开启了之后可能开仓平仓不同步 可能出现开了仓没及时平掉
enable_slippage_protection = False # 是否启用滑点保护
slippage = 0.1 # 滑点阈值

# 日志级别配置
logging.basicConfig(
    filename='./log.log', # 日志文件名
    level=logging.INFO, # 日志记录级别设置为INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # 日志格式
)
logger = logging.getLogger(__name__) # 获取一个logger实例



# 定义函数：同步仓位
"""
同步我的持仓与跟随的带单员的持仓。
"""


def get_gate_balance():
    json = 查询账户余额()
    return json['cross_margin_balance']


def sync_position():
    """
    只是获取一下余额信息。
    """
    leader_detail,leader_margin_balance = get_balance(followed_leader_id)

    """
    只是获取一下余额信息。
    """
    leader_portfolio = fetch_portfolio(followed_leader_id)
    # 过滤出带单员当前有持仓的列表 (adl不为零表示有持仓)
    leader_cur_open_position = [item for item in leader_portfolio if item.get('adl') != 0]
    print___leader_position(leader_cur_open_position) # 打印带单员持仓信息

# ````需要修改的点
    # 获取我自己的详情和持仓信息
    我的账户余额 = get_gate_balance()
    我的账户余额 = 100

# -------------
    my_portfolio = 获取仓位列表()
    # 过滤出我自己当前有持仓的列表 (adl不为零表示有持仓)
    my_cur_open_position = [item for item in my_portfolio if item.get('value') != '0']

    # print___leader_position(my_cur_open_position) # 打印我自己的持仓信息


    # 获取我自己的杠杆设置信息
    # my_leverage_dict = fetch_leverage(my_leader_id)

    # 遍历带单员的当前持仓
    for leader_position in leader_cur_open_position:
        leader_symbol = leader_position['symbol'] # 交易对
        leader_symbol = 'FARTCOINUSDT'
        leader_position_side = leader_position['positionSide'] # 持仓方向
        # leader_position_side = 'LONG' # 持仓方向
        leader_position_amount = abs(float(leader_position["positionAmount"])) # 持仓数量
        leader_entry_price = leader_position['entryPrice'] # 开仓价格
        leader_leverage = leader_position['leverage'] # 杠杆倍数
        leader_isolated = leader_position['isolated'] # 是否逐仓

        # 计算我应该持有的仓位数量 (根据我的保证金余额与带单员保证金余额的比例)
        我应该持仓百分比 = leader_position_amount * float(我的账户余额) / leader_margin_balance
        我应该持仓百分比 = 0.5

        # 判断我是否有同品种同方向的仓位
        my_same_side_symbol_position = [item for item in my_cur_open_position if
                                        item.get('contract').replace('_', '')  == leader_symbol and item.get(
                                            'mode').replace('dual_', '').upper() == leader_position_side]

        # 如果存在多条同品种同方向的仓位历史数据，记录错误并跳过
        if len(my_same_side_symbol_position) > 1:
            logger.error("存在多条同品种同方向仓位历史数据，请关注")
            continue

        # 杠杆对齐：如果我的杠杆与带单员不一致，则调整杠杆
        # if not is_same_leverage(my_same_side_symbol_position, leader_symbol, leader_leverage):
        #     logger.info(f"调整 {leader_symbol} 杠杆数量和带单员一致: {leader_leverage}倍")
        #     adjust_leverage(leader_symbol, my_leader_id, leader_leverage)
        if len(my_same_side_symbol_position) == 1:
            my_leverage = my_same_side_symbol_position[0]['cross_leverage_limit']
            print(my_leverage)
            if my_leverage != leader_leverage:
                print(f"{leader_symbol} 我当前的杠杆倍数:{my_leverage} 调整 {leader_symbol} 杠杆数量和带单员一致: {leader_leverage}倍")
                # 变更杠杆倍数(leader_symbol.replace('USDT', '_USDT'),leader_leverage)


        command = None # 初始化订单操作命令
        quantity = 0 # 初始化订单数量
        my_position_amount = 0 # 初始化我的持仓--价值
        gate_size = 0 # gate平台需要交易的张数
        # 如果我已有同品种同方向的仓位
        if len(my_same_side_symbol_position) == 1:
            # 已有仓位，检查同方向同品种的持仓数据是否有变化
            my_position_info = my_same_side_symbol_position[0]
            # 计算持仓多少个XX币 计算一下我当前仓位价值 占余额的百分比
            my_position_amount = float(my_position_info['value'])

            # 计算仓位差异
            position_amount_diff = float(float(我应该持仓百分比) * float(我的账户余额) - my_position_amount)
            if position_amount_diff < 0:
                # 仓位过大，需要减仓
                command = "CLOSE"
                quantity = abs(position_amount_diff) # 减仓的价值
                gate_size =  TradingUtil.calculate_contract_size(获取指定币的价格(leader_symbol), leader_symbol.replace("USDT","_USDT"), quantity)
                print(f"仓位过大，需要缩仓 {gate_size}张")
            elif position_amount_diff > 0:
                # 仓位过小，需要加仓
                command = "OPEN"
                quantity = position_amount_diff # 加仓的价值
                gate_size =  TradingUtil.calculate_contract_size(获取指定币的价格(leader_symbol), leader_symbol.replace("USDT","_USDT"), quantity)
                print(f"仓位过小，需要扩仓 {gate_size}张")
        else:
            # 新增仓位：如果我没有同品种同方向的仓位，则需要开仓
            command = "OPEN"
            quantity = 我应该持仓百分比 * 我的账户余额 # 开仓数量为应该持有的仓位数量
            gate_size = TradingUtil.calculate_contract_size(获取指定币的价格(leader_symbol),leader_symbol.replace("USDT", "_USDT"), quantity)
            print(f"仓位过不存在,新开单 -> {gate_size}张")

        # 带单员新增的仓位 全仓 (注释说明，实际代码中isolated参数是根据带单员的设置传递的)
        # 获取当前交易对的最新价格 (需要um_futures_client启用)
        cur_price = 获取指定币的价格(leader_symbol) # 请注意：此处需要根据实际情况获取当前价格

        # 滑点保护判断 (如果启用滑点保护)
        if enable_slippage_protection:
            # 如果是空头仓位且当前价格与带单员开仓价的差异大于滑点阈值，则跳过
            if leader_position_side == 'SHORT' and (float(leader_entry_price) - float(cur_price)) > slippage:
                continue
            # 如果是多头仓位且当前价格与带单员开仓价的差异大于滑点阈值，则跳过
            if leader_position_side == 'LONG' and (float(cur_price) - float(leader_entry_price)) > slippage:
                continue
        # 如果有订单操作命令且订单数量占应该持有仓位的比例大于0.05 (避免小额订单)
        if command is not None and quantity / 我应该持仓百分比* 我的账户余额 > 0.05:
            # 记录订单信息
            logger.info(f"{leader_symbol} 应该持仓价值: {我应该持仓百分比* 我的账户余额} 实际持仓价值: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {quantity} 价格: {cur_price}")
            print(f"{leader_symbol} 应该持仓价值: {我应该持仓百分比* 我的账户余额} 实际持仓价值: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {quantity} 价格: {cur_price}")
            # 下单
            # TODO 编写Gate的下单逻辑
            # '{"contract":"BTC_USDT","size":6024,"iceberg":0,"price":"3765","tif":"gtc","text":"t-my-custom-id","stp_act":"-"}'
            # order_info = gate开单()
            # 记录成交信息
            # logger.info(f"{'开' if command == 'OPEN' else '平'}{'空' if order_info['positionSide'] == 'SHORT' else '多'} 成交价格: {order_info['price']} 成交数量: {order_info['origQty']}")

    # 遍历我自己的当前持仓
    for my_position in my_cur_open_position:
        my_symbol = my_position['symbol'] # 交易对
        my_position_side = my_position['positionSide'] # 持仓方向
        my_position_amount = abs(float(my_position['positionAmount'])) # 持仓数量
        my_leverage = my_position['leverage'] # 杠杆倍数
        my_isolated = my_position['isolated'] # 是否逐仓
        # 判断带单员是否有同品种同方向的仓位
        leader_same_side_symbol_position = [item for item in leader_cur_open_position if
                                        item.get('symbol') == my_symbol and item.get(
                                            'positionSide') == my_position_side]
        # 有同品种同方向的仓位 跳过
        if len(leader_same_side_symbol_position) != 0:
            continue
        # 如果带单员没有同品种同方向的仓位
        # 我比带单员多出来的仓位 全部平仓
        # 获取当前交易对的最新价格 (需要um_futures_client启用)
        cur_price = um_futures_client.ticker_price(my_symbol)['price']
        # 临时使用一个占位符价格，因为um_futures_client被注释掉了
        cur_price = 0.0 # 请注意：此处需要根据实际情况获取当前价格

        command = "CLOSE" # 订单操作命令：平仓
        # 记录订单信息
        logger.info(f"{my_symbol} 应该持仓: 0 实际持仓: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {my_position_amount} 价格: {cur_price}")
        # 下单 (平仓我的全部持仓) TODO 多出来的仓位  直接平掉 不用多BB
        # order_info = place_order(command, my_symbol, my_position_side, my_position_amount, cur_price,
        #                          my_leader_id, my_leverage, my_isolated)
        # # 记录成交信息
        # logger.info(f"{'开' if command == 'OPEN' else '平'}{'空' if order_info['positionSide'] == 'SHORT' else '多'} 成交价格: {order_info['price']} 成交数量: {order_info['origQty']}")


def get_balance(leader_id):
    my_detail = fetch_leader_detail(leader_id)
    my_margin_balance = float(my_detail['marginBalance'])  # 我自己的保证金余额
    print___leader_detail(my_detail)  # 打印我自己的详情
    return my_detail,my_margin_balance


# 主程序入口
if __name__ == "__main__":
    # fetch_leader_detail(followed_leader_id)
    # 无限循环，持续同步仓位
    while True:
        sync_position() # 调用同步仓位函数
        time.sleep(sync_wait_time) # 等待指定的同步间隔时间