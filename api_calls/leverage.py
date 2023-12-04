def change_lev(client, symbol, leverage):

    try:
        client.futures_change_leverage(symbol=symbol,
                                       leverage=leverage)
        # print(f'Sold {quantity} of {symbol}')
        print(f'Leverage of {symbol} changed to {leverage}')
    except:

        print(f"Didn't change leverage of {symbol}")

    return int(leverage)

