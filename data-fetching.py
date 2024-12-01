from dotenv import load_dotenv
import os
import requests

# Load environment variables from the .env file
load_dotenv()

# Fetch the API key from the environment
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

def get_stock_data(symbol):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data['Time Series (Daily)']

stock_data = get_stock_data('AAPL')
print(stock_data)
