# Makefile for stock analysis pipeline

# Variables
TICKERS_FILE = data/tickers/NASDAQ.txt
STOCK_DATA_DIR = data/stock_data
FUNDAMENTALS_FILE = data/complemented_fundamentals_yahoo_data.csv
OUTPUT_DIR = data/opportunities

# Default target: Run the full pipeline
all: get_stocks complement_yahoo update_data analyze_stocks

# Step 1: Get stock data from tickers
get_stocks:
	@echo "Fetching stock data for tickers from $(TICKERS_FILE)..."
	python scripts/get_stocks_from_tickers.py $(TICKERS_FILE) $(STOCK_DATA_DIR)

# Step 2: Complement data with Yahoo Finance fundamentals
complement_yahoo:
	@echo "Complementing stock data with Yahoo Finance fundamentals..."
	python scripts/complement_with_yahoo_data.py --input_file $(TICKERS_FILE) --output_file $(FUNDAMENTALS_FILE)

# Step 3: Update stock data
update_data:
	@echo "Updating stock data in $(STOCK_DATA_DIR)..."
	python scripts/update_stock_data.py $(STOCK_DATA_DIR)

# Step 4: Analyze all stocks and generate opportunities
analyze_stocks:
	@echo "Analyzing all stocks in $(STOCK_DATA_DIR)..."
	python scripts/analyze_all_stocks.py --data_folder $(STOCK_DATA_DIR) --output_folder $(OUTPUT_DIR) --description_file $(TICKERS_FILE)

# Clean up (optional)
clean:
	@echo "Cleaning up generated data files..."
	rm -rf $(STOCK_DATA_DIR)/* $(OUTPUT_DIR)/* $(FUNDAMENTALS_FILE)

# Help command
help:
	@echo "Available targets:"
	@echo "  all               - Run the full pipeline"
	@echo "  get_stocks        - Fetch stock data for tickers"
	@echo "  complement_yahoo  - Complement stock data with Yahoo Finance fundamentals"
	@echo "  update_data       - Update stock data"
	@echo "  analyze_stocks    - Analyze all stocks and generate opportunities"
	@echo "  clean             - Remove all generated data"