import logging

import pandas as pd
import requests

# Logging-Konfiguration
logging.basicConfig(filename='crypto_data.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

logging.info("Programm gestartet")

# Beispielhafte API-Endpunkte (du musst diese entsprechend anpassen)
api_endpoints = {
    'Bybit': "https://api.bybit.com//spot/v3/public/quote/ticker/price?symbol={}",
    'Binance': "https://api.binance.com/api/v3/ticker/price?symbol={}",
    'Coinbase': "https://api.coinbase.com/v2/prices/{}/spot",
    'Crypto.com': "https://api.crypto.com/v2/public/get-ticker?instrument_name={}",
    'Kraken': "https://api.kraken.com/0/public/Ticker?pair={}",
}

# Mapping von Symbolen für Kraken und Coinbase
kraken_pairs = {
    'BTCUSDT': 'XXBTZUSD',
    'ETHUSDT': 'XETHZUSD',
    'LINKUSDT': 'LINKUSD',
    'ETCUSDT': 'XETCZUSD',
    'FILUSDT': 'FILUSD',
    'LTCUSDT': 'XLTCZUSD',
    'AAVEUSDT': 'AAVEUSD',
    'UNIUSDT': 'UNIUSD',
    'DOGEUSDT': 'XDGUSD',
    '1INCHUSDT': '1INCHUSD'
}

coinbase_pairs = {
    'BTCUSDT': 'BTC-USD',
    'ETHUSDT': 'ETH-USD',
    'LINKUSDT': 'LINK-USD',
    'ETCUSDT': 'ETC-USD',
    'FILUSDT': 'FIL-USD',
    'LTCUSDT': 'LTC-USD',
    'AAVEUSDT': 'AAVE-USD',
    'UNIUSDT': 'UNI-USD',
    'DOGEUSDT': 'DOGE-USD',
    '1INCHUSDT': '1INCH-USD'
}

crypto_com_pairs = {
    'BTCUSDT': 'BTC_USDT',
    'ETHUSDT': 'ETH_USDT',
    'LINKUSDT': 'LINK_USDT',
    'ETCUSDT': 'ETC_USDT',
    'FILUSDT': 'FIL_USDT',
    'LTCUSDT': 'LTC_USDT',
    'AAVEUSDT': 'AAVE_USDT',
    'UNIUSDT': 'UNI_USDT',
    'DOGEUSDT': 'DOGE_USDT',
    '1INCHUSDT': '1INCH_USDT'
}


def get_last_price(exchange, symbol):
    try:
        url = api_endpoints[exchange].format(symbol)
        response = requests.get(url)
        data = response.json()

        if exchange == 'Bybit':
            return data["result"]["price"]
        elif exchange == 'Binance':
            return data['price']
        elif exchange == 'Coinbase':
            return data['data']['amount']
        elif exchange == 'Crypto.com':
            return data['result']['data'][0]['a']  # Letzter Preis
        elif exchange == 'Kraken':
            return data['result'][symbol]['c'][0]  # Closing price
        else:
            return None
    except Exception as e:
        logging.error(f"Fehler beim Abrufen des Preises von {exchange}: {e}")
        return None


# Symbole der Coins, die du abfragen möchtest
coins = ["BTCUSDT", "ETHUSDT", "LINKUSDT", "ETCUSDT", "FILUSDT",
         "LTCUSDT", "AAVEUSDT", "UNIUSDT", "DOGEUSDT", "1INCHUSDT"]

# Erstelle ein leeres DataFrame mit Coins als Zeilen und Exchanges als Spalten
df = pd.DataFrame(index=coins, columns=api_endpoints.keys())

# Daten für jeden Coin auf jeder Börse sammeln
for coin in coins:
    for exchange in api_endpoints.keys():
        if exchange == 'Kraken' and coin not in kraken_pairs:
            continue  # Überspringe, wenn es kein Mapping gibt
        if exchange == 'Coinbase' and coin not in coinbase_pairs:
            continue  # Überspringe, wenn es kein Mapping gibt
        if exchange == 'Crypto.com' and coin not in crypto_com_pairs:
            continue  # Überspringe, wenn es kein Mapping gibt
        if exchange == 'Kraken':
            price = float(get_last_price(exchange, kraken_pairs.get(coin, coin)))
        elif exchange == 'Crypto.com':
            price = float(get_last_price(exchange, crypto_com_pairs.get(coin, coin)))
        elif exchange == 'Coinbase':
            price = float(get_last_price(exchange, coinbase_pairs.get(coin, coin)))
        else:
            price = float(get_last_price(exchange, coin))

        if price:
            df.at[coin, exchange] = price
            logging.info(f"Preis für {coin} auf {exchange}: {price}")
        else:
            logging.warning(f"Kein Preis für {coin} auf {exchange} gefunden.")
            print(f"Kein Preis für {coin} auf {exchange} gefunden.")

# Speichere das DataFrame in einer Excel-Datei (erstelle die Datei neu)+
try:
    output_file = "crypto_prices_sheet.xlsm"
    print(df)
    df.to_excel("crypto_prices_sheet.xlsm")

    print("Preise wurden in crypto_prices.xlsm gespeichert.")
except Exception as e:
    print(e)
