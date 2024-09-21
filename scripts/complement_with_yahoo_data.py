"""
complement_with_yahoo_data.py

This script loads a list of stock symbols and their descriptions from a tab-separated file (e.g., NASDAQ.txt), 
fetches additional financial data and company information from Yahoo Finance, and saves the results to a CSV file.

Each stock is enhanced with additional Yahoo Finance data such as market capitalization, P/E ratio, dividend yield, 
52-week highs and lows, beta, sector, industry, and more.

The script allows the user to specify input and output file paths through command-line arguments.

Functions:
- `load_stock_descriptions`: Reads the input file containing stock symbols and descriptions.
- `fetch_yahoo_data`: Fetches financial and company data for a given stock symbol using Yahoo Finance.
- `complement_with_yahoo_data`: Combines stock descriptions with Yahoo Finance data and saves the results to a CSV file.

Dependencies:
- pandas: For handling tabular data.
- yfinance: For fetching stock data from Yahoo Finance.
- tqdm: For showing progress with a progress bar.
- argparse: For handling command-line arguments.

Install dependencies:
pip install pandas yfinance tqdm argparse

Usage:
    python complement_with_yahoo_data.py --input_file <path_to_input_file> --output_file <path_to_output_file>

Example:
    python complement_with_yahoo_data.py --input_file data/tickers/NASDAQ.txt --output_file data/complemented_fundamentals_yahoo_data.csv

This will load stock descriptions from `data/tickers/NASDAQ.txt`, fetch additional data from Yahoo Finance, 
and save the results to `data/complemented_fundamentals_yahoo_data.csv`.
"""

import yfinance as yf
import pandas as pd
from tqdm import tqdm
import argparse

# Load descriptions from the input file
def load_stock_descriptions(file_path):
    """
    Loads stock symbols and descriptions from a tab-separated file.

    Args:
        file_path (str): The path to the input file containing stock symbols and descriptions.
    
    Returns:
        list: A list of dictionaries where each dictionary contains 'Symbol' and 'Description' of a stock.
    """
    descriptions = []
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Skip the header
        for line in lines:
            symbol, description = line.strip().split('\t', 1)  # Extract the symbol and description
            descriptions.append({'Symbol': symbol, 'Description': description})
    return descriptions

# Fetch additional data and fundamentals from Yahoo Finance
def fetch_yahoo_data(symbol):
    """
    Fetches financial and company data from Yahoo Finance for a given stock symbol.

    Args:
        symbol (str): The stock ticker symbol.

    Returns:
        dict: A dictionary of financial and company data, including market cap, P/E ratio, dividend yield, etc.
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            'Market Cap': info.get('marketCap'),
            'P/E Ratio': info.get('trailingPE'),
            'Dividend Yield': info.get('dividendYield'),
            '52-Week High': info.get('fiftyTwoWeekHigh'),
            '52-Week Low': info.get('fiftyTwoWeekLow'),
            'Beta': info.get('beta'),
            'Sector': info.get('sector'),
            'Industry': info.get('industry'),
            'Country': info.get('country'),
            'Full Time Employees': info.get('fullTimeEmployees'),
            'Company Description': info.get('longBusinessSummary')
        }
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return {
            'Market Cap': None,
            'P/E Ratio': None,
            'Dividend Yield': None,
            '52-Week High': None,
            '52-Week Low': None,
            'Beta': None,
            'Sector': None,
            'Industry': None,
            'Country': None,
            'Full Time Employees': None,
            'Company Description': None
        }

# Main function to combine descriptions and Yahoo Finance data
def complement_with_yahoo_data(input_file, output_file):
    """
    Combines stock descriptions from the input file with additional financial data from Yahoo Finance.

    Args:
        input_file (str): The path to the input file containing stock symbols and descriptions.
        output_file (str): The path to the output file where the final data will be saved.
    
    Returns:
        None
    """
    # Load stock descriptions
    stock_data = load_stock_descriptions(input_file)
    
    # Create a DataFrame to hold the final data
    final_data = []
    
    # Initialize tqdm progress bar
    with tqdm(total=len(stock_data), desc="Fetching Yahoo Finance Data", unit="stock") as pbar:
        # Fetch data for each stock
        for stock in stock_data:
            symbol = stock['Symbol']
            yahoo_data = fetch_yahoo_data(symbol)
            final_data.append({
                'Symbol': symbol,
                'Description': stock['Description'],
                **yahoo_data
            })
            # Update progress bar
            pbar.update(1)
    
    # Convert final data to a DataFrame
    final_df = pd.DataFrame(final_data)
    
    # Save to a CSV file
    final_df.to_csv(output_file, index=False)
    print(f"Data saved to {output_file}")

# Argument parser function
def parse_arguments():
    """
    Parses command-line arguments for the script.

    Args:
        None
    
    Returns:
        Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Fetch financial and company data from Yahoo Finance for stock symbols listed in a file."
    )
    parser.add_argument('--input_file', type=str, required=True, help="Path to the input file containing stock symbols and descriptions.")
    parser.add_argument('--output_file', type=str, required=True, help="Path to the output file where results will be saved.")
    return parser.parse_args()

# Main entry point
if __name__ == "__main__":
    args = parse_arguments()
    complement_with_yahoo_data(args.input_file, args.output_file)