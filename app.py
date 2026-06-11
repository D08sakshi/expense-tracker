# Devops Project
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from collections import defaultdict
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
# Changed the secret key
app.secret_key = "SECRET_KEY", "temporary-key"

# Create database and table
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    # Expenses Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
     # Add user_id column if it doesn't already exist
    try:
        cursor.execute('''
            ALTER TABLE expenses
            ADD COLUMN user_id INTEGER
        ''')
    except sqlite3.OperationalError:
        pass

    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Home Route
@app.route('/')
def index():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE user_id=?",
        (session['user_id'],)
    )

    expenses = cursor.fetchall()

    # Total Amount Spent
    total = sum(expense[2] for expense in expenses)

    # -------------------------------
    # Last 7 Days Expense Trend
    # -------------------------------

    daily_data = defaultdict(float)

    for expense in expenses:

        date = expense[4]
        amount = expense[2]

        daily_data[date] += amount

    daily_labels = sorted(daily_data.keys())[-7:]
    daily_values = []

    for date in daily_labels:
        daily_values.append(daily_data[date])

    # -------------------------------
    # Expense Category Distribution
    # -------------------------------

    category_data = defaultdict(float)

    for expense in expenses:

        category = expense[3]
        amount = expense[2]

        category_data[category] += amount

    category_labels = list(category_data.keys())
    category_values = list(category_data.values())

    # -------------------------------
    # Monthly Expenses
    # -------------------------------

    monthly_data = defaultdict(float)

    for expense in expenses:

        date = datetime.strptime(expense[4], "%Y-%m-%d")
        month = date.strftime("%b")

        monthly_data[month] += expense[2]

    month_labels = list(monthly_data.keys())
    month_values = list(monthly_data.values())

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        total=total,

        daily_labels=daily_labels,
        daily_values=daily_values,

        category_labels=category_labels,
        category_values=category_values,

        month_labels=month_labels,
        month_values=month_values
    )
    
# Add Expense Route
@app.route('/add', methods=['POST'])
def add_expense():
    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']
    date = request.form['date']

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    user_id = session['user_id']

    cursor.execute('''
      INSERT INTO expenses
      (user_id, title, amount, category, date)
      VALUES (?, ?, ?, ?, ?)
       ''', (
    user_id,
    title,
    amount,
    category,
    date))
    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        # Admin Login
        if role == 'admin':

            if username == 'admin' and password == 'admin123':

                session['admin'] = True
                conn.close()

                return redirect('/admin')

            conn.close()
            return "Invalid Admin Credentials"

        # User Login
        cursor.execute(
            '''
            SELECT id, username
            FROM users
            WHERE username=? AND password=?
            ''',
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session['user_id'] = user[0]
            session['username'] = user[1]

            return redirect('/')

        return "Invalid Username or Password"

    return render_template('login.html')

@app.route('/profile')
def profile():

    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT username, email, role
        FROM users
        WHERE id=?
    ''', (session['user_id'],))

    user = cursor.fetchone()

    conn.close()

    return {
        "username": user[0],
        "email": user[1],
        "role": user[2]
    }

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('expenses.db')
        cursor = conn.cursor()

        try:

            cursor.execute(
                '''
                INSERT INTO users
                (username, email, password, role)
                VALUES (?, ?, ?, ?)
                ''',
                (username, email, password, 'user')
            )

            conn.commit()

        except:

            return "Username or Email already exists"

        finally:

            conn.close()

        return redirect('/login')

    return render_template('register.html')


# Admin Dashboard Route
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("""
      SELECT
    users.username,
    users.email,
    COUNT(expenses.id) AS total_entries,
    COALESCE(SUM(expenses.amount),0) AS total_amount
    FROM users
    LEFT JOIN expenses
    ON users.id = expenses.user_id
    GROUP BY users.id""")

    users = cursor.fetchall()
    total_users = len(users)
    total_expenses = sum(user[3] for user in users)

    conn.close()

    # Dynamic Application Status
    if os.path.exists("expenses.db"):
        app_status = "Running"
    else:
        app_status = "Stopped"

    # Simulated DevSecOps Status
    pipeline_status = "Active"
    docker_status = "Running"
    ec2_status = "Connected"
    trivy_status = "Scan Completed"

    return render_template(
        'admin.html',
        total_users=total_users,
        total_expenses=total_expenses,
        app_status=app_status,
        pipeline_status=pipeline_status,
        docker_status=docker_status,
        ec2_status=ec2_status,
        trivy_status=trivy_status,
        users=users
    )
    


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)