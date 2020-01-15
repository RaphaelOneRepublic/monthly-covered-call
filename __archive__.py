import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import *
import math

etf_close = pd.read_excel("50etf.xlsx", "premium")
lastdate = pd.read_excel("50etf.xlsx", "last_trading_date")
etf_option_name = pd.read_excel("50etf.xlsx", "option_name")
underlying_close = pd.read_excel("50etf.xlsx", "20HV")

# 填补缺失值
for j in range(1, len(etf_close.columns.tolist())):
    for i in range(len(etf_close.date.values.tolist()) - 1, 0, -1):
        if math.isnan(etf_close.iat[i, j]) and math.isnan(etf_close.iat[i - 1, j]):
            etf_close.iat[i, j] = etf_close.iat[i + 1, j]
        elif math.isnan(etf_close.iat[i, j]) and math.isnan(etf_close.iat[i - 1, j]) == False:
            etf_close.iat[i, j] = (etf_close.iat[i - 1, j] + etf_close.iat[i + 1, j]) / 2

fee = 5.0
slippage = 5.0
capital = 1000000.0
size = 50
option_value = 0
remain_money = capital
total_money = [remain_money]
trade_option = pd.DataFrame()
# 回测参数设置
open_b = 1.5
close_b = 0.0001

d = []
trade_content = []
trade_posit = []


def coverd_call(call_name, date, posit):
    global size, trade_option
    call_close = etf_close[etf_close.date == date][call_name].values[0]
    ETF50_close = underlying_close[underlying_close.date == date]["close"].values[0]

    if posit == "open_covered_call":
        num = size
        d.append(date)
        trade_content.append("buy 50ETF and sell" + str(call_name))
        trade_posit.append("buy underlying and sell call")
        print(str(date) + "buy 50ETF and sell" + str(call_name))
        money_chg = -10000 * size * ETF50_close + 10000 * size * call_close
    elif posit == "close_covered_call":
        num = size
        d.append(date)
        trade_content.append("sell 50ETF and buy" + str(call_name))
        trade_posit.append("sell underlying and buy call")
        print(str(date) + "sell 50ETF and buy" + str(call_name))
        money_chg = 10000 * size * ETF50_close - 10000 * size * call_close
    return money_chg - 2 * size * fee - 2 * size * slippage / 2


# 判断开平仓交易：
def trade(date):
    global remain_money
    call_name = etf_option_name[etf_option_name.date == date]["call"].values[0]
    option_value = 0
    # 开仓
    if lastdate[lastdate.trading_date == date]["signal"].values[0] == 2:
        ETF50_close = underlying_close[underlying_close.date == date]["close"].values[0]
        call_close = etf_close[etf_close.date == date][call_name].values[0]
        posit = "open_covered_call"
        change = coverd_call(call_name, date, posit)
        option_value = option_value - 10000 * size * ETF50_close + 10000 * size * call_close
    # 平仓
    elif lastdate[lastdate.trading_date == date]["signal"].values[0] == 1:
        ETF50_close = underlying_close[underlying_close.date == date]["close"].values[0]
        call_close = etf_close[etf_close.date == date][call_name].values[0]
        posit = "close_covered_call"
        change = coverd_call(call_name, date, posit)
        option_value = option_value + 10000 * size * ETF50_close - 10000 * size * call_close
    else:
        change = 0

    remain_money += change
    total_money.append(remain_money + option_value)


day = []
for date in etf_option_name.date.values:
    trade(date)  # 这是全部代码最核心的部分，date取好了开始运行trade(date)函数
    date = pd.to_datetime(str(date)).strftime('%Y-%m-%d')  # date为字符串
    date = datetime.strptime(date, "%Y-%m-%d")
    day.append(date)

print(total_money)
print(len(total_money))
DAY_MAX = len(total_money)

# def calculate_performance():
#     rtn = total_money[-1]/capital - 1
#     max_drawdown_ratio = 0
#     for e,i in enumerate(total_money):
#         for h,j in enumerate(total_money):
#             if h>e and float((j-i)/i) < max_drawdown_ratio:
#                 max_drawdown_ratio = float((j-i)/i)

plt.figure(figsize=(8, 5))
plt.plot(day, total_money[1:])
plt.show()
