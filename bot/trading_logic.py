import requests
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error,  r2_score, mean_absolute_error
import numpy as np
from pandas.tseries.offsets import DateOffset
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
class AlphaVantageTradingLogic:
    def __init__(self, api_key, polygon_api_key):
        self.api_key = api_key
        self.polygon_api_key = polygon_api_key
        self.base_url_alpha = "https://www.alphavantage.co/query"
        self.base_url_polygon = "https://api.polygon.io/v2/aggs"
        self.model=None
        self.today_date = datetime.now().strftime("%Y-%m-%d")
        self.allowed_date = (datetime.now() - timedelta(days=365 * 2)).strftime("%Y-%m-%d")

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
        response = requests.get(f"{self.base_url_polygon}/ticker/{symbol}/range/1/day/{self.allowed_date}/{self.today_date}", params=params)
        data = response.json()
        if 'results' in data:
            historical_prices = [(entry['t'], entry['c']) for entry in data['results']]

            df = pd.DataFrame(historical_prices, columns=['timestamp', 'closing_price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            print('Successfully retrieved historical data for', symbol)
            return df
        else:
            print(f"Failed to get historical data")
            return None
        
    def train_price_prediction_model(self, symbol):
        
        df = self.get_historical_polygon(symbol)
        
        if df is None or len(df) == 0:
            print(f'Not Enough data')
            return
        
        X = df.index.values.astype(int).reshape(-1, 1)
        y = df['closing_price']
        
       
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42, shuffle=True)
        

        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
       #to check model
        # y_pred = self.model.predict(X_test)
        # mean_absolute_val = mean_absolute_error(y_test, y_pred)
        # print(f'Mean Absolute Error {mean_absolute_val}')
        # mean_squared_val = mean_squared_error(y_test, y_pred)
        # print(f'Mean Square Error {mean_squared_val}')
        # root_mean_squared_error = np.sqrt(mean_squared_val)
        # print(f'Root {root_mean_squared_error}')
        # r_squared = r2_score(y_test, y_pred)
        # print(f'R sqaured value {r_squared}')

        
    def predict_price(self, symbol, date):
        if self.model is None:
            print('Model not trained')
            return None
        date_numeric = np.array([[date.timestamp() * 1e9]])
        
        #predict the stock price 
        predicted_price = self.model.predict(date_numeric)[0]
        print(predicted_price)
        return predicted_price
    
    def plot_for_stock(self, symbol):
        df = self.get_historical_polygon(symbol)
        
        if df is None or len(df) == 0:
            print(f"Not enough data")
            return
        X_all = df.index.values.astype(int).reshape(-1, 1)
        y_pred_all = self.model.predict(X_all)
        
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['closing_price'], label='Actual Closing Price', color='black')
        plt.plot(df.index, y_pred_all, label='Predicted Closing Price', linestyle='--', color='red')
        plt.title(f'Actual vs. Predicted Stock Prices for {symbol}')
        plt.xlabel('Date')
        plt.ylabel('Closing Price')
        plt.legend()
        # plt.show()
        
        plt.savefig(f"{symbol}_plot.png")
        plt.close()
        
    def decision_for_stock(self, symbol):
        df = self.get_historical_polygon(symbol)
        
        if df is None or len(df) == 0:
            print(f"Not Enough Data")
            return None
        
        #get last date in the dataset
        last_date = df.index[-1]
        next_date = last_date + DateOffset(days=1)
        
        
        predicted_price = self.predict_price(symbol, next_date)
        current_price = self.get_stock_price(symbol)
        print(f'current price', current_price)
        
        
        if predicted_price is not None:
            percentage_error = ((predicted_price - current_price) / abs(current_price)) * 100
            print(f"Percent error: {percentage_error}")
            
            if predicted_price > current_price:
                return "Buy"
            elif predicted_price < current_price:
                return "Sell"
            else:
                return "Hold"
        else:
            return None