import requests
class AlphaVantageTradingLogic:
    def __init__(self, api_key):
        self.api_key = api_key
        self.portfolio = {}

    def get_stock_price(self, symbol):
        url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.api_key}'

        try:
            response = requests.get(url)
            data = response.json()

            if 'Global Quote' in data:
                price = float(data['Global Quote']['05. price'])
                return price
            else:
                return None
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None
