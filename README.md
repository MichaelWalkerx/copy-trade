# copy-trading-bot

#### 介绍
**币安 | 欧意 跟单带单复制机器**

即使你不是专业交易员，也可以轻松复制专业交易员的带单策略，并且接入到你自己的带单项目，让你也成为专业交易员，享受10%-30%的带单佣金。

#### 实现思路
peek带单员的实时仓位信息，同步到自己的带单项目。可能出现问题，带单员隐藏了带单详情，需要自己跟单之后才能看到仓位。

#### 准备工作
一、币安
1. 登录进入[跟单详情页面](https://www.binance.com/zh-CN/copy-trading)，跟单带单接口都是非官方公开API，F12之后抓一个xhr请求，复制请求为cURL(bash)，之后通过[cURL转requests](https://curlconverter.com/)得到cookies和headers，这个网站仅在本地做转换，可以放心使用。
2. 点击带单者的详情页可以看到，例如[ddbxxb的带单详情](https://www.binance.com/zh-CN/copy-trading/lead-details/3962663535186762752?timeRange=90D)，url的最后那段数字，形如`3962663535186762752`，拿到带单者的id。
3. 开启自己的带单项目，拿到自己的带单id。
4. 创建币安 API Key: [API管理 - 设置 (binance.com)](https://www.binance.com/zh-CN/my/settings/api-management)，安全起见，开启读取权限就行。

二、欧意
1. 创建欧意 API Key: [API - 全球领先的比特币交易平台|okx.com](https://www.okx.com/zh-hans/account/my-api)
2. 挑选带单员：[跟单顶级数字货币交易员 | 欧易 (okx.com)](https://www.okx.com/zh-hans/copy-trading/page/1)

#### 使用方法 
版本要求: python>=3.8
1. 拉取仓库
```
git clone https://gitee.com/DarkCoderX/copy-trading-bot.git
```
2. 安装依赖
```
pip install -r requirements.txt
```
3. 运行脚本
```
python binance_copy_trading_bot.py
python okx_copy_trading_bot.py
```
4. 查看日志
```
tail -f binance_copy_trading_bot.log
tail -f okx_copy_trading_bot.log
```

#### 运行情况
![Alt text](image.png)

#### 群聊
有任何问题可在群里提问 [Twitter](https://x.com/AlgoTraderXX) | [Telegram](https://t.me/algotrader_tg)

#### 恰一口饭 各位随意

<img alt="binance.jpg" height="330" src="binance.jpg" width="200"/><img alt="okx.jpg" height="330" src="okx.jpg" width="200"/>

#### Buy me a coffee

<img alt="receive_code.jpg" height="200" src="receive_code.jpg" width="150"/><img alt="alipay_receive_code.jpg" height="200" src="alipay_receive_code.jpg" width="150"/>