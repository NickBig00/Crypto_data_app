import logging
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import ttk

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# Pfad zur ChromeDriver-Datei

# Logging-Konfiguration
logging.basicConfig(filename='crypto_data.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# API-Endpunkte und Symbol-Mappings
API_ENDPOINTS = {
    'Binance': "https://api.binance.us/api/v3/ticker/price?symbol={}",
    'Coinbase': "https://api.coinbase.com/v2/prices/{}/spot",
    'Crypto.com': "https://api.crypto.com/v2/public/get-ticker?instrument_name={}",
    'Kraken': "https://api.kraken.com/0/public/Ticker?pair={}",
    'uzx.kr': "",
}

API_SYMBOL_MAPPINGS = {
    'BTCUSDT': {'Bybit': 'BTCUSDT', 'Binance': 'BTCUSDT', 'Coinbase': 'BTC-USD', 'Crypto.com': 'BTC_USDT',
                'Kraken': 'XXBTZUSD', 'uzx.kr': 'btc_usdt'},
    'ETHUSDT': {'Bybit': 'ETHUSDT', 'Binance': 'ETHUSDT', 'Coinbase': 'ETH-USD', 'Crypto.com': 'ETH_USDT',
                'Kraken': 'XETHZUSD', 'uzx.kr': 'eth_usdt'},
    'LINKUSDT': {'Bybit': 'LINKUSDT', 'Binance': 'LINKUSDT', 'Coinbase': 'LINK-USD', 'Crypto.com': 'LINK_USDT',
                 'Kraken': 'LINKUSD', 'uzx.kr': 'link_usdt'},
    'LTCUSDT': {'Bybit': 'LTCUSDT', 'Binance': 'LTCUSDT', 'Coinbase': 'LTC-USD', 'Crypto.com': 'LTC_USDT',
                'Kraken': 'XLTCZUSD', 'uzx.kr': 'ltc_usdt'},
    'ETCUSDT': {'Bybit': 'ETCUSDT', 'Binance': 'ETCUSDT', 'Coinbase': 'ETC-USD', 'Crypto.com': 'ETC_USDT',
                'Kraken': 'XETCZUSD', 'uzx.kr': 'etc_usdt'},
    'FILUSDT': {'Bybit': 'FILUSDT', 'Binance': 'FILUSDT', 'Coinbase': 'FIL-USD', 'Crypto.com': 'FIL_USDT',
                'Kraken': 'FILUSD', 'uzx.kr': 'fil_usdt'},
    'AAVEUSDT': {'Bybit': 'AAVEUSDT', 'Binance': 'AAVEUSDT', 'Coinbase': 'AAVE-USD', 'Crypto.com': 'AAVE_USDT',
                 'Kraken': 'AAVEUSD', 'uzx.kr': 'aave_usdt'},
    'UNIUSDT': {'Bybit': 'UNIUSDT', 'Binance': 'UNIUSDT', 'Coinbase': 'UNI-USD', 'Crypto.com': 'UNI_USDT',
                'Kraken': 'UNIUSD', 'uzx.kr': 'uni_usdt'},
    'DOGEUSDT': {'Bybit': 'DOGEUSDT', 'Binance': 'DOGEUSDT', 'Coinbase': 'DOGE-USD', 'Crypto.com': 'DOGE_USDT',
                 'Kraken': 'XDGUSD', 'uzx.kr': 'doge_usdt'},
    '1INCHUSDT': {'Bybit': '1INCHUSDT', 'Binance': '1INCHUSDT', 'Coinbase': '1INCH-USD', 'Crypto.com': '1INCH_USDT',
                  'Kraken': '1INCHUSD', 'uzx.kr': '1inch_usdt'},
    'ADAUSDT': {'Bybit': 'ADAUSDT', 'Binance': 'ADAUSDT', 'Coinbase': 'ADA-USD', 'Crypto.com': 'ADA_USDT',
                'Kraken': 'ADAUSD', 'uzx.kr': 'ada_usdt'},
    'DOTUSDT': {'Bybit': 'DOTUSDT', 'Binance': 'DOTUSDT', 'Coinbase': 'DOT-USD', 'Crypto.com': 'DOT_USDT',
                'Kraken': 'DOTUSD', 'uzx.kr': 'dot_usdt'},
    'SOLUSDT': {'Bybit': 'SOLUSDT', 'Binance': 'SOLUSDT', 'Coinbase': 'SOL-USD', 'Crypto.com': 'SOL_USDT',
                'Kraken': 'SOLUSD', 'uzx.kr': 'sol_usdt'},
    'MATICUSDT': {'Bybit': 'MATICUSDT', 'Binance': 'MATICUSDT', 'Coinbase': 'MATIC-USD', 'Crypto.com': 'MATIC_USDT',
                  'Kraken': 'MATICUSD', 'uzx.kr': 'matic_usdt'},
    'AVAXUSDT': {'Bybit': 'AVAXUSDT', 'Binance': 'AVAXUSDT', 'Coinbase': 'AVAX-USD', 'Crypto.com': 'AVAX_USDT',
                 'Kraken': 'AVAXUSD', 'uzx.kr': 'avax_usdt'},
    'XLMUSDT': {'Bybit': 'XLMUSDT', 'Binance': 'XLMUSDT', 'Coinbase': 'XLM-USD', 'Crypto.com': 'XLM_USDT',
                'Kraken': 'XXLMZUSD', 'uzx.kr': 'xlm_usdt'},
    'ATOMUSDT': {'Bybit': 'ATOMUSDT', 'Binance': 'ATOMUSDT', 'Coinbase': 'ATOM-USD', 'Crypto.com': 'ATOM_USDT',
                 'Kraken': 'ATOMUSD', 'uzx.kr': 'atom_usdt'},
    'VETUSDT': {'Bybit': 'VETUSDT', 'Binance': 'VETUSDT', 'Coinbase': 'VET-USD', 'Crypto.com': 'VET_USDT',
                'Kraken': 'VETUSD', 'uzx.kr': 'vet_usdt'},
    'TRXUSDT': {'Bybit': 'TRXUSDT', 'Binance': 'TRXUSDT', 'Coinbase': 'TRX-USD', 'Crypto.com': 'TRX_USDT',
                'Kraken': 'TRXUSD', 'uzx.kr': 'trx_usdt'},
    'FTTUSDT': {'Bybit': 'FTTUSDT', 'Binance': 'FTTUSDT', 'Coinbase': 'FTT-USD', 'Crypto.com': 'FTT_USDT',
                'Kraken': 'FTTUSD', 'uzx.kr': 'ftt_usdt'},
    'BCHUSDT': {'Bybit': 'BCHUSDT', 'Binance': 'BCHUSDT', 'Coinbase': 'BCH-USD', 'Crypto.com': 'BCH_USDT',
                'Kraken': 'BCHUSD', 'uzx.kr': 'bch_usdt'},
    'SUSHIUSDT': {'Bybit': 'SUSHIUSDT', 'Binance': 'SUSHIUSDT', 'Coinbase': 'SUSHI-USD', 'Crypto.com': 'SUSHI_USDT',
                  'Kraken': 'SUSHIUSD', 'uzx.kr': 'sushi_usdt'},
    'CRVUSDT': {'Bybit': 'CRVUSDT', 'Binance': 'CRVUSDT', 'Coinbase': 'CRV-USD', 'Crypto.com': 'CRV_USDT',
                'Kraken': 'CRVUSD', 'uzx.kr': 'crv_usdt'},
    'YFIUSDT': {'Bybit': 'YFIUSDT', 'Binance': 'YFIUSDT', 'Coinbase': 'YFI-USD', 'Crypto.com': 'YFI_USDT',
                'Kraken': 'YFIUSD', 'uzx.kr': 'yfi_usdt'},
    'RENUSDT': {'Bybit': 'RENUSDT', 'Binance': 'RENUSDT', 'Coinbase': 'REN-USD', 'Crypto.com': 'REN_USDT',
                'Kraken': 'RENUSD', 'uzx.kr': 'ren_usdt'},
    'COMPUSDT': {'Bybit': 'COMPUSDT', 'Binance': 'COMPUSDT', 'Coinbase': 'COMP-USD', 'Crypto.com': 'COMP_USDT',
                 'Kraken': 'COMPUSD', 'uzx.kr': 'comp_usdt'},
    'SNXUSDT': {'Bybit': 'SNXUSDT', 'Binance': 'SNXUSDT', 'Coinbase': 'SNX-USD', 'Crypto.com': 'SNX_USDT',
                'Kraken': 'SNXUSD', 'uzx.kr': 'snx_usdt'},
    'ZRXUSDT': {'Bybit': 'ZRXUSDT', 'Binance': 'ZRXUSDT', 'Coinbase': 'ZRX-USD', 'Crypto.com': 'ZRX_USDT',
                'Kraken': 'ZRXUSD', 'uzx.kr': 'zrx_usdt'},
    'ALGOUSDT': {'Bybit': 'ALGOUSDT', 'Binance': 'ALGOUSDT', 'Coinbase': 'ALGO-USD', 'Crypto.com': 'ALGO_USDT',
                 'Kraken': 'ALGOUSD', 'uzx.kr': 'algo_usdt'},
    'CHZUSDT': {'Bybit': 'CHZUSDT', 'Binance': 'CHZUSDT', 'Coinbase': 'CHZ-USD', 'Crypto.com': 'CHZ_USDT',
                'Kraken': 'CHZUSD', 'uzx.kr': 'chz_usdt'},
    'GRTUSDT': {'Bybit': 'GRTUSDT', 'Binance': 'GRTUSDT', 'Coinbase': 'GRT-USD', 'Crypto.com': 'GRT_USDT',
                'Kraken': 'GRTUSD', 'uzx.kr': 'grt_usdt'},
    'MANAUSDT': {'Bybit': 'MANAUSDT', 'Binance': 'MANAUSDT', 'Coinbase': 'MANA-USD', 'Crypto.com': 'MANA_USDT',
                 'Kraken': 'MANAUSD', 'uzx.kr': 'mana_usdt'},
    'BATUSDT': {'Bybit': 'BATUSDT', 'Binance': 'BATUSDT', 'Coinbase': 'BAT-USD', 'Crypto.com': 'BAT_USDT',
                'Kraken': 'BATUSD', 'uzx.kr': 'bat_usdt'},
    'ZILUSDT': {'Bybit': 'ZILUSDT', 'Binance': 'ZILUSDT', 'Coinbase': 'ZIL-USD', 'Crypto.com': 'ZIL_USDT',
                'Kraken': 'ZILUSD', 'uzx.kr': 'zil_usdt'},
    'ENJUSDT': {'Bybit': 'ENJUSDT', 'Binance': 'ENJUSDT', 'Coinbase': 'ENJ-USD', 'Crypto.com': 'ENJ_USDT',
                'Kraken': 'ENJUSD', 'uzx.kr': 'enj_usdt'},
    'KSMUSDT': {'Bybit': 'KSMUSDT', 'Binance': 'KSMUSDT', 'Coinbase': 'KSM-USD', 'Crypto.com': 'KSM_USDT',
                'Kraken': 'KSMUSD', 'uzx.kr': 'ksm_usdt'},
    'NEARUSDT': {'Bybit': 'NEARUSDT', 'Binance': 'NEARUSDT', 'Coinbase': 'NEAR-USD', 'Crypto.com': 'NEAR_USDT',
                 'Kraken': '', 'uzx.kr': 'near_usdt'}}


def main():
    root = tk.Tk()
    root.title("Crypto Prices")

    # Scrollbar hinzufügen
    canvas = tk.Canvas(root)
    scrollbar = tk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(xscrollcommand=scrollbar.set)

    canvas.pack(side="top", fill="both", expand=True)
    scrollbar.pack(side="bottom", fill="x")

    # Tabelle erstellen
    table_frame = scrollable_frame

    labels = ["Coin", "Binance", "Crypto.com", "Kraken", "Coinbase", "uzx.kr"]
    for i, label in enumerate(labels):
        tk.Label(table_frame, text=label).grid(row=0, column=i, padx=10)

    coin_comboboxes = []
    for i in range(10):
        combo = ttk.Combobox(table_frame, values=sorted(list(API_SYMBOL_MAPPINGS.keys())), state="readonly")
        combo.grid(row=i + 1, column=0, padx=5, pady=5)
        coin_comboboxes.append(combo)
        for j in range(1, len(labels)):
            entry = tk.Entry(table_frame)
            entry.grid(row=i + 1, column=j, padx=10)
            entry.config(state='readonly')

    # Button erstellen
    button = tk.Button(root, text="Update prices", command=lambda: update_selected_prices(table_frame, coin_comboboxes))
    button.pack()

    # Fenstergröße manuell anpassen
    root.update_idletasks()

    # Breite und Höhe festlegen
    width = sum(label.winfo_reqwidth() for label in table_frame.winfo_children()[:len(labels)]) + 700
    height = root.winfo_reqheight() + 60
    root.geometry(f"{width}x{height}")

    # Fenstergröße begrenzen
    root.minsize(width, height)
    root.maxsize(width, height)

    root.mainloop()


def update_selected_prices(table_frame, coin_comboboxes):
    def update_gui_with_prices(i, prices):
        for j, price in enumerate(prices):
            entry = table_frame.grid_slaves(row=i + 1, column=j + 1)[0]
            entry.config(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, price)
            entry.config(state='readonly')

    with ThreadPoolExecutor(max_workers=len(coin_comboboxes) * len(API_ENDPOINTS)) as executor:
        future_to_coin = {
            executor.submit(fetch_prices_for_coin, combo.get()): i
            for i, combo in enumerate(coin_comboboxes) if combo.get()
        }

        for future in as_completed(future_to_coin):
            i = future_to_coin[future]
            try:
                prices = future.result()
                table_frame.after(0, lambda i=i, prices=prices: update_gui_with_prices(i, prices))
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung von {i}: {e}")


def fetch_prices_for_coin(coin):
    prices = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for exchange in API_ENDPOINTS.keys():
            mapped_symbol = get_mapped_symbol(exchange, coin)
            if mapped_symbol:
                if exchange == "uzx.kr":
                    futures.append(executor.submit(get_uzx_price, mapped_symbol))
                else:
                    futures.append(executor.submit(get_last_price, exchange, mapped_symbol))
        for future in as_completed(futures):
            price = future.result()
            prices.append(price if price else "N/A")
    return prices


def get_last_price(exchange, symbol):
    url = API_ENDPOINTS[exchange].format(symbol)
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return parse_price_data(exchange, data, symbol)
    except requests.RequestException as e:
        logging.error(f"Fehler beim Abrufen des Preises von {exchange} für {symbol}: {e}")
        return None


def parse_price_data(exchange, data, symbol):
    if exchange == 'Bybit':
        return data["result"]["price"]
    elif exchange == 'Binance':
        return data['price']
    elif exchange == 'Coinbase':
        return data['data']['amount']
    elif exchange == 'Crypto.com':
        return data['result']['data'][0]['a']
    elif exchange == 'Kraken':
        return data['result'][symbol]['c'][0]
    return None


def get_uzx_price(coin):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Aktiviert den Headless-Modus
    chrome_options.add_argument('--disable-gpu')  # Vermeidet unnötige GPU-Nutzung

    driver_path = ChromeDriverManager().install()
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    url = f'https://uzx.kr/#/exchange/{coin}'
    driver.get(url)

    try:
        wait = WebDriverWait(driver, 10)
        # Versuche zuerst das "buy"-Element zu finden
        price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.orderForm_price.buy")))
        price = price_element.text
    except:
        try:
            # Wenn "buy" nicht gefunden wird, versuche das "sell"-Element zu finden
            price_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.orderForm_price.sell")))
            price = price_element.text
        except Exception as e:
            logging.error(f"Fehler beim Abrufen des Preises für {coin}: {e}")
            price = None
    finally:
        driver.quit()

    logging.info(f"Found price {price} for {coin} from uzx.kr")
    return price


def get_mapped_symbol(exchange, coin):
    return API_SYMBOL_MAPPINGS[coin].get(exchange)


if __name__ == "__main__":
    main()
