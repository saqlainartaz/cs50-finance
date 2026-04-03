# C$50 Finance

A web-based stock portfolio management application built with Flask. Users can register an account, look up real-time stock quotes, buy and sell shares, and track their portfolio performance — all in one place.

This project was developed as part of the [CS50 Computer Science](https://cs50.harvard.edu/) course from Harvard University.

## Features

- **User Authentication** — Register and log in with secure password hashing via `werkzeug.security`
- **Stock Quotes** — Look up real-time stock prices via the IEX Cloud API
- **Buy Shares** — Purchase stock shares with form validation and balance checking
- **Sell Shares** — Sell owned shares with insufficient-share protection
- **Portfolio Dashboard** — View all holdings, current prices, cash balance, and total portfolio value
- **Transaction History** — Review a complete log of all past buys and sells

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (via `cs50.SQL`) |
| Frontend | Jinja2 templates, Bootstrap 5 |
| External API | IEX Cloud (stock quotes) |

## Repository Structure

```
├── app.py                  # Flask application, all routes & database logic
├── helpers.py              # Utilities: API lookup, auth decorator, formatting
├── requirements.txt        # Python dependencies
├── templates/              # Jinja2 HTML templates
│   ├── layout.html         # Base template with nav & flash messages
│   ├── index.html          # Portfolio dashboard
│   ├── login.html
│   ├── register.html
│   ├── buy.html
│   ├── sell.html
│   ├── quote.html          # Quote input form
│   ├── quoted.html         # Quote result display
│   ├── history.html        # Transaction log
│   └── apology.html        # Error page renderer
└── static/
    └── styles.css          # Custom stylesheet
```

## Quick Start

### Prerequisites

- Python 3.8+
- An [IEX Cloud API key](https://iexcloud.io/) (free tier available)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saqlainartaz/cs50-finance.git
   cd cs50-finance
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your API key:
   ```bash
   export API_KEY="sk_your_iex_api_key_here"   # On Windows: set API_KEY=...
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Visit `http://localhost:5000` in your browser.

### First Use

1. Click **Register** to create an account
2. You start with $10,000 in virtual cash (set in the database schema)
3. Use **Quote** to look up stock symbols
4. Buy shares through the **Buy Shares** page
5. Track your portfolio on the home page

## Database Schema

The application uses SQLite with two tables:

- **users** — `id` (PK), `username`, `hash` (password), `cash`
- **user_transactions** — records of buy/sell events with `user_id`, `symbol`, `shares`, `price`, `timestamp`

Portfolio holdings are computed dynamically by aggregating transaction records.

## Screenshots

### Portfolio Dashboard
Displays current holdings, per-share pricing, cash balance, and total portfolio value.

### Transaction History
A complete audit trail of every buy and sell transaction.

## License

This project is for educational purposes as part of the CS50 curriculum.
