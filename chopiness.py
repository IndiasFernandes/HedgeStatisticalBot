import pandas as pd
import numpy as np
from config import *
from tradingBot import FuturesHedgeTradingBot
import time

Bot = FuturesHedgeTradingBot(symbol, leverage, initialAmount, trailStopProfit, stopLoss, fee, callBack)

def chopiness_indicator(symbol, timeframe):
    # Download data from Binance API
    klines = Bot.client.futures_klines(symbol=symbol, interval=timeframe)

    # Convert data to a pandas dataframe
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])

    # Convert timestamps to datetime objects
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)

    # Convert 'high' and 'low' columns to numeric type
    df[['high', 'low', 'close', 'open']] = df[['high', 'low', 'close', 'open']].apply(pd.to_numeric)

    # Calculate ATR
    df['tr'] = np.maximum(df['high'] - df['low'], np.abs(df['high'] - df['close'].shift()))
    df['tr'] = np.maximum(df['tr'], np.abs(df['low'] - df['close'].shift()))
    df['atr'] = df['tr'].rolling(10).mean()

    # Calculate RR
    df['hl_range'] = df['high'] - df['low']
    df['hc_range'] = abs(df['high'] - df['close'].shift())
    df['lc_range'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['hl_range', 'hc_range', 'lc_range']].max(axis=1)
    df['rr'] = np.log(df['atr'] / df['tr'])

    # Calculate MRR
    df['mrr'] = df['rr'].rolling(10).mean()

    # Calculate CI
    ci = df['mrr'].sum() / 100

    # Debugging information
    print('CI:', ci, ' | ATR:',df['atr'][-1],' | RR:',df['rr'][-1],' | MRR:', df['mrr'][-1] )

    return ci

while True:
    time.sleep(5)