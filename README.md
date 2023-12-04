# Futures Hedge Trading Bot for Binance

This repository contains a Python-based trading bot designed for hedging strategies on the Binance Futures market. The bot executes both long and short futures orders, managing positions with features like trailing stops, take profits, and stop losses.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Disclaimer](#disclaimer)
- [Contributing](#contributing)

### Features

- **Market Long and Short Orders**: Executes market long and short orders to establish hedge positions.
- **Dynamic Trailing Stops**: Configurable trailing stops for managing risk and locking in profits.
- **Take Profit and Stop Loss**: Sets take profit and stop loss levels to secure profits and limit losses.
- **Order Management**: Cancels and modifies orders based on market conditions.
- **Real-Time Price Fetching**: Retrieves current futures prices for accurate decision-making.
- **Precision Handling**: Manages quantity and price precision for different trading pairs.

### Installation

1. Clone the repository: 
git clone https://github.com/your-username/futures-hedge-trading-bot.git

css
Copy code
2. Navigate to the cloned directory:
cd futures-hedge-trading-bot

markdown
Copy code
3. Install required packages:
pip install -r requirements.txt

markdown
Copy code

### Configuration

- Set your Binance API keys in `config.py`.
- Configure trading parameters like `symbol`, `leverage`, `initialAmount`, `trailStopProfit`, `stopLoss`, and `callBack`.

### Usage

1. Run `run.py` to start the trading bot.
