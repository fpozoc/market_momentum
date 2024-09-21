"""
analyze_all_stocks_with_market_cap_filter.py

This script analyzes stock data using various technical indicators such as EMA, RSI, ADX, Donchian Channel, and Volume.
It processes all stock CSV files in the specified directory, computes the indicators for each stock, filters the results based
on market capitalization from the fundamentals data, and saves the results into a CSV file, along with a link to Yahoo Finance
for each stock.

Additionally, the script generates visualizations for the top 10 stocks that pass the market cap filter and saves them as images.

Functions:
- `load_stock_descriptions`: Loads stock descriptions from a specified file (e.g., NASDAQ.txt).
- `load_fundamentals`: Loads stock fundamentals (e.g., market cap) from a CSV file.
- `process_stock_file`: Processes each stock's CSV file, calculates technical indicator scores, applies the market cap filter, and stores the results.
- `plot_stock_analysis`: Generates a candlestick chart with various technical indicators (EMA, RSI, Bollinger Bands, ADX, and Volume).
- `parse_arguments`: Parses command-line arguments for data folder, output folder, description file, fundamentals file, and market cap threshold.

Each result includes:
- Symbol, Description, Market Cap, Above Cap Threshold flag, EMA Score, RSI Score, ADX Score, Donchian Score, Volume Score, Total Score, and a Yahoo Finance link.

Dependencies:
- pandas
- tqdm (for progress bar)
- matplotlib (for plotting)
- mplfinance (for plotting stock data)
- indicators (custom module for technical indicator analysis)
- argparse (for argument parsing)

Install dependencies:
pip install pandas tqdm matplotlib mplfinance talib argparse

Usage:
    python analyze_all_stocks_with_market_cap_filter.py --data_folder <path_to_csv_folder> \
        --output_folder <path_to_output_folder> \
        --description_file <path_to_ticker_description_file> \
        --fundamentals_file <path_to_fundamentals_file> \
        --cap_threshold <market_cap_threshold>

Example:
    python scripts/analyze_all_stocks_with_market_cap_filter.py --data_folder data/stock_data \
        --output_folder data/opportunities \
        --description_file data/tickers/NASDAQ.txt \
        --fundamentals_file data/fundamentals/complemented_fundamentals_yahoo_data.csv \
        --cap_threshold 1000000000

This will analyze all stock data in the specified folder, filter stocks based on a market cap of $1 billion, save the results
in a CSV file, and create visualizations for the top 10 stocks in a folder named with today's date.
"""

import os
import pandas as pd
from tqdm import tqdm
from indicators import analyze_ema, analyze_rsi, analyze_adx, analyze_donchian, analyze_volume
from datetime import datetime
import matplotlib.pyplot as plt
import mplfinance as mpf
import argparse
import yfinance as yf
import talib as ta
from datetime import timedelta

# Function to load stock descriptions from a file (e.g., NASDAQ.txt)
def load_stock_descriptions(file_path):
    descriptions = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip the header
        for line in lines:
            symbol, description = line.strip().split('\t', 1)  # Extract the symbol and description
            descriptions[symbol] = description
    return descriptions

# Function to load fundamentals data from the CSV file
def load_fundamentals(file_path):
    return pd.read_csv(file_path)

# Function to process each stock file and analyze it
def process_stock_file(file_path, symbol, descriptions, fundamentals, cap_threshold, analysis_results):
    try:
        # Load the stock data from CSV
        data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        
        # Ensure there is enough data for analysis
        if len(data) < 50:  # Minimum length for most indicators
            return

        # Run the analysis functions and collect scores
        ema_score, ema_entry, ema_exit = analyze_ema(data)
        rsi_score, rsi_entry, rsi_exit = analyze_rsi(data)
        adx_score, adx_entry, adx_exit = analyze_adx(data)
        donchian_score, donchian_entry, donchian_exit = analyze_donchian(data)
        volume_score, volume_entry, volume_exit = analyze_volume(data)
        
        # Calculate the total score
        total_score = (ema_score + rsi_score + adx_score + donchian_score + volume_score) / 5
        
        # Get the stock description and market cap
        description = descriptions.get(symbol, 'No description available')
        market_cap = fundamentals.loc[fundamentals['Symbol'] == symbol, 'Market Cap'].values[0] if symbol in fundamentals['Symbol'].values else None
        is_above_cap_threshold = market_cap >= cap_threshold if market_cap else False
        yahoo_finance_link = f'https://finance.yahoo.com/lookup/?s={symbol}'
        
        # Store the results in the analysis list
        analysis_results.append({
            'Symbol': symbol,
            'Description': description,
            'Market Cap': market_cap,
            'Above Cap Threshold': is_above_cap_threshold,
            'EMA Score': ema_score,
            'RSI Score': rsi_score,
            'ADX Score': adx_score,
            'Donchian Score': donchian_score,
            'Volume Score': volume_score,
            'Total Score': total_score,
            'Yahoo Finance Link': yahoo_finance_link
        })
    except Exception as e:
        print(f"Error processing {symbol}: {e}")

