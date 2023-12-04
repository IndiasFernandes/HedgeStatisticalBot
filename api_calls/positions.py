from binance.exceptions import BinanceAPIException
import pandas as pd

def change_futures_position_mode(client, mode):
    try:
        if mode == 'Hedge':
            client.futures_coin_change_position_mode(dualSidePosition=True)
        elif mode == 'Normal':
            client.futures_coin_change_position_mode(dualSidePosition=False)
        print(f'Position Mode changed to {mode}')
        return mode
    except BinanceAPIException:
        print(f"Position Mode already set to '{mode}'")


def get_futures_all_positions(client):
    # Search for Open Orders
    orders = client.futures_position_information()
    df = pd.DataFrame.from_dict(orders)

    if not df.empty:
        df = df.drop(
            ['maxNotionalValue', 'isAutoAddMargin', 'notional', 'isolatedWallet', 'updateTime'],
            axis=1)

    return df
