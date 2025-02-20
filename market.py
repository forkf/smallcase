from bs4 import BeautifulSoup
import requests
from constants import LOGGER

# from nselib import capital_market
#
#
# def get_stock_price(symbol: str) -> dict:
#     price = 0
#     try:
#         market = capital_market.price_volume_and_deliverable_position_data(symbol=symbol, period="1D")
#         last_price = market['LastPrice']
#         price = float(last_price.values[0].replace(",", ""))
#     except Exception as e:
#         print(e)
#     finally:
#         return {symbol: price}

def screen_symbol(symbol):
    try:
        url = requests.get(f"https://www.screener.in/company/{symbol}/")
        soup = BeautifulSoup(url.content, 'lxml')

        table = soup.find('div', attrs={'id': 'top'})
        price = table.find("span").text
        price = price.split(" ")[-1]
        price = price.replace(",", "")
        return int(price)
    except Exception as error:
        LOGGER.error(error)
        return 0
