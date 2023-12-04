import pandas as pd

def get_futures_positions_information(client):

    # Search for Open Orders
    futureInfo = client.futures_position_information()

    trades = {}

    for info in futureInfo:

        if float(info["positionAmt"]) > 0:
            symbol = info["symbol"]
            positionAmt = float(info["positionAmt"])
            side = "Long"
            trades[symbol] = [positionAmt, side]

        elif float(info["positionAmt"]) < 0:
            symbol = info["symbol"]
            positionAmt = float(info["positionAmt"])
            side = "Short"
            trades[symbol] = [positionAmt, side]

    return trades

def get_futures_account_trades(client, symbol):

    # Search for Latest Trades for specific symbol
    account = client.futures_account_trades(symbol=symbol)
    df = pd.DataFrame.from_dict(account)

    if not df.empty:
        df = df.drop(
            ['id', 'marginAsset', 'quoteQty', 'buyer', 'maker', 'commissionAsset', 'time', 'symbol'],
            axis=1)

    return df

def get_futures_trade_pnl_and_comission(client, symbol, orderIdInitial, orderId2limit):

    account = client.futures_account_trades(symbol=symbol)
    realizedPnl1, comission1, quantityTrade, realizedPnl2, comission2 = 0, 0, 0, 0, 0

    for info in account:
        if info['orderId']==orderIdInitial:
            realizedPnl1 = float(info["realizedPnl"])
            comission1 = float(info["commission"])
            quantityTrade = float(info['qty'])
        if info['orderId']==orderId2limit:
            realizedPnl2 = float(info["realizedPnl"])
            comission2 = float(info["commission"])

    finalPnl = realizedPnl1 + realizedPnl2
    finalComission = comission1 + comission2

    return finalPnl, finalComission, quantityTrade


