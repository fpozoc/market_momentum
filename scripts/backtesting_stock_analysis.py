"""
backtesting_stock_analysis.py

This script performs a backtest of stock data based on technical indicators such as EMA, RSI, ADX, Donchian Channel, and Volume.
It calculates technical scores for each stock in a specified folder, selects the best stock based on scores, and simulates an investment strategy with stop-loss and reevaluation periods.

Functions:
- `get_stock_data`: Loads stock data for a given symbol from a CSV file.
- `load_and_score_stock_data`: Loads stock data from CSV files and calculates technical scores for each day.
- `get_best_stock`: Selects the best stock for a given day based on the highest technical score.
- `backtest`: Runs the backtest simulation using the calculated scores and logs the investment details.

Parameters:
- Stop-loss percentage: Set at 5% (adjustable)
- Initial investment: $50,000
- Reevaluation period: 2 weeks (adjustable)

Dependencies:
- pandas: For handling tabular stock data.
- tqdm: For showing progress bars during the loading and backtesting phases.
- argparse: For handling command-line arguments.
- indicators (module): Custom module that contains the functions `analyze_ema`, `analyze_rsi`, `analyze_adx`, `analyze_donchian`, and `analyze_volume`.

Install dependencies:
pip install pandas tqdm argparse

Usage:
    python backtesting_stock_analysis.py --data_folder <path_to_csv_folder> --start_date <YYYY-MM-DD> --end_date <YYYY-MM-DD>

Example:
    python backtesting_stock_analysis.py --data_folder data/stock_data --start_date 2022-01-01 --end_date 2022-03-15

This will load stock data from the `data/stock_data` folder, calculate scores, and run the backtest for the specified date range.
"""

import os
import pandas as pd
from datetime import timedelta
from tqdm import tqdm
from indicators import analyze_ema, analyze_rsi, analyze_adx, analyze_donchian, analyze_volume
import argparse

# Parameters
STOP_LOSS = 0.05  # Stop-loss percentage
INITIAL_INVESTMENT = 50000  # Initial investment
REEVALUATION_PERIOD = 14  # Reevaluate every 2 weeks

# Function to load stock data for a specific symbol
def get_stock_data(symbol, data_folder):
    """
    Loads stock data for a given symbol from a CSV file.

    Args:
        symbol (str): The stock ticker symbol.
        data_folder (str): The folder where stock CSV files are stored.

    Returns:
        pd.DataFrame: Stock data for the given symbol, or an empty DataFrame if the file is not found or invalid.
    """
    file_path = os.path.join(data_folder, f"{symbol}.csv")
    if os.path.exists(file_path):
        stock_data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
        
        # Ensure required columns are present
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in stock_data.columns]
        if missing_columns:
            print(f"Data for {symbol} is missing required columns: {', '.join(missing_columns)}.")
            return pd.DataFrame()  # Return an empty DataFrame if columns are missing
        
        return stock_data
    else:
        print(f"Data for {symbol} not found.")
        return pd.DataFrame()

# Function to load all stock data from the folder and calculate technical scores
def load_and_score_stock_data(data_folder, start_date, end_date):
    """
    Loads stock data from CSV files and calculates technical scores for each day in the specified date range.

    Args:
        data_folder (str): The folder where stock CSV files are stored.
        start_date (str): The start date of the backtest period.
        end_date (str): The end date of the backtest period.

    Returns:
        pd.DataFrame: A DataFrame containing the date, symbol, and total score for each stock.
    """
    stock_scores = []
    stock_files = [f for f in os.listdir(data_folder) if f.endswith('.csv')]

    # Iterate through all the CSV files and calculate daily scores
    for stock_file in tqdm(stock_files, desc="Loading and scoring stock data"):
        symbol = stock_file.replace('.csv', '')
        stock_data = get_stock_data(symbol, data_folder)
        
        # Filter data for the test range
        stock_data = stock_data[(stock_data.index >= start_date) & (stock_data.index <= end_date)]
        
        # Skip if insufficient data
        if len(stock_data) < 50:
            continue
        
        # Calculate technical scores for each day
        for date, data in stock_data.iterrows():
            try:
                if len(stock_data.loc[:date]) >= 50:
                    # Calculate technical indicator scores
                    ema_score, _, _ = analyze_ema(stock_data.loc[:date])
                    rsi_score, _, _ = analyze_rsi(stock_data.loc[:date])
                    adx_score, _, _ = analyze_adx(stock_data.loc[:date])
                    donchian_score, _, _ = analyze_donchian(stock_data.loc[:date])
                    volume_score, _, _ = analyze_volume(stock_data.loc[:date])

                    # Calculate the total score
                    total_score = (ema_score + rsi_score + adx_score + donchian_score + volume_score) / 5

                    # Store the date, symbol, and score
                    stock_scores.append({
                        'Date': date,
                        'Symbol': symbol,
                        'Score': total_score
                    })
            except Exception as e:
                print(f"Error calculating scores for {symbol} on {date}: {e}")

    return pd.DataFrame(stock_scores)

