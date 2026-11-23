# Trading 212 Portfolio Tracker

A Python-based, read-only portfolio tracker that integrates with the Trading 212 API to retrieve account information, monitor investments, and analyse portfolio activity.

## Features

- **Portfolio Overview** — View current account value and total positions.
- **Stock Information** — Display company names, tickers, and share quantities.
- **Transaction History** — Track deposits, withdrawals, and net contributions.
- **Time Period Selection** — Analyse transactions over 1, 3, 6, or 12 months, or all time.
- **Manual Refresh** — Refresh account balances and holdings without restarting the application.
- **Read-Only Access** — No trading or order execution functionality.

## Technologies

- Python 3
- Trading 212 REST API
- Requests
- Python Dotenv

## Project Structure

```text
trading212-script/
├── .venv/
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── main.py
├── trading212.py
└── agent.py
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd trading212-script
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure API credentials

Generate a read-only API key and secret from your Trading 212 account.

Create a `.env` file:

```env
T212_API_KEY=your_api_key
T212_API_SECRET=your_api_secret
T212_ENV=live
```

Set `T212_ENV=demo` when using a demo account.

**Security:** Never commit your `.env` file or expose your API credentials.

## Usage

Start the application:

```bash
python main.py
```

The application retrieves your account information, current holdings, instrument metadata, and transaction history.

### Portfolio Menu

```text
=== PORTFOLIO MENU ===

1. Change time period
2. Refresh portfolio data
3. Exit
```

### Available Time Periods

| Option | Period |
|---|---|
| 1 | Last 1 month |
| 2 | Last 3 months (default) |
| 3 | Last 6 months |
| 4 | Last 12 months |
| 5 | All time |

Changing the period filters previously retrieved transactions without making additional API requests.

### Example Output

```text
=== TRADING 212 PORTFOLIO ===

Account Currency: GBP
Current Value:    250.00 GBP
Total Positions:  2

=== PERIOD CASH FLOWS ===

Deposited:        200.00 GBP
Withdrawn:        0.00 GBP
Net Deposits:     200.00 GBP

=== HOLDINGS ===

Apple Inc. (AAPL_US_EQ)
  Quantity: 0.5 shares

Microsoft Corporation (MSFT_US_EQ)
  Quantity: 1.2 shares
```

*Example values are illustrative.*

## Data Refresh

Account balances and holdings are retrieved when the application starts and when the user selects the refresh option.

Transaction history and instrument metadata are retrieved at startup. They are not automatically refreshed when updating portfolio balances.

All requests are subject to Trading 212 API rate limits.

## Limitations

- Historical portfolio valuations and period investment returns are not yet implemented.
- Time-period filtering applies to transaction history, not historical holdings.
- Cash-flow calculations depend on the transaction types and currencies returned by Trading 212.
- The application currently uses a command-line interface.
- AI-powered portfolio analysis is planned but not yet implemented.

## Security

The application uses HTTP `GET` requests exclusively and does not implement trading operations.

API credentials are loaded from environment variables using `python-dotenv`.

For additional security, generate Trading 212 credentials with only the permissions required for reading account, portfolio, transaction, and instrument metadata.

## Future Improvements

- AI-powered portfolio summaries and analysis
- Historical performance tracking
- Portfolio allocation visualisations
- Interactive web dashboard
- Automated portfolio reports

## Disclaimer

This project is intended for personal portfolio monitoring and educational purposes. It does not provide financial advice or execute trades.

## License

No license has been specified yet.