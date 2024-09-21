"""
indicators.py

This script contains functions to analyze stock data using different technical indicators: EMA (Exponential Moving Average),
RSI (Relative Strength Index), ADX (Average Directional Index), Donchian Channel, and Volume.

Each function returns a tuple consisting of:
- A signal score (1 to 5), where:
    5 = Strong bullish
    4 = Mild bullish
    3 = Neutral
    2 = Mild bearish
    1 = Strong bearish
- An expected entry price (float or None), which is the suggested price at which to enter a position.
- An expected exit price (float or None), which is the suggested price at which to exit a position.

Dependencies:
- pandas
- ta (for technical analysis indicators like EMA, RSI, ADX, and Donchian Channel)

Install dependencies:
pip install pandas ta
Usage:
Import the functions in your trading strategy code or use them to analyze stock data for entry/exit signals.
"""

import pandas as pd
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.volatility import DonchianChannel

def analyze_ema(data: pd.DataFrame) -> tuple[int, float, float]:
    """
    Analyzes the Exponential Moving Averages (EMA) to detect potential entry and exit points.

    Args:
        data (pd.DataFrame): DataFrame containing stock data with 'Close' prices.

    Returns:
        tuple: (signal_score, expected_entry_price, expected_exit_price)
            signal_score (int): A score from 1 to 5 based on EMA crossover.
            expected_entry_price (float or None): Price where entering the trade is advisable (None if neutral).
            expected_exit_price (float or None): Price where exiting the trade is advisable (None if neutral).
    """
    ema_short = EMAIndicator(data['Close'], window=20).ema_indicator()
    ema_long = EMAIndicator(data['Close'], window=50).ema_indicator()
    
    if len(data) >= 50:
        # Check for crossover and momentum
        if ema_short.iloc[-1] > ema_long.iloc[-1] and ema_short.iloc[-2] < ema_long.iloc[-2]:  # Golden Cross
            return 5, data['Close'].iloc[-1], None  # Strong bullish, enter now, no exit yet
        elif ema_short.iloc[-1] < ema_long.iloc[-1] and ema_short.iloc[-2] > ema_long.iloc[-2]:  # Death Cross
            return 1, None, data['Close'].iloc[-1]  # Strong bearish, exit now
        elif ema_short.iloc[-1] > ema_long.iloc[-1]:
            return 4, data['Close'].iloc[-1], None  # Mild bullish, enter now
        else:
            return 2, None, data['Close'].iloc[-1]  # Mild bearish, exit soon
    return 3, None, None  # Neutral, no action

def analyze_rsi(data: pd.DataFrame) -> tuple[int, float, float]:
    """
    Analyzes RSI for overbought/oversold levels and price divergence to find entry and exit points.

    Args:
        data (pd.DataFrame): DataFrame containing stock data with 'Close' prices.

    Returns:
        tuple: (signal_score, expected_entry_price, expected_exit_price)
            signal_score (int): A score from 1 to 5 based on RSI conditions.
            expected_entry_price (float or None): Price where entering the trade is advisable.
            expected_exit_price (float or None): Price where exiting the trade is advisable.
    """
    rsi = RSIIndicator(data['Close'], window=14).rsi()
    
    if len(data) >= 14:
        # Bullish divergence: price down, RSI up
        if data['Close'].iloc[-1] < data['Close'].iloc[-2] and rsi.iloc[-1] > rsi.iloc[-2]:
            return 5, data['Close'].iloc[-1], None  # Strong bullish divergence, enter now
        # Bearish divergence: price up, RSI down
        elif data['Close'].iloc[-1] > data['Close'].iloc[-2] and rsi.iloc[-1] < rsi.iloc[-2]:
            return 1, None, data['Close'].iloc[-1]  # Strong bearish divergence, exit now
        elif rsi.iloc[-1] < 30:
            return 4, data['Close'].iloc[-1], None  # Oversold, enter now
        elif rsi.iloc[-1] > 70:
            return 2, None, data['Close'].iloc[-1]  # Overbought, exit now
        else:
            return 3, None, None  # Neutral
    return 3, None, None  # Neutral if not enough data

