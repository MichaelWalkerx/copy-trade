import requests
from config import cookies,headers

session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)

# 定义函数：获取指定投资组合的持仓信息
def fetch_portfolio(portfolio_id):
    params = {
        'portfolioId': portfolio_id, # 请求参数：投资组合ID
    }
    url = 'https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-data/positions' # API请求URL
    response = session.get(url, params=params).json() # 发送GET请求并解析JSON响应
    expected_status_code = '000000' # 期望的成功状态码
    # 断言：检查响应状态码是否为期望值，否则抛出错误
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"
    return response['data'] # 返回响应中的数据部分


# 定义函数：获取用户信息
def fetch_userinfo():
    """
    获取当前用户的基本信息。

    Returns:
        dict: 包含用户信息的字典。
    """
    url = "https://www.binance.com/bapi/futures/v1/private/future/copy-trade/home-page/user-info" # API请求URL
    response = session.get(url).json() # 发送GET请求并解析JSON响应
    expected_status_code = '000000' # 期望的成功状态码
    # 断言：检查响应状态码是否为期望值，否则抛出错误
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"
    return response['data'] # 返回响应中的数据部分


# 定义函数：获取带单员详情
# {'code': '000000', 'data': {'aumAmount': '3027744.36253720', 'marginBalance': '76683.15410411'}
def fetch_leader_detail(portfolio_id):
    params = {
        'portfolioId': portfolio_id, # 请求参数：投资组合ID
    }
    url = "https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/lead-portfolio/detail" # API请求URL
    response = session.get(url, params=params).json() # 发送GET请求并解析JSON响应
    expected_status_code = '000000' # 期望的成功状态码
    # 断言：检查响应状态码是否为期望值，否则抛出错误
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"
    return response['data'] # 返回响应中的数据部分


# 定义函数：获取指定投资组合的杠杆信息
def fetch_leverage(portfolio_id):
    query_body = {
      "copyTradeType": "PUB_LEAD", # 跟单类型：公开带单
      "portfolioId": portfolio_id # 投资组合ID
    }
    url = "https://www.binance.com/bapi/futures/v1/private/future/user-data/userLeverage" # API请求URL
    response = session.post(url, json=query_body).json() # 发送POST请求并解析JSON响应
    expected_status_code = '000000' # 期望的成功状态码
    # 断言：检查响应状态码是否为期望值，否则抛出错误
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"
    return response['data'] # 返回响应中的数据部分


# 定义函数：调整杠杆
def adjust_leverage(symbol, portfolio_id, leverage=5):
    leverage_info = {
      "symbol": symbol, # 交易对符号
      "leverage": leverage, # 杠杆倍数
      "copyTradeType": "PUB_LEAD", # 跟单类型：公开带单
      "portfolioId": portfolio_id # 投资组合ID
    }
    url = "https://www.binance.com/bapi/futures/v1/private/future/user-data/adjustLeverage" # API请求URL
    response = session.post(url, json=leverage_info).json() # 发送POST请求并解析JSON响应
    expected_status_code = '000000' # 期望的成功状态码
    # 断言：检查响应状态码是否为期望值，否则抛出错误
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"



followed_leader_id = '4466349480575764737'  # 要跟随的带单员的ID

if __name__ == '__main__':
    # rs = fetch_leader_detail(followed_leader_id)
    rs = fetch_portfolio(followed_leader_id)
    print(rs)