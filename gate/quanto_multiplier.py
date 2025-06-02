# # coding: utf-8
# import requests
# import time
# import hashlib
# import hmac
# def gen_sign(method, url, query_string=None, payload_string=None):
#     key = '25b205ed26fbfb4ef1b69aeabe789cbc'        # api_key
#     secret = '7476587dadfa09aee744f8dc9e273b508921a0da7a865a2ce18082e3427b79a1'     # api_secret
#
#     t = time.time()
#     m = hashlib.sha512()
#     m.update((payload_string or "").encode('utf-8'))
#     hashed_payload = m.hexdigest()
#     s = '%s\n%s\n%s\n%s\n%s' % (method, url, query_string or "", hashed_payload, t)
#     sign = hmac.new(secret.encode('utf-8'), s.encode('utf-8'), hashlib.sha512).hexdigest()
#     return {'KEY': key, 'Timestamp': str(t), 'SIGN': sign}
#
#
# host = "https://api.gateio.ws"
# prefix = "/api/v4"
# headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
#
# def 查询所有合约信息():
#
#     headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
#
#     url = '/futures/usdt/contracts'
#     query_param = ''
#     r = requests.request('GET', host + prefix + url, headers=headers)
#     print(r.json())
#     return r.json()
#
#
#
# if __name__ == '__main__':
#     contract_list = 查询所有合约信息()
#     # 查询账户余额()
#     # print(contract_list)
#
#     quanto_multipliers = {}
#     for contract in contract_list:
#         if 'name' in contract and 'quanto_multiplier' in contract:
#             quanto_multipliers[contract['name']] = contract['quanto_multiplier']
#
#     # 将字典写入到 Python 文件中
#     with open('D:\跟单\copy-trade\gate\contract_quanto_multipliers.py', 'w', encoding='utf-8') as f:
#         f.write("contract_quanto_multipliers = ")
#         import json
#         json.dump(quanto_multipliers, f, indent=4)