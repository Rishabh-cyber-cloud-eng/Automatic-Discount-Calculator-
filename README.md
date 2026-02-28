# Discount Policy Calculator

## Overview
A Python-based analysis tool designed to automate discount calculations according to company-specific pricing policies and dealer criteria. This application streamlines the evaluation process by cross-referencing daily sales data with master dealer agreements, eliminating the need for manual spreadsheet calculations.

## Features
* **Automated Processing:** Programmatically applies complex discount rules to raw sales data.
* **Data Integration:** Merges and analyzes data from multiple sources (`Sales Ledger` and `Master Dealer` files) to determine accurate payout criteria.
* **Scalable Analysis:** Built with Python to efficiently handle large datasets and output consistent, reliable results.

## Repository Structure
* `app.py`: The core Python script containing the data processing and calculation logic.
* `Master_Dealer_File.xlsx`: The master dataset containing specific dealer profiles, tiers, and criteria.
* `Sales_Ledger_Template.xlsx`: The standardized template for inputting raw sales transaction data.

## Prerequisites
To run this project locally, you will need Python installed on your machine along with standard data analysis libraries. 

Install the required dependencies via your terminal:
```bash
pip install pandas openpyxl
