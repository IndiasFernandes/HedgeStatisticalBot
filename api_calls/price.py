import requests

# Get price for specific Coin
def get_futures_current_price(symbol, client):
    futuresPrice = float(client.futures_symbol_ticker(symbol=symbol)["price"])
    return futuresPrice

# Get price for several Coins (coinsPrice = {} Needed)
def get_futures_current_price_coins(coinsList, client):
    coinsPrice = {}
    # Symbol, Price, Time
    futuresPrice = client.futures_symbol_ticker()
    for coins in coinsList:
        for coin in futuresPrice:
            if str(coin["symbol"]) == coins:
                coinsPrice[coins] = float(coin["price"])
    return coinsPrice
