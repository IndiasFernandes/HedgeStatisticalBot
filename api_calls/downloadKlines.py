import os
import pandas as pd
from binance.enums import HistoricalKlinesType


# Function that gets Klines from Binance (Futures or Spot)
from colorama import Fore
import requests
import pandas as pd

def get_klines(symbols, interval, start, end, type, client):

    colnames = ['time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume',
                'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore']

    if type == 'Spot':
        kline_type = HistoricalKlinesType.SPOT
    elif type == 'Futures':
        kline_type = HistoricalKlinesType.FUTURES

    klines_generator = client.get_historical_klines_generator(
                    symbol=symbols,
                    interval=interval,
                    start_str=start,
                    end_str=end,
                    klines_type=kline_type
                    )  # we will get the generator first


    klines_list = list(klines_generator)  # you can either save the generator directly or convert it to data

    df = pd.DataFrame(klines_list, columns=colnames)  # save as a pandas dataframe

    # print("\033[38;5;76mData Downloaded!\033[0;0m\n")

    return df

def save_klines(df, path, symbol):
    print(df)
    df.to_csv(os.path.join(path + symbol + '.csv'), mode='a', index=False)  # save the file

    print(Fore.GREEN + f'- Data saved ({path + symbol + ".csv"})', end='\n')

# Get timestamp of earliest date data is available
def get_initial_timestamp(client, symbol, timeframe):

    from datetime import datetime
    timestamp = str(client._get_earliest_valid_timestamp(symbol, timeframe))
    timestamp = int(timestamp[:-3])
    dt_object = datetime.fromtimestamp(timestamp)

    return timestamp

def get_last_klines(symbol, exchangeType, interval, limit):

    if exchangeType == 'Spot':
        url = 'https://api.binance.com/api/v3/klines'
    elif exchangeType == 'Futures':
        url = 'https://fapi.binance.com/fapi/v1/klines'

    params = {'symbol': symbol, 'interval': interval, 'limit': limit}

    # Get the data from Binance API
    response = requests.get(url, params=params)
    data = response.json()

    # Convert data to pandas dataframe and clean up
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume',
                                     'taker_buy_quote_asset_volume', 'ignore'])


    df.drop(['timestamp', 'close_time', 'quote_asset_volume', 'num_trades', 'taker_buy_base_asset_volume',
             'taker_buy_quote_asset_volume', 'ignore'], axis=1, inplace=True)

    df = df.astype(float)

    return df



