import pandas as pd

def get_futures_account_balance(client):
    # Search for Open Orders
    account = client.futures_account_balance()
    df = pd.DataFrame.from_dict(account)

    if not df.empty:
        df = df.drop(
            ['accountAlias', 'updateTime'],
            axis=1)

    return df

def get_futures_trades(client):
    # Search for Open Orders
    account = client.futures_account_trades()
    df = pd.DataFrame.from_dict(account)

    if not df.empty:
        df = df.drop(
            ['id', 'marginAsset', 'quoteQty', 'time', 'buyer'],
            axis=1)

    return df

def change_futures_margin_mode(client, symbol, marginType):
    try:
        if marginType == 'Isolated':
            client.futures_change_margin_type(symbol=symbol,
                                       marginType='ISOLATED')
            print(f'Margin Type of {symbol} changed to {marginType}')
        elif marginType == 'Cross':
            client.futures_change_margin_type(symbol=symbol,
                                              marginType='CROSS')
            print(f'Margin Type of {symbol} changed to {marginType}')
    except:

        print(f"Didn't change Margin Type of {symbol}")

    return marginType



