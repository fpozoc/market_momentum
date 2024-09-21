"""
Stock Data Updater Script

This script updates historical stock data for all stock symbols that have existing CSV files 
in a specified directory. It uses the `yfinance` library to fetch stock data and updates 
the existing data by appending any new data from the last available date.

Progress is displayed using `tqdm`, showing the percentage of CSV files processed.

Usage:
    python update_stock_data.py <csv_directory>

Example:
    python update_stock_data.py data/stock_data

This will update stock data for all CSV files in the `data/stock_data` folder.

Arguments:
    csv_directory: str - The path to the directory where CSV files with stock data are stored.

Dependencies:
    - pandas
    - yfinance
    - tqdm
    - os

Functions:
    - update_stock_data(symbol, csv_directory): Updates stock data for a specific ticker symbol.
    - process_stock_data(csv_directory): Updates stock data for all CSV files in the specified directory.

Author: Fernando Pozo
Date: 2024-09-21
"""

import os
import pandas as pd
import yfinance as yf
from tqdm import tqdm  # For displaying progress bars
import argparse

# Function to parse command-line arguments
def parse_arguments():
    """
    Parses command-line arguments for the script.

    Arguments:
        csv_directory (str): The path to the directory where CSV files with stock data are stored.

    Returns:
        Namespace: A namespace object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Update stock data for all symbols in a directory containing CSV files."
    )
    parser.add_argument(
        "csv_directory", 
        type=str, 
        help="Path to the directory where stock data CSV files are stored."
    )
    return parser.parse_args()

# Function to update the CSV file with new data
def update_stock_data(symbol, csv_directory):
    """
    Updates the stock data for the given symbol by appending any new data to the existing CSV file.
    
    If the CSV file for the stock already exists, this function loads the file, checks the last date 
    for which data is available, and downloads new data from the day after that date.

    Args:
        symbol (str): The stock ticker symbol to update.
        csv_directory (str): The path to the directory where CSV files with stock data are stored.
    
    Returns:
        None
    """
    csv_file_path = os.path.join(csv_directory, f"{symbol}.csv")
    
    # Check if the CSV file exists
    if os.path.exists(csv_file_path):
        # Load the existing data
        existing_data = pd.read_csv(csv_file_path, index_col='Date', parse_dates=True)
        
        # Get the last date in the existing data
        last_date = existing_data.index[-1]
        
        # Download new data starting from the day after the last available date
        new_data = yf.download(symbol, start=last_date + pd.Timedelta(days=1))
        
        if not new_data.empty:
            # Append the new data to the existing data using pd.concat()
            updated_data = pd.concat([existing_data, new_data])
            updated_data.to_csv(csv_file_path)
            print(f"Data for {symbol} updated successfully.")
        else:
            print(f"No new data for {symbol}.")
    else:
        print(f"File for {symbol} does not exist.")

# Function to process all CSV files in the specified directory
def process_stock_data(csv_directory):
    """
    Processes all stock data files in the specified directory, updating stock data for each symbol.
    
    This function reads each CSV file in the directory and updates the stock data for that symbol 
    by calling `update_stock_data`. The progress is displayed using a `tqdm` progress bar.

    Args:
        csv_directory (str): The path to the directory where CSV files with stock data are stored.
    
    Returns:
        None
    """
    # Get all CSV files in the directory
    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
    
    # Use tqdm to display a progress bar while processing CSV files
    for csv_file in tqdm(csv_files, desc="Processing stock data", unit="file"):
        symbol = csv_file.replace('.csv', '')  # Extract the stock symbol from the file name
        update_stock_data(symbol, csv_directory)

# Main function
def main():
    """
    The main function of the script. It parses command-line arguments and updates stock data 
    for all CSV files in the specified directory.

    Returns:
        None
    """
    # Parse command-line arguments
    args = parse_arguments()

    # Process stock data in the specified directory
    process_stock_data(args.csv_directory)

# Entry point of the script
if __name__ == "__main__":
    main()