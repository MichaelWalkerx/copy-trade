# 导入所需的库
import math # 导入数学库
from binance.um_futures import UMFutures # 从binance库导入UMFutures类，用于与币安U本位合约API交互
import time # 导入time库，用于处理时间相关操作
import logging # 导入logging库，用于记录日志
import pandas as pd # 导入pandas库，用于数据处理和分析 (在此代码中未使用)
import openpyxl # 导入openpyxl库，用于读写Excel文件 (在此代码中未使用)

# 从config模块导入配置信息，包括api_key, api_secret
from config import api_key,api_secret,followed_leader_id,my_leader_id
# 从binanceApi模块导入币安相关的API函数
from binanceApi import fetch_portfolio, fetch_userinfo, fetch_leader_detail, fetch_leverage, adjust_leverage

# 以下注释说明了如何获取cookies和headers，用于模拟网页登录
# 通过网页登录到币安网页版 进入跟单详情页面 https://www.binance.com/zh-CN/copy-trading
# 跟单带单接口都是非官方公开API F12之后复制一个xhr请求 复制为cURL(bash)
# 之后通过https://curlconverter.com/将cURL快速转换成requests得到cookies和headers 这个网站仅在本地做转换 可以放心使用


# 带单者的id 点击带单者的详情页可以看到 例如ddbxxb的详情页 https://www.binance.com/zh-CN/copy-trading/lead-details/3962663535186762752?timeRange=90D
# followed_leader_id为 4154811161454700544 我的带单id同理


# 同步间隔时长 例如每隔1s同步仓位 时间过长会导致滑点过大 过短请求过于频繁
sync_wait_time = 1 # 同步仓位的等待时间（秒）

# binance API key 开启读取权限就行 主要用来读取开仓前的ticker价格 用于滑点判断

# um_futures_client = UMFutures(api_key, api_secret) # 初始化币安U本位合约客户端 (当前被注释掉，未启用)

# 滑点控制 这个不太好把握 开启了之后可能开仓平仓不同步 可能出现开了仓没及时平掉
enable_slippage_protection = False # 是否启用滑点保护
slippage = 0.1 # 滑点阈值

# 日志级别配置
logging.basicConfig(
    filename='./binance_copy_trading_bot.log', # 日志文件名
    level=logging.INFO, # 日志记录级别设置为INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # 日志格式
)
logger = logging.getLogger(__name__) # 获取一个logger实例

# 定义函数：检查杠杆是否一致
def is_same_leverage(leverage_dict, _symbol, expected_leverage):
    # 过滤出指定交易对且杠杆与期望值一致的项，判断列表长度是否大于0
    return len([item for item in leverage_dict if item.get('symbol') == _symbol and item.get('leverage') == expected_leverage]) > 0


