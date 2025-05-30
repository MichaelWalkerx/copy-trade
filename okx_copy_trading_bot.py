# from okx.okxclient import OkxClient
# from okx.MarketData import MarketAPI
# from okx.Trade import TradeAPI
# from okx.Account import AccountAPI
# from collections import defaultdict
# import time
# import logging


# leader_data = {
#     "卡皮巴拉（老明星）": "305B2C62DA40873F",
#     "星辰社区": "4CC714DF5A1691A0",
#     "睡觉加躺平": "238CFC2F7265C90D",
#     "韭菜想逆袭": "923F2F72E4A8FAB0",
#     "xmm-luck": "E7FB79AE8F77F63F",
#     "Fiee的逆袭之路": "0D3AE8E34B6A73CF",
#     "Xurry": "C7D37F8092789496",
#     "Plymouth": "A8AF8AFFAB6051B3",
#     "日赚一妹": "0F4CEF2F5248734C",
#     "亿总": "0870A246F3749D76",
#     # 我的名称
#     "AlgoTrader": "CF61BFD782AF8D9F",
# }

# leader_unique_name = leader_data['Xurry']
# my_unique_name = leader_data['AlgoTrader']

# # 配置自己的okx主账户api key 需要交易权限
# apikey = ""
# secretkey = ""
# passphrase = ""
# flag = "0"  # 实盘:0 模拟盘:1

# enable_slippage_protection = False
# slippage = 0.1

# # 同步周期 1代表1s一次
# sync_wait_time = 1

# # 日志级别配置
# logging.basicConfig(
#     filename='./okx_copy_trading_bot.log',
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
# )
# logger = logging.getLogger(__name__)

# okx_client = OkxClient(apikey, secretkey, passphrase, False, flag, debug=False)
# account_api = AccountAPI(apikey, secretkey, passphrase, False, flag, debug=False)
# marketAPI = MarketAPI(apikey, secretkey, passphrase, False, flag, debug=False)
# tradeAPI = TradeAPI(apikey, secretkey, passphrase, False, flag, debug=False)


# def fetch_leader_detail(leader_unique_code):
#     url = '/api/v5/copytrading/public-stats'
#     params = {
#         "instType": "SWAP",
#         "uniqueCode": leader_unique_code,
#         "lastDays": 4 # 1代表7 2代表30 3代表90 4代表365
#     }
#     rsp = okx_client._request_with_params("GET", url, params)
#     assert rsp['code'] == '0', f"{rsp['msg']}"
#     data = rsp['data'][0]
#     return data


# def fetch_leader_cur_positions(leader_unique_code):
#     url = '/api/v5/copytrading/public-current-subpositions'
#     params = {
#         "instType": "SWAP",
#         "uniqueCode": leader_unique_code,
#     }
#     rsp = okx_client._request_with_params("GET", url, params)
#     assert rsp['code'] == '0', f"{rsp['msg']}"
#     return summary_positions(rsp['data'])


# def fetch_my_cur_positions(my_unique_code=None, is_leader=True, inst_type="SWAP"):
#     url = '/api/v5/copytrading/current-subpositions'
#     params = {
#         "uniqueCode": my_unique_code,
#         "instType": inst_type,
#         "subPosType": "lead" if is_leader else "copy"
#     }
#     rsp = okx_client._request_with_params("GET", url, params)
#     assert rsp['code'] == '0', f"{rsp['msg']}"
#     return summary_positions(rsp['data'])


# def summary_positions(leader_position_list):
#     summary_list = []
#     separator = "_"
#     summary = defaultdict(
#         lambda: {'total_cost': 0, 'total_pos': 0, 'total_margin': 0, 'total_lever': 0, 'total_upl': 0})

#     for leader_position in leader_position_list:
#         # 产品ID 例如BTC-USDT-SWAP
#         inst_id = leader_position['instId']
#         # 计价单位
#         ccy = leader_position['ccy']
#         # 产品类型 SPOT：币币 SWAP：永续合约
#         inst_type = leader_position['instType']
#         # 杠杆
#         lever = float(leader_position['lever'])
#         # 保证金
#         margin = float(leader_position['margin'])
#         # 最新标记价格，仅适用于合约
#         mark_px = leader_position['markPx']
#         # 保证金模式，isolated：逐仓 ；cross：全仓
#         mgn_mode = leader_position['mgnMode']
#         # 开仓均价
#         open_avg_px = float(leader_position['openAvgPx'])
#         # 开仓时间
#         open_time = leader_position['openTime']
#         # 持仓方向 long：开平仓模式开多 short：开平仓模式开空 net：买卖模式（subPos为正代表开多，subPos为负代表开空）
#         pos_side = leader_position['posSide']
#         # 持仓张数
#         sub_pos = float(leader_position['subPos'])
#         # 未实现收益
#         upl = float(leader_position['upl'])
#         # 未实现收益率
#         upl_ratio = leader_position['uplRatio']

