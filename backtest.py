from datetime import datetime

import pandas as pd
import math

fee = 5.0
slippage = 5.0
capital = 1500000.0
size = 50
unit_shares = 10000
option_value = 0
security_value = 0
money = capital

holding_security = 0
holding_option = None

etf_daily = pd.read_excel("data/data.xlsx")

trace = pd.DataFrame(columns=
                     ["holding_option", "money", "securities", "options", "capital"])

# Closing prices of the underlying security
daily_underlying_close = etf_daily[['date', 'close']]

# Trading signal
daily_trading_signal = etf_daily[['date', 'signal']]

# Closing price of options
daily_premium = etf_daily.loc[:, [col for col in etf_daily.columns
                                  if col == "date" or col.startswith("50ETF")]]

num_trading_dates = etf_daily.shape[0]

# Subtract one column representing dates
num_options = daily_premium.shape[1] - 1

# Fill in NaN values
# Set to the mean of values of two adjacent dates,
# or the value of the following date in case the previous date also records NaN
for col in daily_premium.columns.drop("date"):
    for i in range(1, num_trading_dates):
        cur = num_trading_dates - 1 - i
        if math.isnan(daily_premium.loc[cur, col]):
            if cur == 0 or math.isnan(daily_premium.loc[cur - 1, col]):
                daily_premium.loc[cur, col] = daily_premium.loc[cur + 1, col]
            else:
                daily_premium.loc[cur, col] = (daily_premium.loc[cur + 1, col] + daily_premium.loc[cur - 1, col]) / 2


def get_underlying_close(_date: datetime):
    return daily_underlying_close[daily_underlying_close.date == _date]["close"].values[0]


def get_call_close(call: str, _date: datetime):
    return daily_premium[daily_premium.date == _date][call].values[0]


def get_at_the_money_call(_date: datetime):
    return etf_daily[etf_daily.date == _date]['call_name'].values[0]


def get_trading_signal(_date):
    return etf_daily[etf_daily.date == _date]['signal'].values[0]


def open_covered_call(call: str, _date: datetime):
    call_close = get_call_close(call, _date)
    underlying_close = get_underlying_close(_date)
    global holding_security, holding_option
    holding_security = 1
    holding_option = call
    revenue = _value_covered_call(call, _date)
    revenue -= 2 * size * fee + 2 * size * slippage / 2
    print("Covered call position opened on %s, underlying price: %s, %s price %f"
          % (_date, underlying_close, call, call_close))
    return revenue


def close_covered_call(call: str, _date: datetime):
    call_close = get_call_close(call, _date)
    underlying_close = get_underlying_close(_date)
    global holding_security, holding_option
    holding_security = 0
    holding_option = None
    revenue = -_value_covered_call(call, _date)
    revenue -= 2 * size * fee + 2 * size * slippage / 2
    print("Covered call position closed on %s, underlying price: %s, %s price %f"
          % (_date, underlying_close, call, call_close))
    return revenue


def _value_covered_call(call: str, _date: datetime):
    call_close = get_call_close(call, _date)
    underlying_close = get_underlying_close(_date)
    revenue = - unit_shares * size * underlying_close + unit_shares * size * call_close
    return revenue


def open_call(call: str, _date: datetime):
    call_close = get_call_close(call, _date)
    revenue = unit_shares * size * call_close
    revenue -= size * fee + size * slippage / 2
    global holding_option
    holding_option = call
    print("Call position opened on %s, %s price: %s"
          % (_date, call, call_close))
    return revenue


def close_call(call: str, _date: datetime):
    call_close = get_call_close(call, _date)
    revenue = - unit_shares * size * call_close
    revenue -= size * fee + size * slippage / 2
    global holding_option
    holding_option = None
    print("Call position closed on %s, %s price: %s"
          % (_date, call, call_close))
    return revenue


for _date in etf_daily.date:
    at_the_money_call = get_at_the_money_call(_date)
    signal = get_trading_signal(_date)
    change = 0
    if signal == 2:
        if holding_security == 0:
            change = open_covered_call(at_the_money_call, _date)
        else:
            change = open_call(at_the_money_call, _date)
    elif signal == 1:
        if holding_option is None:
            change = 0
        else:
            change = close_call(holding_option, _date)
    money += change
    option_value = unit_shares * size * get_call_close(holding_option, _date) if holding_option is not None else 0
    security_value = unit_shares * size * get_underlying_close(_date) if holding_security == 1 else 0
    capital = money - option_value + security_value
    trace.loc[_date] = [holding_option, money, security_value, option_value, capital]

# Uncomment or output Excel
trace.to_excel("output.xlsx", "statistics")
