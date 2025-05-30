import pandas as pd
import math

import requests

from config import cookies,headers

session = requests.Session()
session.headers.update(headers)
session.cookies.update(cookies)
def query_leader_list(page_num=1, page_size=20):
    query_info = {
      "pageNumber": page_num,
      "pageSize": page_size,
      "timeRange": "90D",
      "dataType": "AUM",
      "favoriteOnly": False,
      "hideFull": False,
      "nickname": "",
      "order": "DESC",
      "userAsset": 16907.06191725,
      "portfolioType": "PUBLIC"
    }
    url = "https://www.binance.com/bapi/futures/v1/friendly/future/copy-trade/home-page/query-list"
    response = session.post(url, json=query_info).json()
    expected_status_code = '000000'
    assert response['code'] == expected_status_code, f"{response['message']}, {response['messageDetail']}"
    return response['data']

def query_all_leader_list(page_size, total):
    total_info = query_leader_list(1, 1)
    total_size = min(total, total_info['total'])
    all_info_list = []
    for page in range(1, math.floor(total_size / page_size) + 1):
        one_page = query_leader_list(page, page_size)
        all_info_list.extend(one_page['list'])
    return all_info_list
def craw_leader_to_excel():
    leader_info_list = query_all_leader_list(20, 100)
    data_to_write = []
    for info in leader_info_list:
        data_to_write.append({
            'Nickname': info['nickname'],
            'Lead Portfolio ID': info['leadPortfolioId'],
            'AUM': info['aum'],
            'ROI': info['roi'],
            'PNL': info['pnl'],
            'MDD': info['mdd'],
            'Win Rate': info['winRate']
        })

    # 创建 DataFrame
    df = pd.DataFrame(data_to_write)
    excel_file_path = './portfolio_info.xlsx'
    df.to_excel(excel_file_path, index=True)


if __name__ == '__main__':
    craw_leader_to_excel()