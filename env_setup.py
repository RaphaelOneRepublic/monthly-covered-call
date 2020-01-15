import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

etf_daily = pd.read_excel("data.xlsx")

daily_underlying_close = etf_daily[['date', 'close']]
daily_trading_signal = etf_daily[['date', 'signal']]
daily_premium = etf_daily[[col for col in etf_daily.columns
                           if col == "date" or col.startswith("50ETF")]]

etf_daily.iteritems