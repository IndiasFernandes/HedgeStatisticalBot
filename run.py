from tradingBot import FuturesHedgeTradingBot
from config import *

Bot = FuturesHedgeTradingBot(symbol, leverage, initialAmount, trailStopProfit, stopLoss, fee, callBack)
Bot.openBothSides()
Bot.loopTrade()