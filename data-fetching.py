import os
from dotenv import load_dotenv
from langchain_openai import OpenAI  # Updated import from langchain-openai
from langchain.tools import Tool
from langchain.agents import initialize_agent
import requests
from datetime import datetime, timedelta

# Load environment variables from the .env file
load_dotenv()

# Get the OpenAI API key from the environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Alpha Vantage API key (Replace with your actual API key)
ALPHA_VANTAGE_API_KEY = 'your_alpha_vantage_api_key'

# Function to fetch closing prices from Alpha Vantage
def get_closing_prices(ticker: str, start_date: str, end_date: str) -> str:
    """
    Fetch the daily closing prices for a given stock ticker from Alpha Vantage.
    """
    url = f'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': ticker,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'full'  # 'compact' for last 100 data points, 'full' for the entire available history
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    # Handle any errors from the API response
    if "Error Message" in data:
        return f"Error: {data['Error Message']}"
    if "Note" in data:
        return f"Error: {data['Note']}"
    
    # Extract the time series data (daily stock prices)
    time_series = data.get("Time Series (Daily)", {})
    
    # Filter data for the specified date range
    closing_prices = []
    for date, daily_data in time_series.items():
        if start_date <= date <= end_date:
            closing_prices.append(f"{date}: {daily_data['4. close']}")
    
    # Return the formatted closing prices
    if closing_prices:
        result = f"Closing prices for {ticker} from {start_date} to {end_date}:\n"
        result += "\n".join(closing_prices)
    else:
        result = f"No data found for {ticker} between {start_date} and {end_date}."
    
    return result

# Function to parse the date range from a query (for example: "last year")
def parse_date_range(query: str):
    """
    Parse a date range from the query (e.g., 'last year').
    """
    if "last year" in query:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
    return None, None

# Initialize the OpenAI language model for LangChain with the API key
llm = OpenAI(temperature=0, openai_api_key=openai_api_key)

# Define LangChain tool using the get_closing_prices function
tool = Tool(
    name="Get Closing Prices",
    func=get_closing_prices,
    description="Fetch closing prices of a stock for a specified date range using Alpha Vantage."
)

# Initialize the LangChain agent with the tool and OpenAI LLM
agent = initialize_agent([tool], llm, agent_type="zero-shot-react-description", verbose=True)

# Main function for testing or execution
if __name__ == "__main__":
    # Example query: User asks for the closing prices of Apple over the last year
    query = "What were the closing prices for Apple over the last year?"
    
    # Parse the date range from the query
    start_date, end_date = parse_date_range(query)

    # Fetch the closing prices using the tool
    if start_date and end_date:
        response = get_closing_prices("AAPL", start_date, end_date)
        print(response)
    else:
        # Use LangChain agent to process more complex queries
        response = agent.run(query)
        print(response)