# Function to plot stock data with detailed technical analysis for top 10 stocks
def plot_stock_analysis(symbol, data, stock_description, output_folder, rank):
    # Calculate EMAs
    data['EMA_20'] = ta.EMA(data['Close'], timeperiod=20)
    data['EMA_50'] = ta.EMA(data['Close'], timeperiod=50)
    
    # Calculate RSI
    data['RSI'] = ta.RSI(data['Close'], timeperiod=14)
    
    # Calculate Bollinger Bands
    data['Upper_BB'], data['Middle_BB'], data['Lower_BB'] = ta.BBANDS(data['Close'], timeperiod=20)
    
    # Calculate ADX
    data['ADX'] = ta.ADX(data['High'], data['Low'], data['Close'], timeperiod=14)
    
    # Calculate price variation over 2 and 6 weeks
    current_price = data['Close'].iloc[-1]
    two_weeks_ago = data.index[-1] - timedelta(weeks=2)
    six_weeks_ago = data.index[-1] - timedelta(weeks=6)
    price_2w = data.loc[data.index <= two_weeks_ago]['Close'].iloc[-1] if len(data[data.index <= two_weeks_ago]) > 0 else None
    price_6w = data.loc[data.index <= six_weeks_ago]['Close'].iloc[-1] if len(data[data.index <= six_weeks_ago]) > 0 else None
    variation_2w = ((current_price - price_2w) / price_2w * 100) if price_2w else None
    variation_6w = ((current_price - price_6w) / price_6w * 100) if price_6w else None
    
    # Plot the stock
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
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
    ax2.axhline(70, color='red', linestyle='--')  # Overbought level
    ax2.axhline(30, color='green', linestyle='--')  # Oversold level
    ax2.set_title('RSI (Relative Strength Index)', fontsize=14)
    ax2.legend()

    # Volume and ADX Plot
    ax3.plot(data.index, data['ADX'], color='orange', label='ADX')
    ax3.bar(data.index, data['Volume'], color='gray', alpha=0.3)
    ax3.set_title('ADX and Volume', fontsize=14)
    ax3.legend()

    plt.tight_layout()

    # Save the plot to the output folder
    plot_path = os.path.join(output_folder, f"top_{rank}_{symbol}.png")
    plt.savefig(plot_path)
    plt.close()

# Function to plot and save the analysis for top 10 stocks
def plot_top_stocks(top_stocks, data_folder, output_folder):
    for rank, stock in enumerate(top_stocks, start=1):
        symbol = stock['Symbol']
        description = stock['Description']
        file_path = os.path.join(data_folder, f"{symbol}.csv")
        data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        plot_stock_analysis(symbol, data, description, output_folder, rank)

# Argument parser function
def parse_arguments():
    parser = argparse.ArgumentParser(description="Analyze stock data and compute technical indicators with market cap filtering.")
    parser.add_argument('--data_folder', type=str, required=True, help="Path to the folder containing stock CSV files.")
    parser.add_argument('--output_folder', type=str, required=True, help="Path to the folder where analysis results will be saved.")
    parser.add_argument('--description_file', type=str, required=True, help="Path to the file containing stock descriptions.")
    parser.add_argument('--fundamentals_file', type=str, required=True, help="Path to the CSV file containing stock fundamentals.")
    parser.add_argument('--cap_threshold', type=float, default=1e9, help="Market cap threshold for filtering stocks.")
    return parser.parse_args()

# Main entry point
if __name__ == "__main__":
    args = parse_arguments()

    # Create the output folder if it doesn't exist, with today's date
    today_date = datetime.today().strftime('%Y-%m-%d')
    output_folder = os.path.join(args.output_folder, f"{today_date}_indicators_analysis")
    os.makedirs(output_folder, exist_ok=True)

    # Generate the output file path for the final analysis
    output_file = os.path.join(output_folder, f"{today_date}_indicators_analysis.csv")

    # List to store the results of the analysis
    analysis_results = []

    # Load stock descriptions and fundamentals
    descriptions = load_stock_descriptions(args.description_file)
    fundamentals = load_fundamentals(args.fundamentals_file)

    # Get list of all stock CSV files
    stock_files = [file for file in os.listdir(args.data_folder) if file.endswith('.csv')]

    # Initialize the progress bar using tqdm
    with tqdm(total=len(stock_files), desc="Analyzing Stocks", unit="stock") as pbar:
        # Process each stock file and update the progress bar
        for file_name in stock_files:
            symbol = file_name.replace('.csv', '')
            file_path = os.path.join(args.data_folder, file_name)
            process_stock_file(file_path, symbol, descriptions, fundamentals, args.cap_threshold, analysis_results)
            pbar.update(1)  # Update progress

    # Convert the results to a DataFrame
    analysis_df = pd.DataFrame(analysis_results)

    # Sort the analysis by total score in descending order
    sorted_analysis_df = analysis_df.sort_values(by='Total Score', ascending=False)

    # Save the sorted analysis to a CSV file
    sorted_analysis_df.to_csv(output_file, index=False)

    # Filter top 10 stocks that passed the market cap filter
    top_10_stocks = sorted_analysis_df[sorted_analysis_df['Above Cap Threshold']].head(10).to_dict('records')

    # Plot the top 10 stocks
    plot_top_stocks(top_10_stocks, args.data_folder, output_folder)

    print(f"Analysis complete. Results saved to {output_file}.")