#         group_key_list = [inst_id, ccy, inst_type, pos_side, mgn_mode, mark_px]
#         primary_key = separator.join(group_key_list)
#         summary[primary_key]['total_cost'] += open_avg_px * sub_pos
#         summary[primary_key]['total_pos'] += sub_pos
#         summary[primary_key]['total_margin'] += margin
#         summary[primary_key]['total_lever'] += lever * sub_pos
#         summary[primary_key]['total_upl'] += upl

#     average_open_prices = {}
#     average_leverages = {}
#     for primary_key, totals in summary.items():
#         if totals['total_pos'] != 0:
#             average_open_prices[primary_key] = totals['total_cost'] / totals['total_pos']
#             average_leverages[primary_key] = totals['total_lever'] / totals['total_pos']
#         else:
#             average_open_prices[primary_key] = 0
#             average_leverages[primary_key] = 0

#     # 打印结果
#     for primary_key, avg_price in average_open_prices.items():
#         [inst_id, ccy, inst_type, pos_side, mgn_mode, mark_px] = primary_key.split(separator)
#         summary_position_info = {
#             'ccy': ccy,
#             'instId': inst_id,
#             'instType': inst_type,
#             'lever': average_leverages[primary_key],
#             'margin': summary[primary_key]['total_margin'],
#             'markPx': mark_px,
#             'mgnMode': mgn_mode,
#             'openAvgPx': average_open_prices[primary_key],
#             'posSide': pos_side,
#             'subPos': summary[primary_key]['total_pos'],
#             'upl': summary[primary_key]['total_upl']
#         }
#         summary_list.append(summary_position_info)
#     return summary_list


# def fetch_leverage(inst_id, mgn_mode):
#     rsp = account_api.get_leverage(inst_id, mgn_mode)
#     assert rsp['code'] == '0', f"{rsp['msg']}"
#     return rsp['data']


# def is_same_leverage(leverage_dict, _symbol, expected_mgn_mode, expected_leverage, expected_pos_side):
#     return len([item for item in leverage_dict if item.get('instId') == _symbol and item.get("mgnMode") == expected_mgn_mode and float(item.get("lever")) == expected_leverage and item.get("posSide") == expected_pos_side]) > 0


# def adjust_leverage(inst_id, mgn_mode, leverage, position_side):
#     rsp = account_api.set_leverage(lever=leverage, mgnMode=mgn_mode, instId=inst_id, posSide=position_side)
#     assert rsp['code'] == '0', f"{rsp['msg']}"
#     return rsp['data']


# def print_leader_detail(leader_detail):
#     logger.info(f"================带单员===================")
#     logger.info(f"胜率: {float(leader_detail['winRatio']) * 100:.2f}%")
#     logger.info(f"带单保证金: {leader_detail['investAmt']}")
#     logger.info("=========================================\n")


# def print_leader_position(summary_position_list):
#     logger.info(f"================持仓信息===================")
#     for position in summary_position_list:
#         logger.info("---------------------------------")
#         logger.info(
#             f"{'空' if (position['posSide'] == 'net' and position['subPos'] < 0) else '多'} {position['instId']}{'现货' if position['instType'] == 'SPOT' else '永续'} {'逐仓' if position['mgnMode'] == 'isolated' else '全仓'}{position['lever']}倍")
#         logger.info(
#             f"未实现盈亏: {position['upl']} {position['ccy']} 持仓数量: {position['subPos']}  保证金: {position['margin']}")
#         logger.info(f"开仓均价: {position['openAvgPx']} 标记价格: {position['markPx']}")
#         logger.info("---------------------------------")
#     logger.info("=========================================\n\n")


# def sync_position():
#     leader_detail = fetch_leader_detail(leader_unique_name)
#     leader_margin_balance = float(leader_detail['investAmt'])
#     leader_cur_positions = fetch_leader_cur_positions(leader_unique_name)

#     print_leader_detail(leader_detail)
#     print_leader_position(leader_cur_positions)

#     my_detail = fetch_leader_detail(my_unique_name)

#     my_margin_balance = float(my_detail['investAmt'])
#     my_cur_open_position = fetch_my_cur_positions(my_unique_name)
#     print_leader_detail(my_detail)
#     print_leader_position(my_cur_open_position)

#     for leader_position in leader_cur_positions:
#         leader_symbol = leader_position['instId']
#         if leader_position['posSide'] == 'net':
#             if leader_position["subPos"] < 0:
#                 leader_position_side = "SHORT"
#             else:
#                 leader_position_side = "LONG"
#         else:
#             leader_position_side = leader_position['posSide'].upper()
#         leader_position_amount = abs(leader_position['subPos'])
#         leader_entry_price = leader_position['openAvgPx']
#         leader_leverage = leader_position['lever']
#         leader_isolated = leader_position['mgnMode']
#         leader_ccy = leader_position['ccy']

#         my_should_hold_position_amount = leader_position_amount * my_margin_balance / leader_margin_balance

#         # 判断我是否有同品种同方向同种模式仓位
#         my_same_side_symbol_position = [item for item in my_cur_open_position if
#                                         item.get('instId') == leader_symbol and item.get(
#                                             'posSide') == leader_position['posSide'] and item.get('mgnMode') == leader_isolated]

