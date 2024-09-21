"""
Stock Data Downloader Script

This script downloads historical stock data for the first stock symbol found in a text file 
that contains stock tickers. It uses the yfinance library to fetch stock data for the last 
5 years (or a specified period) and saves the data to a CSV file in a specified output folder.

The script is designed to be run from the command line with two arguments:
1. The path to the text file containing stock tickers.
2. The path to the folder where the downloaded CSV file should be saved.

Each line in the text file is expected to contain a stock symbol followed by a description, 
separated by a tab. The first line (header) is ignored.

Usage:
    python scripts/get_stocks_from_tickers.py <tickers_file> <output_folder>

    - `<tickers_file>`: Path to the text file containing stock tickers (e.g., NASDAQ.txt).
    - `<output_folder>`: Path to the folder where the CSV file should be saved.

Example:
    python scripts/get_stocks_from_tickers.py data/tickers/NASDAQ.txt data/stock_data

This will download the stock data for the first symbol in NASDAQ.txt and save it as a CSV file 
in the `data/stock_data` folder.

Arguments:
    tickers_file: str - The path to the file that contains stock symbols.
    output_folder: str - The path to the folder where stock data CSV files will be saved.

Dependencies:
    - pandas
    - yfinance
    - argparse
    - tqdm
    - os

Functions:
    - parse_arguments(): Parses command-line arguments.
    - get_first_stock_symbol(file_path): Reads the first stock symbol from the specified file.
    - download_stock_data(symbol, period): Downloads historical stock data using yfinance.
    - main(): The main function that orchestrates argument parsing, downloading, and saving of stock data.

Author: Fernando Pozo
Date: 2024-09-21
"""

import os
import pandas as pd
import yfinance as yf
import argparse
from tqdm import tqdm  # For progress bar

# Function to parse command-line arguments
def parse_arguments():
    """
    Parses command-line arguments for the script.

    Arguments:
        tickers_file (str): The path to the text file containing stock tickers.
        output_folder (str): The path to the folder where stock data CSV files will be saved.
    
    Returns:
        Namespace: A namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Download stock data for the first symbol from a tickers file and save it to a CSV file."
    )
    parser.add_argument(
        "tickers_file", 
        type=str, 
        help="Path to the text file containing stock tickers."
    )
    parser.add_argument(
        "output_folder", 
        type=str, 
        help="Path to the folder where stock data CSV files will be saved."
    )
    return parser.parse_args()

# Function to read the first stock symbol from the specified file
def get_first_stock_symbol(file_path: str) -> str:
    """
    Reads the first stock symbol from the specified text file.

    This function reads a text file containing stock tickers, 
    skips the first line (assumed to be a header), 
    and extracts the first stock ticker symbol from the file.

    Args:
        file_path (str): The path to the file containing stock symbols.
    
    Returns:
        str: The first stock symbol found in the file.
    """
    with open(file_path, 'r') as file:
        # Skip the first line (header)
        lines = file.readlines()[1:]
        # Get the first stock symbol (assuming the first column is the symbol)
        first_stock = lines[0].split('\t')[0]
        return first_stock

# Function to download historical stock data using yfinance
def download_stock_data(symbol: str, period: str = '5y') -> pd.DataFrame:
    """
    Downloads historical stock data for a given stock symbol using the yfinance library.

    This function fetches historical data for the specified stock symbol over a period of time.
    By default, it downloads the last 5 years of data.

    Args:
        symbol (str): The stock symbol to download data for.
        period (str): The period of historical data to download (default: '5y').
    
    Returns:
        pd.DataFrame: A pandas DataFrame containing the historical stock data.
    """
    stock_data = yf.download(symbol, period=period)
    return stock_data

# Main function to process the stock symbols and download data
def main():
    """
    Main function of the script.

    This function performs the following tasks:
    1. Parses command-line arguments to get the tickers file and output folder.
    2. Reads the first stock symbol from the specified tickers file.
    3. Downloads the last 5 years of historical stock data for the first symbol using yfinance.
    4. Saves the downloaded stock data to a CSV file in the specified output folder.
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Get the first symbol from the specified tickers file
    first_symbol = get_first_stock_symbol(args.tickers_file)
    print(f"Downloading data for: {first_symbol}")

    # Download historical data for the first stock with tqdm progress bar
    with tqdm(total=1, desc=f"Downloading {first_symbol}", unit="stock") as pbar:
        stock_data = download_stock_data(first_symbol)
        pbar.update(1)

    # Ensure the output folder exists, create it if necessary
    os.makedirs(args.output_folder, exist_ok=True)

    # Save the data to a CSV file
    csv_file_path = os.path.join(args.output_folder, f"{first_symbol}.csv")
    stock_data.to_csv(csv_file_path)
    
    print(f"Data for {first_symbol} saved to {csv_file_path}")

# Run the main function
if __name__ == "__main__":
    main()