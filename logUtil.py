import logging # 导入logging库，用于记录日志
# 日志级别配置
logging.basicConfig(
    filename='./log.log', # 日志文件名
    level=logging.INFO, # 日志记录级别设置为INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # 日志格式
)
logger = logging.getLogger(__name__) # 获取一个logger实例


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