# Function to get the best stock based on technical scores from the daily scores table
def get_best_stock(date, stock_scores):
    """
    Selects the best stock for a given day based on the highest technical score.

    Args:
        date (str): The date to select the best stock for.
        stock_scores (pd.DataFrame): DataFrame containing stock symbols and their technical scores.

    Returns:
        tuple: (best stock symbol, best score) or (None, None) if no stock is available for the date.
    """
    day_scores = stock_scores[stock_scores['Date'] == date]
    if not day_scores.empty:
        best_stock = day_scores.sort_values(by='Score', ascending=False).iloc[0]
        return best_stock['Symbol'], best_stock['Score']
    return None, None

# Backtest function
def backtest(stock_scores, initial_investment, stop_loss, reevaluation_period, data_folder):
    """
    Runs the backtest simulation and logs the investment details.

    Args:
        stock_scores (pd.DataFrame): DataFrame containing stock symbols and their scores.
        initial_investment (float): The initial amount to invest.
        stop_loss (float): The stop-loss percentage.
        reevaluation_period (int): The period (in days) after which the stock is reevaluated.
        data_folder (str): The folder where stock CSV files are stored.

    Returns:
        pd.DataFrame: A DataFrame containing the investment log.
    """
    investment_log = []
    current_investment = initial_investment
    current_stock = None
    current_shares = 0
    start_date = stock_scores['Date'].min()
    
    with tqdm(total=(stock_scores['Date'].max() - start_date).days // reevaluation_period, desc="Backtesting", unit="2-week period") as pbar:
        current_date = start_date
        while current_date <= stock_scores['Date'].max():
            best_stock, score = get_best_stock(current_date, stock_scores)
            if not best_stock:
                current_date += timedelta(days=reevaluation_period)
                pbar.update(1)
                continue

            stock_data = get_stock_data(best_stock, data_folder)
            if stock_data.empty:
                current_date += timedelta(days=reevaluation_period)
                pbar.update(1)
                continue

            if current_stock != best_stock:
                entry_price = stock_data.loc[stock_data.index == current_date, 'Open'].values[0]
                current_shares = current_investment / entry_price
                current_stock = best_stock
                print(f"Switched to {current_stock} on {current_date} with {current_shares} shares.")

            reevaluation_end_date = current_date + timedelta(days=reevaluation_period)
            for day in stock_data.loc[current_date:reevaluation_end_date].itertuples():
                if day.Low <= entry_price * (1 - stop_loss):
                    exit_price = entry_price * (1 - stop_loss)
                    current_investment = current_shares * exit_price
                    investment_log.append({
                        'Date': day.Index,
                        'Symbol': current_stock,
                        'Action': 'Stop-Loss',
                        'Shares': current_shares,
                        'Exit Price': exit_price,
                        'Investment Value': current_investment
                    })
                    best_stock, score = get_best_stock(day.Index, stock_scores)
                    stock_data = get_stock_data(best_stock, data_folder)
                    entry_price = stock_data.loc[stock_data.index == day.Index, 'Open'].values[0]
                    current_shares = current_investment / entry_price
                    current_stock = best_stock
                    print(f"Stop-Loss hit. Switched to {current_stock} on {day.Index}")
                    break
            
            reevaluation_price = stock_data.loc[stock_data.index ==             reevaluation_end_date, 'Open'].values[0]
            current_investment = current_shares * reevaluation_price
            investment_log.append({
                'Date': reevaluation_end_date,
                'Symbol': current_stock,
                'Action': 'Reevaluate',
                'Shares': current_shares,
                'Exit Price': reevaluation_price,
                'Investment Value': current_investment
            })

            # Move to the next 2-week period
            current_date += timedelta(days=reevaluation_period)
            pbar.update(1)

    return pd.DataFrame(investment_log)

# Argument parser function
def parse_arguments():
    """
    Parses command-line arguments for the script.

    Args:
        None

    Returns:
        Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Backtest stock data using technical indicators and investment strategies.")
    parser.add_argument('--data_folder', type=str, required=True, help="Path to the folder containing stock CSV files.")
    parser.add_argument('--start_date', type=str, required=True, help="Start date for the backtest (YYYY-MM-DD).")
    parser.add_argument('--end_date', type=str, required=True, help="End date for the backtest (YYYY-MM-DD).")
    return parser.parse_args()

# Main entry point
if __name__ == "__main__":
    args = parse_arguments()

    # Load and score stock data
    stock_scores = load_and_score_stock_data(args.data_folder, args.start_date, args.end_date)

    # Print stock_scores for debugging
    print("Stock scores:")
    print(stock_scores.head())

    # Run the backtest for the test period
    backtest_results = backtest(stock_scores, INITIAL_INVESTMENT, STOP_LOSS, REEVALUATION_PERIOD, args.data_folder)

    # Print final earnings and the investment log
    final_investment_value = backtest_results.iloc[-1]['Investment Value']
    print(f"Final investment value for the test period: ${final_investment_value:.2f}")

    # Save the backtest results to a CSV file
    output_file = 'data/backtesting/backtest_results.csv'
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    backtest_results.to_csv(output_file, index=False)
    print(f"Backtest results saved to {output_file}.")