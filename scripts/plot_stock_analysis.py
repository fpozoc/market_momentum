"""
plot_stock_analysis.py

This script downloads historical stock data and performs a technical analysis using various indicators: 
EMA (Exponential Moving Averages), RSI (Relative Strength Index), Bollinger Bands, ADX (Average Directional Index), 
and Volume. It then generates a detailed candlestick chart with overlaid indicators, as well as plots for RSI and ADX.

The analysis is supplemented with stock price variations over 2 and 6 weeks to help assess the stock's short-term 
and mid-term performance. The chart includes a candlestick chart with EMAs, Bollinger Bands, RSI, ADX, and Volume.

Functions:
- `load_stock_descriptions`: Loads stock descriptions from a file (e.g., NASDAQ.txt).
- `download_stock_data`: Downloads historical stock data for a given symbol from Yahoo Finance.
- `calculate_price_variation`: Calculates the stock's price variations over 2 and 6 weeks.
- `plot_stock_analysis`: Generates a candlestick chart with various technical indicators (EMA, RSI, Bollinger Bands, ADX, and Volume).
  
Dependencies:
- pandas: For handling stock data.
- yfinance: For downloading stock data from Yahoo Finance.
- matplotlib and mplfinance: For plotting the stock analysis and candlestick chart.
- talib: For calculating technical indicators.
- datetime: For date manipulations (timedelta).

Install dependencies:
pip install yfinance pandas matplotlib mplfinance ta-lib

Usage:
1. Define the path to the stock descriptions file (e.g., `data/tickers/NASDAQ.txt`).
2. Specify the stock symbol to analyze (e.g., 'AAPL').
3. The script will download the historical stock data, analyze it using technical indicators, 
   and generate a candlestick chart with overlaid technical indicators.

Example:
    python plot_stock_analysis.py

This will download and analyze stock data for a specified symbol and produce a visual chart with EMA, RSI, ADX, 
Bollinger Bands, and price variations over 2 and 6 weeks.
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import talib as ta
from datetime import timedelta

# Load descriptions from NASDAQ.txt file (or similar)
def load_stock_descriptions(file_path):
    descriptions = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip the header
        for line in lines:
            symbol, description = line.strip().split('\t', 1)  # Extract the symbol and description
            descriptions[symbol] = description
    return descriptions

# Download historical stock data from Yahoo Finance
def download_stock_data(symbol, period='6mo'):
    stock_data = yf.download(symbol, period=period)
    return stock_data

# Calculate price variation over 2 and 6 weeks
def calculate_price_variation(data):
    current_price = data['Close'].iloc[-1]  # Latest closing price
    two_weeks_ago = data.index[-1] - timedelta(weeks=2)
    six_weeks_ago = data.index[-1] - timedelta(weeks=6)
    
    # Get prices from 2 and 6 weeks ago (if available)
    price_2w = data.loc[data.index <= two_weeks_ago]['Close'].iloc[-1] if len(data[data.index <= two_weeks_ago]) > 0 else None
    price_6w = data.loc[data.index <= six_weeks_ago]['Close'].iloc[-1] if len(data[data.index <= six_weeks_ago]) > 0 else None
    
    # Calculate percentage variations
    variation_2w = ((current_price - price_2w) / price_2w * 100) if price_2w else None
    variation_6w = ((current_price - price_6w) / price_6w * 100) if price_6w else None
    
    return current_price, variation_2w, variation_6w

# Plot the candlestick chart with EMA, RSI, Bollinger Bands, Volume, ADX, and price variations
def plot_stock_analysis(symbol, data, stock_description):
    # Calculate EMAs
    data['EMA_20'] = ta.EMA(data['Close'], timeperiod=20)
    data['EMA_50'] = ta.EMA(data['Close'], timeperiod=50)
    
    # Calculate RSI
    data['RSI'] = ta.RSI(data['Close'], timeperiod=14)
    
    # Calculate Bollinger Bands
    data['Upper_BB'], data['Middle_BB'], data['Lower_BB'] = ta.BBANDS(data['Close'], timeperiod=20)
    
    # Calculate ADX
    data['ADX'] = ta.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
    
    # Calculate price and percentage variation
    current_price, variation_2w, variation_6w = calculate_price_variation(data)
    
    # Set up the subplots
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
    
    # Candlestick chart with EMAs and Bollinger Bands
    mpf.plot(data, type='candle', ax=ax1, volume=False, style='charles',
             addplot=[
                 mpf.make_addplot(data['EMA_20'], ax=ax1, color='blue', width=1.5, label='EMA 20'),
                 mpf.make_addplot(data['EMA_50'], ax=ax1, color='red', width=1.5, label='EMA 50'),
                 mpf.make_addplot(data['Upper_BB'], ax=ax1, color='green', linestyle='--', width=1, label='Upper BB'),
                 mpf.make_addplot(data['Lower_BB'], ax=ax1, color='green', linestyle='--', width=1, label='Lower BB')
             ])
    
    # Display the current price, percentage variation, and stock name on the chart
    ax1.text(0.02, 0.9, f"{stock_description}\nPrice: ${current_price:.2f}\n2W Change: {variation_2w:.2f}%\n6W Change: {variation_6w:.2f}%", 
             transform=ax1.transAxes, fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
    
    ax1.set_title(f'{symbol} - Candlestick, EMAs, and Bollinger Bands', fontsize=14)
    
    # RSI Plot
    ax2.plot(data.index, data['RSI'], color='purple', label='RSI')
    ax2.axhline(70, color='red', linestyle='--')
    ax2.axhline(30, color='green', linestyle='--')
    ax2.set_title('RSI (Relative Strength Index)', fontsize=14)
    ax2.legend()
    
    # Volume and ADX Plot
    ax3.plot(data.index, data['ADX'], color='orange', label='ADX')
    ax3.bar(data.index, data['Volume'], color='gray', alpha=0.3)
    ax3.set_title('ADX and Volume', fontsize=14)
    ax3.legend()
    
    plt.tight_layout()
    plt.show()

# Load stock descriptions from NASDAQ.txt (or similar file)
descriptions = load_stock_descriptions('data/tickers/NASDAQ.txt')

# Download data for a stock
symbol = 'AAPL'  # Replace with any stock symbol
stock_data = download_stock_data(symbol)

# Get the stock description for the symbol
stock_description = descriptions.get(symbol, "No description available")

# Plot the stock analysis
plot_stock_analysis(symbol, stock_data, stock_description)