def analyze_adx(data: pd.DataFrame) -> tuple[int, float, float]:
    """
    Analyzes the ADX to determine trend strength and direction, and suggest entry and exit points.

    Args:
        data (pd.DataFrame): DataFrame containing stock data with 'High', 'Low', and 'Close' prices.

    Returns:
        tuple: (signal_score, expected_entry_price, expected_exit_price)
            signal_score (int): A score from 1 to 5 based on ADX strength and direction.
            expected_entry_price (float or None): Price where entering the trade is advisable.
            expected_exit_price (float or None): Price where exiting the trade is advisable.
    """
    adx = ADXIndicator(high=data['High'], low=data['Low'], close=data['Close'], window=14)
    adx_value = adx.adx()
    pdi = adx.adx_pos()
    ndi = adx.adx_neg()

    if len(data) >= 14:
        if adx_value.iloc[-1] > 25:
            if pdi.iloc[-1] > ndi.iloc[-1]:  # Upward trend
                return 5, data['Close'].iloc[-1], None  # Strong bullish trend, enter now
            else:  # Downward trend
                return 1, None, data['Close'].iloc[-1]  # Strong bearish trend, exit now
        elif adx_value.iloc[-1] < 20:  # Weak trend
            return 3, None, None  # Neutral, no action
    return 3, None, None  # Neutral

def analyze_donchian(data: pd.DataFrame) -> tuple[int, float, float]:
    """
    Analyzes Donchian Channel to detect breakouts above or below the channel, indicating entry or exit points.

    Args:
        data (pd.DataFrame): DataFrame containing stock data with 'High', 'Low', and 'Close' prices.

    Returns:
        tuple: (signal_score, expected_entry_price, expected_exit_price)
            signal_score (int): A score from 1 to 5 based on Donchian Channel breakouts.
            expected_entry_price (float or None): Price where entering the trade is advisable.
            expected_exit_price (float or None): Price where exiting the trade is advisable.
    """
    donchian = DonchianChannel(high=data['High'], low=data['Low'], close=data['Close'], window=20)
    high_band = donchian.donchian_channel_hband()
    low_band = donchian.donchian_channel_lband()

    if len(data) >= 20:
        if data['Close'].iloc[-1] > high_band.iloc[-2]:  # Breakout above the channel
            return 5, data['Close'].iloc[-1], None  # Bullish breakout, enter now
        elif data['Close'].iloc[-1] < low_band.iloc[-2]:  # Breakdown below the channel
            return 1, None, data['Close'].iloc[-1]  # Bearish breakdown, exit now
        else:
            return 3, None, None  # No breakout, neutral
    return 3, None, None  # Neutral if not enough data

def analyze_volume(data: pd.DataFrame) -> tuple[int, float, float]:
    """
    Analyzes volume in relation to price movement to detect strength in the trend and determine entry/exit points.

    Args:
        data (pd.DataFrame): DataFrame containing stock data with 'Close' and 'Volume'.

    Returns:
        tuple: (signal_score, expected_entry_price, expected_exit_price)
            signal_score (int): A score from 1 to 5 based on volume and price movement.
            expected_entry_price (float or None): Price where entering the trade is advisable.
            expected_exit_price (float or None): Price where exiting the trade is advisable.
    """
    average_volume = data['Volume'].rolling(window=20).mean()

    if len(data) >= 20:
        if data['Close'].iloc[-1] > data['Close'].iloc[-2] and data['Volume'].iloc[-1] > average_volume.iloc[-1]:
            return 5, data['Close'].iloc[-1], None  # Bullish with high volume, enter now
        elif data['Close'].iloc[-1] < data['Close'].iloc[-2] and data['Volume'].iloc[-1] > average_volume.iloc[-1]:
            return 1, None, data['Close'].iloc[-1]  # Bearish with high volume, exit now
        else:
            return 3, None, None  # Neutral volume
    return 3, None, None  # Neutral