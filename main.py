# Function to fetch all stock names listed on NSE

import pandas as pd
import requests
import os


def fetch_nse_stock_names(csv_path="EQUITY_L.csv"):
	"""
	Downloads the NSE equity list CSV and loads all stock names from it.
	Returns a list of company names.
	"""
	nse_url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
	try:
		# Download the CSV file
		# response = requests.get(nse_url)
		# response.raise_for_status()
		# with open(csv_path, "wb") as f:
		# 	f.write(response.content)
		# Load the CSV locally
		df = pd.read_csv(csv_path)
		stock_names = df['NAME OF COMPANY'].tolist()
		return stock_names
	except Exception as e:
		print(f"Error fetching NSE stock names: {e}")
		return []

if __name__ == "__main__":
    stock_names = fetch_nse_stock_names()
    print(f"Fetched {len(stock_names)} stock names from NSE.")
    # Optionally, print the first 10 stock names
    print(stock_names[:10])

