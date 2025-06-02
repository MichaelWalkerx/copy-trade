# coding: utf-8
import requests
import time
import hashlib
import hmac

from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder, Transfer, WalletApi



gate_apiclient = ApiClient()
class RunConfig(object):
    def __init__(self, api_key=None, api_secret=None, host_used=None):
        # type: (str, str, str) -> None
        self.api_key = api_key
        self.api_secret = api_secret
        self.host_used = host_used
        self.use_test = "https://api-testnet.gateapi.io"
run_config = RunConfig("91b7b7897be9d71073fa898208f1c9aa","98cd59e4273d77a18219166b4fc27cad0dbefbe751f44f454458d1fca84941dc")

config = Configuration(key=run_config.api_key, secret=run_config.api_secret, host=run_config.host_used)
futures_api = FuturesApi(ApiClient(config))

def gen_sign(method, url, query_string=None, payload_string=None):
    # key = '25b205ed26fbfb4ef1b69aeabe789cbc'        # api_key
    # secret = '7476587dadfa09aee744f8dc9e273b508921a0da7a865a2ce18082e3427b79a1'     # api_secret
    key = '91b7b7897be9d71073fa898208f1c9aa'        # 模拟盘小号
    secret = '98cd59e4273d77a18219166b4fc27cad0dbefbe751f44f454458d1fca84941dc'     # api_secret

    t = time.time()
    m = hashlib.sha512()
    m.update((payload_string or "").encode('utf-8'))
    hashed_payload = m.hexdigest()
    s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
    sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
    return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}


# host = "https://api.gateio.ws"
host = "https://api-testnet.gateapi.io"
prefix = "/api/v4"
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

def 获取仓位列表():
    # host = "https://api-testnet.gateapi.io"

    url = '/futures/usdt/positions'
    query_param = ''
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers)
    json = r.json()
    list = {}
    for item in json:
        if item['value'] != '0':
            list[len(list)] = item
            print(f'当前仓位列表 :{item['contract']} 价值:{ item['value']} -- 杠杆倍数{item['cross_leverage_limit']}')
    return json

def 查询账户余额():
    url = '/futures/usdt/accounts'
    query_param = ''
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('GET', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('GET', host + prefix + url, headers=headers)
    json = r.json()
    print(f'当前账户可用余额(包含未实现盈亏): {json['cross_margin_balance']}')
    return json


def 变更杠杆倍数(contract,cross_leverage_limit):
    url = f'/futures/usdt/dual_comp/positions/{contract}/leverage'
    query_param = f'leverage=0&cross_leverage_limit={cross_leverage_limit}'
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('POST', prefix + url, query_param)
    headers.update(sign_headers)
    r = requests.request('POST', host + prefix + url + "?" + query_param, headers=headers)
    print(r.json())

def 获取指定币的价格(contracts):
    url = f'/futures/usdt/contracts/{contracts}'
    r = requests.request('GET', host + prefix + url, headers=headers)
    return r.json()['index_price']

def gate开单(contracts,size,price=None):
    order = {}
    if price is None:
        # 市价委托
        print("市价开单")
        order = {
            "contract": contracts,
            "size": size,
            "price": "0",
            "tif": "ioc",
            "text": "t-my-custom-id",
            "stp_act": "-"
        }
    else:
        # 限价委托模板
        print("限价开单")
        order = {
            "contract": contracts,
            "size": size,
            "price": price,
            "tif": "gtc",
            "text": "t-my-custom-id",
            "stp_act": "-"
        }

    url = '/futures/usdt/orders'
    query_param = ''
    # body = '{"contract":"BTC_USDT","size":1,"price":"0","tif":"ioc","text":"自定义的开单ID t-my-custom-id","stp_act":"-"}'
    body = str(order)
    # '{"contract":"BTC_USDT","size":-2,"price":"104318.2","tif":"gtc","text":"t-my-custom-id","stp_act":"-"}'
    # `gen_sign` 的实现参考认证一章
    sign_headers = gen_sign('POST', prefix + url, query_param, body)
    headers.update(sign_headers)
    r = requests.request('POST', host + prefix + url, headers=headers, data=body)
    print(r.json())

if __name__ == '__main__':
    list =  gate开单('BTC_USDT',3)
    print(list)
    # list =  获取仓位列表()
    # print(list)
    # # 查询账户余额()
    # 变更杠杆倍数('FARTCOIN_USDT','2')