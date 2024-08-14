import logging
import time
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

# Pfad zur ChromeDriver-Datei

# Logging-Konfiguration
logging.basicConfig(filename='crypto_data.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# API-Endpunkte und Symbol-Mappings
API_ENDPOINTS = {
    'Bybit': "https://api.bybit.com//spot/v3/public/quote/ticker/price?symbol={}",
    'Binance': "https://api.binance.com/api/v3/ticker/price?symbol={}",
    'Coinbase': "https://api.coinbase.com/v2/prices/{}/spot",
    'Crypto.com': "https://api.crypto.com/v2/public/get-ticker?instrument_name={}",
    'Kraken': "https://api.kraken.com/0/public/Ticker?pair={}",
    'uzx.kr': "",
}

KRAKEN_PAIRS = {
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

COINBASE_PAIRS = {
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

CRYPTO_COM_PAIRS = {
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

COINS = ["BTCUSDT", "ETHUSDT", "LINKUSDT", "ETCUSDT", "FILUSDT",
         "LTCUSDT", "AAVEUSDT", "UNIUSDT", "DOGEUSDT", "1INCHUSDT"]


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

    labels = ["Coin", "Bybit", "Binance", "Crypto.com", "Kraken", "Coinbase", "uzx.kr"]
    for i, label in enumerate(labels):
        tk.Label(table_frame, text=label).grid(row=0, column=i, padx=10)

    coin_comboboxes = []
    for i in range(10):
        combo = ttk.Combobox(table_frame, values=COINS)
        combo.grid(row=i + 1, column=0, padx=5, pady=5)
        coin_comboboxes.append(combo)
        for j in range(1, len(labels)):
            tk.Label(table_frame, text="").grid(row=i + 1, column=j, padx=10)

    # Button erstellen
    button = tk.Button(root, text="Update prices", command=lambda: update_selected_prices(table_frame, coin_comboboxes))
    button.pack()

    # Fenstergröße manuell anpassen
    root.update_idletasks()

    # Breite und Höhe festlegen
    width = sum(label.winfo_reqwidth() for label in table_frame.winfo_children()[:len(labels)]) + 400
    height = root.winfo_reqheight() + 60
    root.geometry(f"{width}x{height}")

    # Fenstergröße begrenzen
    root.minsize(width, height)
    root.maxsize(width, height)

    root.mainloop()


def update_selected_prices(table_frame, coin_comboboxes):
    def update_gui_with_prices(i, prices):
        for j, price in enumerate(prices):
            label = tk.Label(table_frame, text=price)
            label.grid(row=i + 1, column=j + 1, padx=10)

    with ThreadPoolExecutor(max_workers=len(coin_comboboxes) * len(API_ENDPOINTS)) as executor:
        future_to_coin = {
            executor.submit(fetch_prices_for_coin, combo.get()): i
            for i, combo in enumerate(coin_comboboxes) if combo.get()
        }

        for future in as_completed(future_to_coin):
            i = future_to_coin[future]
            try:
                prices = future.result()
                # GUI-Update im Hauptthread
                table_frame.after(0, lambda i=i, prices=prices: update_gui_with_prices(i, prices))
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung von {i}: {e}")

def create_table(root, coins, exchanges):
    columns = ["Coin"] + list(exchanges)
    table = ttk.Treeview(root, columns=columns, show="headings")
    table.pack(expand=True, fill="both")

    # Spaltenüberschriften setzen
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=100, anchor="center")

    # Daten in die Tabelle einfügen und Comboboxen für die Coin-Spalte hinzufügen
    coin_comboboxes = []
    for i in range(10):  # 10 Zeilen
        combo = ttk.Combobox(table, values=COINS)
        combo.pack(padx=5, pady=5)
        table.insert("", "end", iid=f"row{i + 1}", values=[""] + [""] * len(exchanges))
        table.set(f"row{i + 1}", "Coin", combo)
        coin_comboboxes.append(combo)
        table.update_idletasks()

    return table


def create_update_button(root, table):
    button = tk.Button(root, text="Update prices", command=lambda: update_selected_prices(table))
    button.pack()


def fetch_prices_for_coin(coin):
    prices = []
    with ThreadPoolExecutor(max_workers=5) as executor:  # Erhöhung der max_workers
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
    chrome_driver_path = 'C:/Users/gross/chromedriver-win64/chromedriver.exe'

    # Chrome-Optionen (optional, falls du das Browser-Fenster nicht sehen möchtest)
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Kommentar entfernen, wenn du den Browser sehen möchtest

    # WebDriver initialisieren
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URL der Webseite
    url = f'https://uzx.com/#/exchange/{coin}'
    driver.get(url)

    # Warten, bis das Preis-Element sichtbar ist
    try:
        wait = WebDriverWait(driver, 30)

        # Initialer Preis, um die erste Erfassung zu starten
        last_price = None
        current_price = None

        # Warten, bis der Preis sich stabilisiert hat
        for _ in range(10):  # Versuche 10 mal
            price_element = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.singlePrice_price_val.sell'))
            )
            current_price = price_element.text.strip()

            if current_price != last_price:
                last_price = current_price
                time.sleep(2)  # Kurze Pause, um den Preis erneut zu überprüfen
            else:
                break

        print(f"Finaler {coin} Preis: {current_price}")
        return current_price

    except Exception as e:
        logging.warning(e)
        return None

    finally:
        driver.quit()


def update_prices(table):
    with ThreadPoolExecutor(max_workers=len(COINS) * len(API_ENDPOINTS)) as executor:
        future_to_coin = {
            executor.submit(fetch_prices_for_coin, coin): coin for coin in COINS
        }
        for future in as_completed(future_to_coin):
            coin = future_to_coin[future]
            try:
                prices = future.result()
                table.item(coin, values=[coin] + prices)
            except Exception as e:
                logging.error(f"Fehler bei der Verarbeitung von {coin}: {e}")


def get_mapped_symbol(exchange, coin):
    if exchange == 'Kraken':
        return KRAKEN_PAIRS.get(coin)
    elif exchange == 'Coinbase':
        return COINBASE_PAIRS.get(coin)
    elif exchange == 'Crypto.com':
        return CRYPTO_COM_PAIRS.get(coin)
    elif exchange == 'uzx.kr':
        return CRYPTO_COM_PAIRS.get(coin).lower()
    else:
        return coin


if __name__ == "__main__":
    main()