#         if len(my_same_side_symbol_position) > 1:
#             logger.error("存在多条同品种同方向仓位历史数据，请关注")
#             continue

#         my_leverage_dict = fetch_leverage(leader_symbol, leader_isolated)
#         # 杠杆对齐
#         if not is_same_leverage(my_leverage_dict, leader_symbol, leader_isolated, leader_leverage, leader_position['posSide']):
#             logger.info(f"调整 {leader_symbol} 杠杆数量和带单员一致: {leader_leverage}倍")
#             adjust_leverage(leader_symbol, leader_isolated, leader_leverage, leader_position['posSide'])

#         command = None
#         quantity = 0
#         my_position_amount = 0

#         if len(my_same_side_symbol_position) == 1:
#             # 已有仓位，检查同方向同品种的持仓数据是否有变化
#             my_position_info = my_same_side_symbol_position[0]
#             my_position_amount = abs(my_position_info['subPos'])

#             position_amount_diff = my_should_hold_position_amount - my_position_amount
#             if position_amount_diff < 0:
#                 # 仓位过大 减仓
#                 command = "CLOSE"
#             elif position_amount_diff > 0:
#                 # 仓位过小 加仓
#                 command = "OPEN"
#             quantity = abs(position_amount_diff)
#         else:
#             # 新增仓位
#             command = "OPEN"
#             quantity = my_should_hold_position_amount

#         # 带单员新增的仓位 全仓
#         cur_price = marketAPI.get_ticker(leader_symbol)['data'][0]['askPx']
#         if enable_slippage_protection:
#             if leader_position_side == 'SHORT' and (float(leader_entry_price) - float(cur_price)) > slippage:
#                 continue
#             if leader_position_side == 'LONG' and (float(cur_price) - float(leader_entry_price)) > slippage:
#                 continue
#         if command is not None and quantity / my_should_hold_position_amount > 0.05:
#             logger.info(
#                 f"{leader_symbol} 应该持仓: {my_should_hold_position_amount} 实际持仓: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {quantity} 价格: {cur_price}")
#             side = None
#             if command == "OPEN" and leader_position_side == "LONG":
#                 side = 'buy'
#             if command == "CLOSE" and leader_position_side == "LONG":
#                 side = 'sell'
#             if command == "OPEN" and leader_position_side == "SHORT":
#                 side = 'sell'
#             if command == "CLOSE" and leader_position_side == "SHORT":
#                 side = 'buy'
#             rsp = tradeAPI.place_order(instId=leader_symbol,
#                                               tdMode=leader_isolated,
#                                               ccy=leader_ccy,
#                                               posSide=leader_position_side.lower(),
#                                               side=side,
#                                               sz=round(quantity, 1),
#                                               ordType='market')
#             assert rsp['code'] == '0', f"{rsp['msg']}"
#             logger.info("Order placed")

#     for my_position in my_cur_open_position:
#         my_symbol = my_position['instId']
#         if my_position['posSide'] == 'net':
#             if my_position["subPos"] < 0:
#                 my_position_side = "SHORT"
#             else:
#                 my_position_side = "LONG"
#         else:
#             my_position_side = my_position['posSide'].upper()
#         my_position_amount = abs(my_position['subPos'])
#         my_leverage = my_position['lever']
#         my_isolated = my_position['mgnMode']
#         my_same_side_symbol_position = [item for item in leader_cur_positions if
#                                         item.get('instId') == my_symbol and item.get(
#                                             'posSide') == my_position['posSide'] and item.get('mgnMode') == my_isolated]
#         if len(my_same_side_symbol_position) != 0:
#             continue
#         # 我比带单员多出来的仓位 全部平仓
#         cur_price = marketAPI.get_ticker(my_symbol)['data'][0]['askPx']
#         command = "CLOSE"
#         logger.info(
#             f"{my_symbol} 应该持仓: 0 实际持仓: {my_position_amount} {'加仓' if command == 'OPEN' else '减仓'}: {my_position_amount} 价格: {cur_price}")
#         side = None
#         if command == "OPEN" and my_position_side == "LONG":
#             side = 'buy'
#         if command == "CLOSE" and my_position_side == "LONG":
#             side = 'sell'
#         if command == "OPEN" and my_position_side == "SHORT":
#             side = 'sell'
#         if command == "CLOSE" and my_position_side == "SHORT":
#             side = 'buy'
#         rsp = tradeAPI.place_order(instId=my_symbol,
#                                           tdMode=my_isolated,
#                                           ccy=my_position['ccy'],
#                                           posSide=my_position_side.lower(),
#                                           side=side,
#                                           sz=round(my_position_amount, 1),
#                                           ordType='market')
#         assert rsp['code'] == '0', f"{rsp['msg']}"
#         logger.info("Order placed")


# if __name__ == "__main__":
#     while True:
#         sync_position()
#         time.sleep(sync_wait_time)

