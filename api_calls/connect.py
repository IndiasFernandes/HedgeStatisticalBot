from binance import Client
from colorama import Fore, Style
from config import *

def connect_binance():
    print(Fore.BLACK + '    - Connecting to Binance ', end='')
    client = Client(binance_key, binance_secret)
    print(Fore.GREEN + Style.BRIGHT + u'\u2713', end='\n')
    return client