# 定义函数：下单
def place_order(command, _symbol, position_side, quantity, price, portfolio_id, leverage, isolated=False, time_in_force="GTC", order_type="MARKET"):
    """
    在币安U本位合约上下单。

    Args:
        command (str): 订单操作类型 ("OPEN" 或 "CLOSE")。
        _symbol (str): 交易对符号。
        position_side (str): 持仓方向 ("LONG" 或 "SHORT")。
        quantity (float): 订单数量。
        price (float): 订单价格 (仅限限价单)。
        portfolio_id (str): 投资组合ID。
        leverage (int): 杠杆倍数。
        isolated (bool, optional): 是否为逐仓模式. Defaults to False (全仓).
        time_in_force (str, optional): 订单生效时间. Defaults to "GTC".
        order_type (str, optional): 订单类型 ("MARKET" 或 "LIMIT"). Defaults to "MARKET".

    Returns:
        dict: 订单响应数据。
    """
    # 生效时间t ime_in_force的说明
    # • GTC (生效直到取消): 此种订单将持续有效直到完全成交或被取消。
    # • IOC (立即成交或取消): 此种订单将会立即成交全部或部分订单，并且取消剩余未成交的部分。
    # • FOK (全部成交或取消): 此种订单必须立即全部成交，否则将被全部取消。

    if command is None:
        return None # 如果command为None，则不执行下单操作

    order_info = {} # 初始化订单信息字典

    # 限价开仓订单信息模板
    limit_order_open = {
        "symbol": _symbol, # 交易对符号
        "type": "LIMIT", # 订单类型：限价单
        "side": "SELL" if position_side == "SHORT" else "BUY", # 订单方向：根据持仓方向确定买入或卖出
        "positionSide": position_side, # 持仓方向
        "quantity": quantity, # 订单数量
        "timeInForce": time_in_force, # 生效时间
        "price": price, # 订单价格
        "copyTradeType": "PUB_LEAD", # 跟单类型：公开带单
        "portfolioId": portfolio_id, # 投资组合ID
        "placeType": "order-form" # 下单类型：订单表单
    }

    # 限价平仓订单信息模板
    limit_order_close = {
        "symbol": _symbol, # 交易对符号
        "type": "LIMIT", # 订单类型：限价单
        "side": "BUY" if position_side == "SHORT" else "SELL", # 订单方向：根据持仓方向确定买入或卖出
        "quantity": quantity, # 订单数量
        "price": price, # 订单价格
        "positionSide": position_side, # 持仓方向
        "leverage": leverage, # 杠杆倍数
        "isolated": isolated, # 是否逐仓
        "timeInForce": time_in_force, # 生效时间
        "copyTradeType": "PUB_LEAD", # 跟单类型：公开带单
        "portfolioId": portfolio_id, # 投资组合ID
        "placeType": "position" # 下单类型：持仓
    }

    # 市价开仓订单信息模板
    market_order_open = {
        "symbol": _symbol, # 交易对符号
        "type": "MARKET", # 订单类型：市价单
        "side": "SELL" if position_side == "SHORT" else "BUY", # 订单方向：根据持仓方向确定买入或卖出
        "positionSide": position_side, # 持仓方向
        "quantity": quantity, # 订单数量
        "copyTradeType": "PUB_LEAD", # 跟单类型：公开带单
        "portfolioId": portfolio_id, # 投资组合ID
        "placeType": "order-form" # 下单类型：订单表单
    }

    # 市价平仓订单信息模板
    market_order_close = {
      "symbol": _symbol, # 交易对符号
      "type": "MARKET", # 订单类型：市价单
      "side": "BUY" if position_side == "SHORT" else "SELL", # 订单方向：根据持仓方向确定买入或卖出
      "quantity": quantity, # 订单数量
      "positionSide": position_side, # 持仓方向
      "leverage": leverage, # 杠杆倍数
      "isolated": isolated, # 是否逐仓
      "copyTradeType": "PUB_LEAD", # 跟单类型：公开带单
      "portfolioId": portfolio_id, # 投资组合ID
      "newOrderRespType": "RESULT", # 新订单响应类型：返回结果
      "placeType": "position" # 下单类型：持仓
    }

    # 根据订单类型和操作类型选择相应的订单信息模板
    if order_type == "LIMIT" and command == "OPEN":
        order_info = limit_order_open
    if order_type == "LIMIT" and command == "CLOSE":
        order_info = limit_order_close
    if order_type == "MARKET" and command == "OPEN":
        order_info = market_order_open
    if order_type == "MARKET" and command == "CLOSE":
        order_info = market_order_close

    # logger.info(order_info) # 记录订单信息 (当前被注释掉)
    url = "https://www.binance.com/bapi/futures/v1/private/future/order/place-order" # API请求URL
    response = session.post(url, json=order_info).json() # 发送POST请求并解析JSON响应
    expected_status_code = '000000' # 期望的成功状态码
    # 断言：检查响应状态码是否为期望值，否则抛出错误
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"
    return response['data'] # 返回响应中的数据部分


# 定义函数：打印带单员详情
def print___leader_detail(leader_detail):
    """
    打印带单员的详细信息。
    """
    logger.info(f"================{leader_detail['nickname']}===================") # 打印带单员昵称
    logger.info(f"带单保证金: {leader_detail['marginBalance']}") # 打印带单保证金
    logger.info(f"资产管理规模: {leader_detail['aumAmount']}") # 打印资产管理规模
    logger.info(f"跟单者盈亏: {leader_detail['copierPnl']}") # 打印跟单者盈亏
    logger.info(
        f"最小带单金额: 定额 {leader_detail['fixedAmountMinCopyUsd']} | 定比 {leader_detail['fixedRadioMinCopyUsd']}") # 打印最小带单金额
    logger.info(f"分润比例: {leader_detail['profitSharingRate']}") # 打印分润比例
    logger.info("=========================================\n") # 打印分隔线


