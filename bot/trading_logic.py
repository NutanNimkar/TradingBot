import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import numpy as np
from pandas.tseries.offsets import DateOffset
from alpha_vantage.timeseries import TimeSeries
class AlphaVantageTradingLogic:
    def __init__(self, api_key, polygon_api_key):
        self.api_key = api_key
        self.polygon_api_key = polygon_api_key
        self.base_url_alpha = "https://www.alphavantage.co/query"
        self.base_url_polygon = "https://api.polygon.io/v2/aggs"
        self.model=None

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
    def get_historical_polygon(self, symbol):
        params = {
            'ticker': {symbol},
            'multiplier': 1,
            'timespan': 'day',
            'apiKey': self.polygon_api_key,
        }
        response = requests.get(f"{self.base_url_polygon}/ticker/{symbol}/range/1/day/2022-01-01/2024-01-01", params=params)
        data = response.json()
        if 'results' in data:
            historical_prices = [(entry['t'], entry['c']) for entry in data['results']]

            df = pd.DataFrame(historical_prices, columns=['timestamp', 'closing_price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            print('Successfully retrieved historical data for', symbol)
            return df
        else:
            print(f"Failed to get historical data for {symbol}. Check the symbol and try again.")
            return None
        
    def train_price_prediction_model(self, symbol):
        
        df = self.get_historical_polygon(symbol)
        
        if df is None or len(df) == 0:
            print(f'Insufficient data for training {symbol}')
            return
        
        X = df.index.values.astype(int).reshape(-1, 1)
        y = df['closing_price']
        
        #split the stat into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42, shuffle=True)
        
        #train a linear regression model
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        #evaluate the model
        y_pred = self.model.predict(X_test)
        mean_square_error = mean_squared_error(y_test, y_pred)
        print(f'Mean squared Error {mean_square_error}')
        
    def predict_price(self, symbol, date):
        if self.model is None:
            print('Model not trained. Train the model')
            return None
        date_numeric = np.array([[date.timestamp() * 1e9]])
        
        #predict the stock price 
        predicted_price = self.model.predict(date_numeric)[0]
        print(predicted_price)
        return predicted_price
    
    def decision_for_stock(self, symbol):
        df = self.get_historical_polygon(symbol)
        
        if df is None or len(df) == 0:
            print(f"Insufficient historical data for making predications")
            return None
        
        #get last date in the dataset
        last_date = df.index[-1]
        next_date = last_date + DateOffset(days=1)
        
        
        #predict the price for the next day
        predicted_price = self.predict_price(symbol, next_date)
        current_price = self.get_stock_price(symbol)
        print(f'current price', current_price)
        
        
        if predicted_price is not None:
            if predicted_price > current_price:
                return "Buy"
            elif predicted_price < current_price:
                return "Sell"
            else:
                return "Hold"
        else:
            return None