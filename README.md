# Market Momentum

Table of Contents
=================

- [Market Momentum](#market-momentum)
- [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Usage](#usage)
  - [Getting Stock Symbols](#getting-stock-symbols)
  - [Requirements](#requirements)
  - [Makefile](#makefile)

## Overview

Market Momentum is a repository designed to analyze stock data using various technical indicators such as EMA, RSI, ADX, Donchian Channel, and Volume. It automates the process of downloading stock data, computing indicators, and filtering stocks based on market capitalization from the fundamentals data. Additionally, it generates visualizations for top-performing stocks.

## Features

- Fetch stock data from Yahoo Finance.
- Compute technical indicators for stocks (EMA, RSI, ADX, Donchian Channel, Volume).
- Filter stocks based on market capitalization.
- Generate visualizations for top stocks.
- Save analysis results in CSV format.
  
## Usage

To run the analysis, use the following commands:

```bash
# Download stock data from tickers
python scripts/get_stocks_from_tickers.py data/tickers/NASDAQ.txt data/stock_data

# Complement the stock data with fundamentals from Yahoo Finance
python scripts/complement_with_yahoo_data.py --input_file data/tickers/NASDAQ.txt --output_file data/complemented_fundamentals_yahoo_data.csv

# Update stock data
python scripts/update_stock_data.py data/stock_data

# Analyze all stocks and generate opportunities
python scripts/analyze_all_stocks.py --data_folder data/stock_data --output_folder data/opportunities --description_file data/tickers/NASDAQ.txt
```

## Getting Stock Symbols

To get stock symbols for analysis, you can refer to stock listings from this resource:
Stock Symbols - EODData

Download and use these symbols in your stock analysis workflow.

## Requirements

	•	pandas
	•	tqdm
	•	yfinance
	•	matplotlib
	•	mplfinance
	•	talib
	•	argparse

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Makefile

To automate the workflow, you can use the following Makefile commands:

```bash
all:
    python scripts/get_stocks_from_tickers.py data/tickers/NASDAQ.txt data/stock_data
    python scripts/complement_with_yahoo_data.py --input_file data/tickers/NASDAQ.txt --output_file data/complemented_fundamentals_yahoo_data.csv
    python scripts/update_stock_data.py data/stock_data
    python scripts/analyze_all_stocks.py --data_folder data/stock_data --output_folder data/opportunities --description_file data/tickers/NASDAQ.txt
```