import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]

    # Getting Data from Database
    symbols = db.execute(
        "SELECT symbol, SUM(shares) FROM user_transactions WHERE user_id=? GROUP BY symbol HAVING SUM(shares) > 0", user_id)

    # Setting total cash to zero
    total_cash = 0

    # Selecting the logged in user's cash
    cash = db.execute("SELECT cash FROM users WHERE id=?", user_id)[0]["cash"]

    # Upadating total cash
    total_cash = total_cash + cash

    # Creating a list
    database = []

    # Looping over database and storing it in the list we just made
    for row in symbols:
        stock = lookup(row["symbol"])
        stock_price = stock["price"]
        bought_shares = row["SUM(shares)"]
        symbol_share_value = (stock_price * bought_shares)
        # Writing to the list
        database.append({"symbol": stock["symbol"], "name": stock["name"], "shares": row["SUM(shares)"], "price": usd(
                        stock["price"]), "total": usd(symbol_share_value)})
        # Updating the total cash
        total_cash = total_cash + symbol_share_value

    # Returning values we extracted to index page
    return render_template("index.html", database=database, cash=usd(cash), total_cash=usd(total_cash))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # Get User Id
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Checking for Form manipultion and passing of non-number figure
        if request.form.get("shares").isdigit() == False:
            return apology("must provide valido shares", 400)

       # Converting str to int and storing it in a variable
        shares = int(request.form.get("shares"))

       # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure symbol was submitted
        if not shares:
            return apology("must provide shares", 403)

        # Ensure share is within valid range
        if shares < 0:
            return apology("must provide valid shares", 400)

        # Seacrching for the submitted symbol
        stock = lookup(request.form.get("symbol"))

        # Ensure symbol is a valid one
        if stock == None:
            return apology("must provide valid symbol", 400)

        # Getting user's available cash
        total_balance = db.execute(
            "SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        # Looking up a stock’s current price
        stock_price = stock["price"]

        # Looking up a stock’s symbol
        stock_symbol = stock["symbol"]

        # check if user can afford the purchase
        remaining_balance = total_balance - (stock_price * shares)

        # Time
        date = datetime.datetime.now()

        if remaining_balance >= 0:
            # Update remaining cash
            db.execute("UPDATE users SET cash = ? WHERE id = ?",
                       remaining_balance, user_id)

            # Upadate the table of transactions
            db.execute("INSERT INTO user_transactions (user_id, symbol, shares, price, timestamp) VALUES (?, ?, ?, ?, ?)",
                       user_id, stock_symbol, shares, stock_price, date)

            # Alert Successful Purchase
            flash("Successful Purchase!")

            # Redirect to index
            return redirect("/")

        else:
            return apology("Purchase Failure(Reason: Insufficient Amount of Money!)")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        rows = db.execute(
            "SELECT symbol FROM user_transactions WHERE user_id=? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        return render_template("buy.html", symbols=[row["symbol"] for row in rows])


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # Get user id
    user_id = session["user_id"]

    # Extracting data from database
    rows = db.execute(
        "SELECT * FROM user_transactions WHERE user_id =?", user_id)

    # Sending data to history page
    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username").upper())

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

       # Ensure symbol was submitted
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Seacrching for the submitted symbol
        stock = lookup(request.form.get("symbol"))

        # Ensure symbol is a valid one
        if stock == None:
            return apology("must provide valid symbol", 400)
        else:
            return render_template("quoted.html", name=stock["name"], price=usd(stock["price"]), symbol=stock["symbol"])

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Ensure the password do Match
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("Passwords Do not Match", 400)

        usrname = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username").upper())
        # Ensure the username is not already taken
        if len(usrname) != 0:
            return apology("username already taken", 400)

        # Query database for username
        rows = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username").upper(), generate_password_hash(request.form.get("password")))

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # Get User Id
    user_id = session["user_id"]

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol = request.form.get("symbol")
        # Ensure symbol was submitted
        if not symbol:
            return apology("must provide symbol", 403)

        # Converting str to int and storing it in a variable
        shares = int(request.form.get("shares"))

        # Ensure symbol was submitted
        if not shares:
            return apology("must provide shares", 403)

        # Ensure share is within valid range
        if shares < 0:
            return apology("must provide valid shares", 403)

        # Seacrching for the submitted symbol
        stock = lookup(symbol)

        # Ensure symbol is a valid one
        if stock == None:
            return apology("must provide valid symbol", 403)

        # Getting user's available cash
        total_balance = db.execute(
            "SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

        # Looking up a stock’s current price
        stock_price = stock["price"]

        # Looking up a stock’s symbol
        stock_symbol = stock["symbol"]

        # check if user can afford the purchase
        remaining_balance = total_balance + (stock_price * shares)

        # Getting user current shares
        user_shares = db.execute(
            "SELECT shares FROM user_transactions WHERE user_id=? AND symbol =? GROUP BY symbol", user_id, symbol)[0]["shares"]

        # In case user is having money crisis
        if shares > user_shares:
            return apology("Insufficient Shares! Retry.")

        # Time
        date = datetime.datetime.now()

        # Update remaining cash
        db.execute("UPDATE users SET cash = ? WHERE id = ?",
                   remaining_balance, user_id)

        # Upadate the table of transactions
        db.execute("INSERT INTO user_transactions (user_id, symbol, shares, price, timestamp) VALUES (?, ?, ?, ?, ?)",
                   user_id, stock_symbol, (-1)*shares, stock_price, date)

        # Alert Successful Sell
        flash("Share Successfully Sold!")

        return redirect("/")

    else:
        rows = db.execute(
            "SELECT symbol FROM user_transactions WHERE user_id=? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        return render_template("sell.html", symbols=[row["symbol"] for row in rows])