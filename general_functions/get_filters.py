def get_futures_filters(client, symbol):
    futures = client.futures_exchange_info()
    for sym in futures['symbols']:
        if sym['symbol'] == symbol:
            return sym['quantityPrecision'], sym['pricePrecision'], sym['baseAssetPrecision'], sym['quotePrecision']

