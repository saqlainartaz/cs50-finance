# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask-based stock portfolio management application from CS50. Users can register, login, buy/sell stocks, view their portfolio, check stock quotes, and see transaction history.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app (requires API_KEY env var)
export API_KEY="your_iex_cloud_api_key"
python app.py

# Run on Windows (CMD)
set API_KEY=your_iex_cloud_api_key
python app.py
```

## Dependencies

See `requirements.txt`: cs50, Flask, Flask-Session, requests.

Requires an **API_KEY** environment variable for the IEX Cloud stock quote API (`https://cloud.iexapis.com/`).

## Architecture

### Structure
- **`app.py`** — Flask application with all routes and SQLite database logic
- **`helpers.py`** — Utility functions: `lookup()` (stock API), `login_required` decorator, `usd()` formatting, `apology()` error rendering
- **`templates/`** — Jinja2 HTML templates (layout, index, login, register, buy, sell, quote, quoted, history, apology)
- **`static/styles.css`** — Stylesheet
- **`finance.db`** — SQLite database

### Database Schema (inferred from usage)
- **`users`** — `id`, `username`, `hash`, `cash`
- **`user_transactions`** — records of buys/sells with `user_id`, `symbol`, `shares`, `price`, `timestamp`

### Routes
| Route | Auth | Description |
|---|---|---|
| `GET /` | Required | Portfolio index showing holdings + total value |
| `GET/POST /buy` | Required | Buy shares (form + action) |
| `GET/POST /sell` | Required | Sell shares (form + action) |
| `GET/POST /quote` | Required | Look up stock quote |
| `GET /history` | Required | Transaction history |
| `GET/POST /login` | Public | Login |
| `GET/POST /register` | Public | User registration |
| `GET /logout` | Public | Logout |

### Key Conventions
- Usernames are stored in **UPPERCASE** in the database
- Sell transactions record **negative shares** in `user_transactions`
- Portfolio holdings are computed by `SUM(shares)` grouped by symbol where sum > 0
- Flash messages are used for buy/sell confirmations
