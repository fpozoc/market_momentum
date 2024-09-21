"""
analyze_all_stocks.py

This script analyzes stock data using various technical indicators such as EMA, RSI, ADX, Donchian Channel, and Volume.
It processes all stock CSV files in the specified directory, computes the indicators for each stock, and saves the results
into a CSV file, along with a link to Yahoo Finance for each stock.

Functions:
- `load_stock_descriptions`: Loads stock descriptions from a specified file (e.g., NASDAQ.txt).
- `process_stock_file`: Processes each stock's CSV file, calculates technical indicator scores, and stores the results.
- `analyze_ema`, `analyze_rsi`, `analyze_adx`, `analyze_donchian`, `analyze_volume`: Custom indicator analysis functions.

Each result includes:
- Symbol, Description, EMA Score, RSI Score, ADX Score, Donchian Score, Volume Score, Total Score, and a Yahoo Finance link.

Dependencies:
- pandas
- tqdm (for progress bar)
- indicators (custom module for technical indicator analysis)

Install dependencies:
pip install pandas tqdm

Usage:
    python scripts/analyze_all_stocks.py --data_folder <path_to_csv_folder> --output_folder <path_to_output_folder> --description_file <path_to_ticker_description_file>

Example:
    python scripts/analyze_all_stocks.py --data_folder data/stock_data --output_folder data/opportunities --description_file data/tickers/NASDAQ.txt

This will analyze all stock data in the specified folder and save the results in a CSV file with today's date in the filename.
"""

import os
import pandas as pd
from tqdm import tqdm
from indicators import analyze_ema, analyze_rsi, analyze_adx, analyze_donchian, analyze_volume
from datetime import datetime
import argparse

# Function to load stock descriptions from a file (e.g., NASDAQ.txt)
def load_stock_descriptions(file_path):
    """
    Loads stock descriptions from a specified text file.
    
    Args:
        file_path (str): Path to the file containing stock symbols and descriptions.
        
    Returns:
        dict: A dictionary mapping stock symbols to their descriptions.
    """
    descriptions = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip the header
        for line in lines:
            symbol, description = line.strip().split('\t', 1)  # Extract the symbol and description
            descriptions[symbol] = description
    return descriptions

# Function to process each stock file and analyze it
def process_stock_file(file_path, symbol, descriptions, analysis_results):
    """
    Processes a stock CSV file, calculates technical indicator scores, and appends the results to the analysis list.

    Args:
        file_path (str): Path to the CSV file containing stock data.
        symbol (str): The stock symbol.
        descriptions (dict): A dictionary mapping stock symbols to their descriptions.
        analysis_results (list): List to store the results of the analysis.
    """
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
        
        # Get the stock description and create a Yahoo Finance link
        description = descriptions.get(symbol, 'No description available')
        yahoo_finance_link = f'https://finance.yahoo.com/lookup/?s={symbol}'
        
        # Store the results in the analysis list
        analysis_results.append({
            'Symbol': symbol,
            'Description': description,
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

# Argument parser function
def parse_arguments():
    """
    Parses command-line arguments for the script.

    Args:
        None

    Returns:
        Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Analyze stock data and compute technical indicators.")
    parser.add_argument('--data_folder', type=str, required=True, help="Path to the folder containing stock CSV files.")
    parser.add_argument('--output_folder', type=str, required=True, help="Path to the folder where analysis results will be saved.")
    parser.add_argument('--description_file', type=str, required=True, help="Path to the file containing stock descriptions.")
    return parser.parse_args()

# Main entry point
if __name__ == "__main__":
    args = parse_arguments()

    # Create the output folder if it doesn't exist
    os.makedirs(args.output_folder, exist_ok=True)

    # Generate the filename with today's date
    today_date = datetime.today().strftime('%Y-%m-%d')
    output_file = f'{args.output_folder}/{today_date}_indicators_analysis.csv'

    # List to store the results of the analysis
    analysis_results = []

    # Load stock descriptions from the provided file
    descriptions = load_stock_descriptions(args.description_file)

    # Get list of all stock CSV files
    stock_files = [file for file in os.listdir(args.data_folder) if file.endswith('.csv')]

    # Initialize the progress bar using tqdm
    with tqdm(total=len(stock_files), desc="Analyzing Stocks", unit="stock") as pbar:
        # Process each stock file and update the progress bar
        for file_name in stock_files:
            symbol = file_name.replace('.csv', '')
            file_path = os.path.join(args.data_folder, file_name)
            process_stock_file(file_path, symbol, descriptions, analysis_results)
            pbar.update(1)  # Update progress

    # Convert the results to a DataFrame
    analysis_df = pd.DataFrame(analysis_results)

    # Sort the analysis by total score in descending order
    sorted_analysis_df = analysis_df.sort_values(by='Total Score', ascending=False)

    # Save the sorted analysis to a CSV file
    sorted_analysis_df.to_csv(output_file, index=False)

    print(f"Analysis complete. Results saved to {output_file}.")