# 定义函数：打印带单员持仓信息
def print___leader_position(leader_position_list):
    """
    打印带单员的持仓信息列表。
    """
    logger.info(f"================持仓信息===================") # 打印持仓信息标题
    for leader_position in leader_position_list: # 遍历持仓列表
        logger.info("---------------------------------") # 打印分隔线
        # 打印持仓方向、交易对、仓位模式和杠杆倍数
        logger.info(f"{'空' if leader_position['positionSide'] == 'SHORT' else '多'} {leader_position['symbol']} {'逐仓' if leader_position['isolated'] else '全仓'}{leader_position['leverage']}倍")
        # 打印未实现盈亏、持仓数量和保证金
        logger.info(f"未实现盈亏: {leader_position['unrealizedProfit']}{leader_position['collateral']} 持仓数量: {abs(float(leader_position['positionAmount']))}  保证金: {abs(float(leader_position['notionalValue']) / leader_position['leverage'])}")
        logger.info(f"开仓价: {leader_position['entryPrice']} 标记价格: {leader_position['markPrice']}") # 打印开仓价和标记价格
        logger.info("---------------------------------") # 打印分隔线
    logger.info("=========================================\n") # 打印分隔线

# 定义函数：同步仓位
def sync_position():
    """
    同步我的持仓与跟随的带单员的持仓。
    """
    # 获取跟随的带单员的详情和持仓信息
    leader_detail = fetch_leader_detail(followed_leader_id)
    leader_margin_balance = float(leader_detail['marginBalance']) # 带单员的保证金余额
    print___leader_detail(leader_detail) # 打印带单员详情

    leader_portfolio = fetch_portfolio(followed_leader_id)
    # 过滤出带单员当前有持仓的列表 (adl不为零表示有持仓)
    leader_cur_open_position = [item for item in leader_portfolio if item.get('adl') != 0]
    print___leader_position(leader_cur_open_position) # 打印带单员持仓信息

    # 获取我自己的详情和持仓信息
    my_detail = fetch_leader_detail(my_leader_id)
    my_margin_balance = float(my_detail['marginBalance']) # 我自己的保证金余额
    print___leader_detail(my_detail) # 打印我自己的详情

    my_portfolio = fetch_portfolio(my_leader_id)
    # 过滤出我自己当前有持仓的列表 (adl不为零表示有持仓)
    my_cur_open_position = [item for item in my_portfolio if item.get('adl') != 0]
    print___leader_position(my_cur_open_position) # 打印我自己的持仓信息

    # 获取我自己的杠杆设置信息
    my_leverage_dict = fetch_leverage(my_leader_id)

    # 遍历带单员的当前持仓
    for leader_position in leader_cur_open_position:
        leader_symbol = leader_position['symbol'] # 交易对
        leader_position_side = leader_position['positionSide'] # 持仓方向
        leader_position_amount = abs(float(leader_position["positionAmount"])) # 持仓数量
        leader_entry_price = leader_position['entryPrice'] # 开仓价格
        leader_leverage = leader_position['leverage'] # 杠杆倍数
        leader_isolated = leader_position['isolated'] # 是否逐仓

        # 计算我应该持有的仓位数量 (根据我的保证金余额与带单员保证金余额的比例)
        my_should_hold_position_amount = leader_position_amount * my_margin_balance / leader_margin_balance

        # 判断我是否有同品种同方向的仓位
        my_same_side_symbol_position = [item for item in my_cur_open_position if
                                        item.get('symbol') == leader_symbol and item.get(
                                            'positionSide') == leader_position_side]

        # 如果存在多条同品种同方向的仓位历史数据，记录错误并跳过
        if len(my_same_side_symbol_position) > 1:
            logger.error("存在多条同品种同方向仓位历史数据，请关注")
            continue

        # 杠杆对齐：如果我的杠杆与带单员不一致，则调整杠杆
        if not is_same_leverage(my_leverage_dict, leader_symbol, leader_leverage):
            logger.info(f"调整 {leader_symbol} 杠杆数量和带单员一致: {leader_leverage}倍")
            adjust_leverage(leader_symbol, my_leader_id, leader_leverage)

        command = None # 初始化订单操作命令
        quantity = 0 # 初始化订单数量
        my_position_amount = 0 # 初始化我的持仓数量

        # 如果我已有同品种同方向的仓位
        if len(my_same_side_symbol_position) == 1:
            # 已有仓位，检查同方向同品种的持仓数据是否有变化
            my_position_info = my_same_side_symbol_position[0]
            my_position_amount = abs(float(my_position_info['positionAmount'])) # 我的当前持仓数量

            # 计算仓位差异
            position_amount_diff = my_should_hold_position_amount - my_position_amount
            if position_amount_diff < 0:
                # 仓位过大，需要减仓
                command = "CLOSE"
                quantity = abs(position_amount_diff) # 减仓数量为差异的绝对值
            elif position_amount_diff > 0:
                # 仓位过小，需要加仓
                command = "OPEN"
                quantity = position_amount_diff # 加仓数量为差异值
        else:
            # 新增仓位：如果我没有同品种同方向的仓位，则需要开仓
            command = "OPEN"
            quantity = my_should_hold_position_amount # 开仓数量为应该持有的仓位数量

        # 带单员新增的仓位 全仓 (注释说明，实际代码中isolated参数是根据带单员的设置传递的)
        # 获取当前交易对的最新价格 (需要um_futures_client启用)
        # cur_price = um_futures_client.ticker_price(leader_symbol)['price']
        # 临时使用一个占位符价格，因为um_futures_client被注释掉了
        cur_price = 0.0 # 请注意：此处需要根据实际情况获取当前价格

        # 滑点保护判断 (如果启用滑点保护)
        if enable_slippage_protection:
            # 如果是空头仓位且当前价格与带单员开仓价的差异大于滑点阈值，则跳过
            if leader_position_side == 'SHORT' and (float(leader_entry_price) - float(cur_price)) > slippage:
                continue
            # 如果是多头仓位且当前价格与带单员开仓价的差异大于滑点阈值，则跳过
            if leader_position_side == 'LONG' and (float(cur_price) - float(leader_entry_price)) > slippage:
                continue
        # 如果有订单操作命令且订单数量占应该持有仓位的比例大于0.05 (避免小额订单)
        if command is not None and quantity / my_should_hold_position_amount > 0.05:
            # 记录订单信息
            logger.info(f"{leader_symbol} 应该持仓: {my_should_hold_position_amount} 实际持仓: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {quantity} 价格: {cur_price}")
            # 下单
            order_info = place_order(command, leader_symbol, leader_position_side, quantity, cur_price,
                                     my_leader_id, leader_leverage, leader_isolated)
            # 记录成交信息
            logger.info(f"{'开' if command == 'OPEN' else '平'}{'空' if order_info['positionSide'] == 'SHORT' else '多'} 成交价格: {order_info['price']} 成交数量: {order_info['origQty']}")

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
        # 如果带单员没有同品种同方向的仓位
        if len(leader_same_side_symbol_position) != 0:
            continue
        # 我比带单员多出来的仓位 全部平仓
        # 获取当前交易对的最新价格 (需要um_futures_client启用)
        # cur_price = um_futures_client.ticker_price(my_symbol)['price']
        # 临时使用一个占位符价格，因为um_futures_client被注释掉了
        cur_price = 0.0 # 请注意：此处需要根据实际情况获取当前价格

        command = "CLOSE" # 订单操作命令：平仓
        # 记录订单信息
        logger.info(f"{my_symbol} 应该持仓: 0 实际持仓: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {my_position_amount} 价格: {cur_price}")
        # 下单 (平仓我的全部持仓)
        order_info = place_order(command, my_symbol, my_position_side, my_position_amount, cur_price,
                                 my_leader_id, my_leverage, my_isolated)
        # 记录成交信息
        logger.info(f"{'开' if command == 'OPEN' else '平'}{'空' if order_info['positionSide'] == 'SHORT' else '多'} 成交价格: {order_info['price']} 成交数量: {order_info['origQty']}")


# 主程序入口
if __name__ == "__main__":
    fetch_leader_detail(followed_leader_id)
    # 无限循环，持续同步仓位
    # while True:
    #     sync_position() # 调用同步仓位函数
    #     time.sleep(sync_wait_time) # 等待指定的同步间隔时间