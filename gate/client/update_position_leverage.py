from __future__ import print_function
import gate_api
from gate_api.exceptions import ApiException, GateApiException
# Defining the host is optional and defaults to https://api.gateio.ws/api/v4
# See configuration.py for a list of all supported configuration parameters.
# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure APIv4 key authorization
configuration = gate_api.Configuration(
    host = "https://api-testnet.gateapi.io/api/v4",
    key = "91b7b7897be9d71073fa898208f1c9aa",
    secret = "98cd59e4273d77a18219166b4fc27cad0dbefbe751f44f454458d1fca84941dc"
)
api_client = gate_api.ApiClient(configuration)
# Create an instance of the API class
api_instance = gate_api.FuturesApi(api_client)
settle = 'usdt'  # str | Settle currency


def 调整杠杆(target):

    settle = 'usdt'  # str | Settle currency
    contract = 'BTC_USDT'  # str | Futures contract
    leverage = '0'  # str | New position leverage
    cross_leverage_limit = target  # str | Cross margin leverage(valid only when `leverage` is 0) (optional)
    # Update position leverage
    try:
        # 调用 get_position 方法获取指定合约的当前仓位信息
        api_instance.update_position_leverage(settle, contract, leverage,
                                                             cross_leverage_limit=cross_leverage_limit)
        print("调整成功")
    except GateApiException as ex:
        # 捕获 GateApiException 异常
        # 如果异常标签不是 "POSITION_NOT_FOUND" (仓位未找到)，则重新抛出异常
        if ex.label != "POSITION_NOT_FOUND":
            raise ex
def 获取tick数据():
    settle = 'usdt'  # str | Settle currency
    contract = 'BTC_USDT'  # str | Futures contract, return related data only if specified (optional)
    try:
        tickers = api_instance.list_futures_tickers(settle, contract=contract)
        assert len(tickers) == 1
        # 获取最新成交价格
        last_price = tickers[0].last
        # 记录最新价格日志
        # print("last price of contract %s: %s", contract, last_price)
        return last_price
    except GateApiException as ex:
        print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
    except ApiException as e:
        print("Exception when calling FuturesApi->list_futures_tickers: %s\n" % e)


# 双仓模式下，
# 减仓：reduce_only=true，size 为正数表示减空仓，负数表示减多仓
# 加仓：reduce_only=false，size 为正数表示加多仓，负数表示加空仓

# 对多仓的操作: 加仓 : reduce_only=false + 正数   | 减仓reduce_only=true + 负数
# 对空仓的操作: 加仓 : reduce_only=true + 正数   | 减仓reduce_only=false + 负数
# 平仓：size=0，根据 auto_size 设置平仓的方向，并同时设置 reduce_only 为 true
# reduce_only：确保只执行减仓操作，防止增加仓位
def 市价下单(isNew,target,size_num):
    if isNew:
        futures_order = gate_api.FuturesOrder(contract='BTC_USDT', size=size_num, price="0", tif='ioc')
    else:
        if target == "多仓":
            futures_order = gate_api.FuturesOrder(contract='BTC_USDT', size=size_num, price="0", tif='ioc',reduce_only= size_num < 0)
        else:
            futures_order = gate_api.FuturesOrder(contract='BTC_USDT', size=size_num, price="0", tif='ioc',reduce_only= size_num > 0)

    try:
        # Create a futures order
        api_response = api_instance.create_futures_order(settle, futures_order)
        print(api_response)
    except GateApiException as ex:
        print("Gate api exception, label: %s, message: %s\n" % (ex.label, ex.message))
    except ApiException as e:
        print("Exception when calling FuturesApi->create_futures_order: %s\n" % e)


if __name__ == '__main__':
    # 市价下单(True,"多仓",10)
    # 市价下单(True,"空",-10)
    # 市价下单(False,"多仓",-1)
    市价下单(False,"空仓",-1)
    # 市价下单(False,"多仓",1)
    # 市价下单(False,"空仓",1)
    # 市价下单(False,"空仓",11)
    #
    # for i in range(10000):
    #    rs=  获取tick数据()
    #    print(rs)
