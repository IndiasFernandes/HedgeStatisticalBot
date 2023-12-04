from api_calls.connect import connect_binance
from api_calls.leverage import change_lev
from api_calls.orders import market_long_hedge_futures, stop_order_long_futures, \
    market_short_hedge_futures, stop_order_short_futures, take_profit_long_futures, take_profit_short_futures, \
    get_futures_symbol_open_orders, cancel_all_futures_orders, cancel_futures_order, trailing_stop_long_futures, \
    trailing_stop_short_futures
from api_calls.price import get_futures_current_price
from api_calls.trades import get_futures_account_trades, get_futures_trade_pnl_and_comission
from general_functions.get_filters import get_futures_filters
import colorama
from colorama import Fore, Back, Style
import time
# Initialize colorama
colorama.init(autoreset=True)

class FuturesHedgeTradingBot():
    def __init__(self, symbol, leverage, initialAmount, takeProfit, stopLoss, fee, callBackRate):
        self.client = connect_binance()
        self.symbol = symbol.upper()
        self.leverage = change_lev(self.client, self.symbol, leverage)
        self.quantityPrecision, self.pricePrecision, self.baseAssetPrecision, self.quoteAssetPrecision = get_futures_filters(self.client, symbol)
        self.initialAmount = initialAmount
        self.takeProfit = takeProfit
        self.stopLoss = stopLoss
        self.fee = fee
        self.callBackRate = callBackRate

    def runHedgeBot(self):

        # Print Welcome Text
        print(Fore.WHITE + Back.BLACK + Style.DIM + ' Welcome to Futures Binance Bot ')

        answer = ''
        while answer != 'y':
            print(Style.DIM + '\nIMPORTANT: Please verify that: '
                              '\n- All your positions are closed '
                              '\n- All your orders are closed'
                              '\n- You have more than 10 USDT/BUSD in your account')
            answer = input('\nAre you ready to start the bot? "y"\n')

    def openBothSides(self):

        # Cancel all open orders
        cancel_all_futures_orders(self.client, self.symbol)

        # Get the current coin price
        price = get_futures_current_price(self.symbol, self.client)
        amountInCurrency = round((self.initialAmount / price) * self.leverage, self.quantityPrecision)

        # Create the two initial market orders
        self.orderL = market_long_hedge_futures(self.client, amountInCurrency, self.symbol, 'Buy')['orderId']
        self.orderS = market_short_hedge_futures(self.client, amountInCurrency, self.symbol, 'Sell')['orderId']


        # Define Take Profit for Long Position
        self.priceLTP = price * (1 + (((self.takeProfit) / 100) / self.leverage))
        self.priceLTP = round(self.priceLTP, self.pricePrecision)
        # print(f'takeProfitPriceLong = {takeProfitPriceLong}')

        # Define Trailing Stop for Short Position
        self.priceSTP = price * (1 - (((self.takeProfit) / 100) / self.leverage))
        self.priceSTP = round(self.priceSTP, self.pricePrecision)
        # print(f'takeProfitPriceShort = {takeProfitPriceShort}')

        # Define Stop Loss for Long Position
        self.priceLSL = price * (1 - (((self.stopLoss) / 100) / self.leverage))
        self.priceLSL = round(self.priceLSL, self.pricePrecision)
        # print(f'stopLossPriceLong = {stopLossPriceLong}')

        # Define Stop Loss for Short Position
        self.priceSSL = price * (1 + (((self.stopLoss) / 100) / self.leverage))
        self.priceSSL = round(self.priceSSL, self.pricePrecision)
        # print(f'stopLossPriceShort = {stopLossPriceShort}')

        # Set the Stop Losses
        self.orderLSL = stop_order_long_futures(self.client, amountInCurrency, self.symbol, 'Sell', self.priceLSL)['orderId']
        # print(f'orderLSL = {self.orderLSL}')
        self.orderSSL = stop_order_short_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceSSL)['orderId']
        # print(f'orderSSL = {self.orderSSL}')

        # Set the Trailing Stop Profits
        self.orderLTP = trailing_stop_long_futures(self.client, amountInCurrency, self.symbol, 'Sell', self.priceLTP, self.callBackRate)['orderId']
        # print(f'orderLTP = {self.orderLTP}')
        self.orderSTP = trailing_stop_short_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceSTP, self.callBackRate)['orderId']
        # print(f'orderSTP = {self.orderSTP}')

    def loopTrade(self):

        while True:
            listOpenOrders = get_futures_symbol_open_orders(self.client, self.symbol)['orderId'].to_list()

            # IF Short Position is closed on Stop Loss
            self.orderStateSSL = self.checkOrder(self.orderSSL, listOpenOrders)
            if self.orderStateSSL == 'Closed':
                cancel_futures_order(self.client, self.orderSTP, self.symbol)

                # Get the current coin price and calculate half the profit
                price = get_futures_current_price(self.symbol, self.client)
                amountInCurrency = round(self.initialAmount, self.quantityPrecision)

                # Create Short Market Order with Half Profit
                self.orderS = market_short_hedge_futures(self.client, amountInCurrency, self.symbol, 'Sell')

                # Define Trailing Stop
                self.priceSTP = price * (1 - (((self.takeProfit ) / 100) / self.leverage))
                self.priceSTP = round(self.priceSTP, self.pricePrecision)

                # Define Stop Loss
                self.priceSSL = price * (1 + (((self.stopLoss ) / 100) / self.leverage))
                self.priceSSL = round(self.priceSSL, self.pricePrecision)

                # Set Stop-Loss
                self.orderSSL = \
                stop_order_short_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceSSL)['orderId']

                # Set Trailing Stop
                self.orderSTP = \
                trailing_stop_short_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceSTP,
                                            self.callBackRate)['orderId']

                self.orderStateSSL = 'Open'

            # IF Long Position is closed on Stop Loss
            self.orderStateLSL = self.checkOrder(self.orderLSL, listOpenOrders)
            if self.orderStateLSL == 'Closed':
                cancel_futures_order(self.client, self.orderLTP, self.symbol)

                amountInCurrency = round(self.initialAmount, self.quantityPrecision)

                # Create Long Market Order with Half Profit
                self.orderL = market_long_hedge_futures(self.client, amountInCurrency, self.symbol, 'Buy')

                # Define Trailing Stop
                self.priceLTP = price * (1 + (((self.takeProfit ) / 100) / self.leverage))
                self.priceLTP = round(self.priceLTP, self.pricePrecision)

                # Define Stop Loss
                self.priceLSL = price * (1 - (((self.stopLoss ) / 100) / self.leverage))
                self.priceLSL = round(self.priceLSL, self.pricePrecision)

                # Set Stop-Loss
                self.orderLSL = \
                    stop_order_long_futures(self.client, amountInCurrency, self.symbol, 'Sell', self.priceLSL)[
                        'orderId']

                # Set Trailing Stop
                self.orderLTP = \
                    trailing_stop_long_futures(self.client, amountInCurrency, self.symbol, 'Sell', self.priceLTP,
                                                self.callBackRate)['orderId']

                self.orderStateLSL = 'Open'

            # IF Short Position is closed on Take Profit
            self.orderStateSTP = self.checkOrder(self.orderSTP, listOpenOrders)
            if self.orderStateSTP == 'Closed':
                cancel_futures_order(self.client, self.orderSSL, self.symbol)
                finalPnL, finalComission, quantityTrade = get_futures_trade_pnl_and_comission(self.client, self.symbol,
                                                                                              self.orderS,
                                                                                              self.orderSTP)
                finalProfit = finalPnL - finalComission

                # Get the current coin price and calculate half the profit
                price = get_futures_current_price(self.symbol, self.client)
                halfProfitInCurrency = ((finalProfit / 2) / price) * self.leverage
                amountInCurrency = round(halfProfitInCurrency + quantityTrade, self.quantityPrecision)

                # Create Short Market Order with Half Profit
                self.orderS = market_short_hedge_futures(self.client, amountInCurrency, self.symbol, 'Sell')

                # Create Long Market Order with Half Profit
                market_long_hedge_futures(self.client, amountInCurrency, self.symbol, 'Buy')

                # Define Trailing Stop
                self.priceSTP = price * (1 - (((self.takeProfit ) / 100) / self.leverage))
                self.priceSTP = round(self.priceSTP, self.pricePrecision)

                # Define Stop Loss
                self.priceSSL = price * (1 + (((self.stopLoss ) / 100) / self.leverage))
                self.priceSSL = round(self.priceSSL, self.pricePrecision)

                # Set Stop-Loss
                self.orderLSL = \
                    stop_order_short_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceSSL)[
                        'orderId']

                # Set Trailing Stop
                self.orderSTP = \
                    trailing_stop_short_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceSTP,
                                                self.callBackRate)['orderId']

                self.orderStateSTP = 'Open'

            # IF Long Position is closed on Take Profit
            self.orderStateLTP = self.checkOrder(self.orderLTP, listOpenOrders)
            if self.orderStateLTP == 'Closed':
                cancel_futures_order(self.client, self.orderLSL, self.symbol)
                finalPnL, finalComission, quantityTrade = get_futures_trade_pnl_and_comission(self.client, self.symbol,
                                                                                              self.orderL,
                                                                                              self.orderLTP)
                finalProfit = finalPnL - finalComission

                # Get the current coin price and calculate half the profit
                price = get_futures_current_price(self.symbol, self.client)
                halfProfitInCurrency = ((finalProfit / 2) / price) * self.leverage
                amountInCurrency = round(halfProfitInCurrency + quantityTrade, self.quantityPrecision)

                # Create Long Market Order with Half Profit
                self.orderL = market_long_hedge_futures(self.client, amountInCurrency, self.symbol, 'Buy')

                # Create Long Market Order with Half Profit
                market_short_hedge_futures(self.client, amountInCurrency, self.symbol, 'Sell')

                # Define Trailing Stop
                self.priceLTP = price * (1 + (((self.takeProfit ) / 100) / self.leverage))
                self.priceLTP = round(self.priceLTP, self.pricePrecision)

                # Define Stop Loss
                self.priceLSL = price * (1 - (((self.stopLoss ) / 100) / self.leverage))
                self.priceLSL = round(self.priceLSL, self.pricePrecision)

                # Set Stop-Loss
                self.orderLSL = \
                    stop_order_long_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceLSL)[
                        'orderId']

                # Set Trailing Stop
                self.orderLTP = \
                    trailing_stop_long_futures(self.client, amountInCurrency, self.symbol, 'Buy', self.priceLTP,
                                                self.callBackRate)['orderId']
                self.orderStateLTP = 'Open'

            print('STOP LOSS - '
                  f'Short: {self.colorOrder(self.orderStateSSL)} '
                  f'Long: {self.colorOrder(self.orderStateLSL)}  '
                  'TAKE PROFIT - '
                  f'Short: {self.colorOrder(self.orderStateSTP)} '
                  f'Long: {self.colorOrder(self.orderStateLTP)}')

            time.sleep(5)

    def checkOrder(self, orderId, listOpenOrders):
        if orderId in listOpenOrders:
            return 'Open'
        else:
            return 'Closed'

    def colorOrder(self, orderState):
        if orderState == 'Open':
            return Fore.GREEN + "Open" + Fore.RESET
        elif orderState == 'Closed':
            return Fore.RED + "Open" + Fore.RESET

    def closeRedistribute(self):

        # Print Welcome Text
        print(Fore.WHITE + Back.BLACK + Style.DIM + ' Welcome to Margin RSI Binance Bot ')


    # # TODO: Adapt to Hedge Mode (2 lines) maybe green and red
    # def loopSingleCoin(self, side, symbol):
    #
    #     tradeOn = False
    #
    #     futureInfo = self.client.futures_position_information()
    #
    #     # If Open Orders fill dataframe
    #     for info in futureInfo:
    #         if float(info["positionAmt"]) > 0:
    #
    #             # Get Info
    #             side = "Long"
    #             coin = info["symbol"]
    #             positionAmt = float(info["positionAmt"])
    #             entryPrice = float(info["entryPrice"])
    #             leverage = int(info["leverage"])
    #             liquidationPrice = float(info['liquidationPrice'])
    #
    #             tradeOn = True
    #
    #             # Get Price
    #             coinFuturePrice = get_futures_current_price(coin, self.client)
    #
    #             # Calculations
    #             tradeSize = round((positionAmt * entryPrice) / leverage, 2)
    #             realPercentage = (((coinFuturePrice / entryPrice) - 1) * 100)
    #             realPercentageLev = round(realPercentage * leverage - feePercentage * leverage, 2)
    #             profitLoss = round(tradeSize * (realPercentageLev / 100), 2)
    #
    #             if realPercentage < -minimumMarginDouble:
    #
    #                 side, activate = self.check_symbol(symbol)
    #
    #                 if activate == True:
    #
    #                     futureInfo = self.client.futures_position_information()
    #                     for info in futureInfo:
    #                         if info["symbol"] == symbol:
    #                             entryPrice = float(info["entryPrice"])
    #
    #                     amountInCurrency = format_lot_size(self.quantityFilter, positionAmt)
    #                     order = market_futures(self.client, positionAmt, symbol, 'Buy')
    #                     print(f'Bought another level of Trailing Stop (Percentage: {realPercentage} | amount: {positionAmt})')
    #
    #                     time.sleep(1)
    #
    #                     # Set Take_Profit
    #                     takeProfitPrice = entryPrice * (1 - (self.takeProfit / 100))
    #                     takeProfitPrice = format_price(self.priceFilter, takeProfitPrice)
    #
    #                     # Define Stop-Loss Price
    #                     stopLossPrice = entryPrice * (1 + (self.stopLoss / 100))
    #                     stopLossPrice = format_price(self.priceFilter, stopLossPrice)
    #
    #                     slOrder = stop_order_futures(self.client, amountInCurrency, symbol, 'Buy', stopLossPrice)
    #                     tpOrder = take_profit_futures(self.client, amountInCurrency, symbol, 'Buy', takeProfitPrice)
    #
    #
    #         elif float(info["positionAmt"]) < 0:
    #
    #             # Get Info
    #             side = "Short"
    #             coin = info["symbol"]
    #             print(coin)
    #             positionAmt = float(info["positionAmt"])
    #             entryPrice = float(info["entryPrice"])
    #             leverage = int(info["leverage"])
    #
    #             tradeOn = True
    #
    #             coinFuturePrice = get_futures_current_price(coin, self.client)
    #
    #             # Calculations
    #             tradeSize = round((positionAmt * -1 * entryPrice) / leverage, 2)
    #             realPercentage = (((coinFuturePrice / entryPrice) - 1) * -1 * 100)
    #             realPercentageLev = round((realPercentage * leverage) - feePercentage * leverage, 2)
    #             profitLoss = round(tradeSize * (realPercentageLev / 100), 2)
    #
    #             if realPercentage > minimumMarginDouble:
    #
    #                 side, activate = self.check_symbol(symbol)
    #
    #                 if activate == True:
    #                     amountInCurrency = format_lot_size(self.quantityFilter, positionAmt)
    #                     order = market_futures(self.client, positionAmt, symbol, 'Sell')
    #                     print(
    #                         f'Bought another level of Trailing Stop (Percentage: {realPercentage} | amount: {positionAmt})')
    #
    #                     time.sleep(1)
    #
    #                     futureInfo = self.client.futures_position_information()
    #                     for info in futureInfo:
    #                         if info["symbol"] == symbol:
    #                             entryPrice = float(info["entryPrice"])
    #
    #                     # Set Take_Profit
    #                     takeProfitPrice = entryPrice * (1 - (self.takeProfit / 100))
    #                     takeProfitPrice = format_price(self.priceFilter, takeProfitPrice)
    #
    #                     # Define Stop-Loss Price
    #                     stopLossPrice = entryPrice * (1 + (self.stopLoss / 100))
    #                     stopLossPrice = format_price(self.priceFilter, stopLossPrice)
    #
    #                     slOrder = stop_order_futures(self.client, amountInCurrency, symbol, 'Buy', stopLossPrice)
    #                     tpOrder = take_profit_futures(self.client, amountInCurrency, symbol, 'Buy', takeProfitPrice)
    #
    #     print(
    #         f'COIN {coin} | Perc: {realPercentageLev}% | PnL:{profitLoss}$ | Position Amount:{positionAmt} | Trade Size:{tradeSize}$ | Entry Price:{entryPrice} | Liquidation Price:{liquidationPrice}')
    #
    #     return tradeOn
    #
    # # TODO: Adapt speficic indicator & rules to activate single coin or not
    # def loopRSI(self):
    #
    #     # While waiting for trade
    #     while True:
    #         rsi = calculate_rsi(self.symbol)
    #         print(f'RSI is {round(rsi, 2)} (Looking to Buy)')
    #
    #         if rsi < self.lowerRSI:
    #             # Get BTCUSDT Information
    #             initialPrice = get_margin_current_price(self.symbol, self.client)
    #
    #             # Get the amount on BTC
    #             amountInBTC = float(self.amount) / initialPrice
    #             amountInBTC = format_lot_size(self.quantityFilter, amountInBTC)
    #
    #             # Execute buy order
    #             market_isolated_margin(self.client, amountInBTC, self.symbol, 'Buy', 'Loan')
    #
    #             break
    #
    #     # While trade is on
    #     while True:
    #         rsi = calculate_rsi(self.symbol)
    #         print(f'RSI is {round(rsi, 2)} (Looking to Sell)')
    #         if rsi > self.higherRSI:
    #             # Get BTCUSDT Information
    #             initialPrice = get_margin_current_price(self.symbol, self.client)
    #
    #             # Execute buy order
    #             market_isolated_margin(self.client, amountInBTC, self.symbol, 'Sell', 'Loan')
    #             break
    #
    # def long_market(self, side, amount):
    #
    #     # SetInitial Price
    #     initialPrice = get_futures_current_price(symbol, self.client)
    #
    #     # Define right amount
    #     amountInCurrency = float(amountOpen) / initialPrice
    #     amountInCurrency = round(amountInCurrency, self.quantityPrecision)
    #
    #     # Set Take_Profit
    #     takeProfitPrice = initialPrice * (1 + (takeProfit / 100))
    #     takeProfitPrice = format_price(self.pricePrecision, takeProfitPrice)
    #
    #     # Define Stop-Loss Price
    #     stopLossPrice = initialPrice * (1 - (stopLoss / 100))
    #     stopLossPrice = format_price(self.pricePrecision, stopLossPrice)
    #
    #     orderLong = market_long_hedge_futures(self.client, amountOpen, self.symbol, 'Buy')
    #     slLong = stop_order_long_futures(self.client, amountOpen, self.symbol, 'Buy')
    #     tpLong = take_profit_long_futures(self.client, amountOpen, self.symbol, 'Buy')
    #
    #     orderShort = market_short_hedge_futures(self.client, amountOpen, self.symbol, 'Buy')
    #     slShort = stop_order_short_futures(self.client, amountOpen, self.symbol, 'Buy')
    #     tpderShort = take_profit_short_futures(self.client, amountOpen, self.symbol, 'Buy')
    #
    #     # if any disapears:
    #     #     if sl
    #     #     if tp:
    #
    # def short_market(self, side, amount):
    #
    # def runLoopCoin(self):
    #
    # def runLoopCoins(self):
