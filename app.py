# Devops Project
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "devsecops_secret"

# Create database and table
def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()


# Home Route
@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    total = sum(expense[2] for expense in expenses)

    conn.close()

    return render_template(
        'index.html',
        expenses=expenses,
        total=total
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

    cursor.execute('''
        INSERT INTO expenses (title, amount, category, date)
        VALUES (?, ?, ?, ?)
    ''', (title, amount, category, date))

    conn.commit()
    conn.close()

    return redirect('/')

# Admin Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # Simple Admin Credentials
        if username == 'admin' and password == 'admin123':

            session['admin'] = True
            return redirect('/admin')

        else:
            return "Invalid Username or Password"

    return render_template('login.html')


# Admin Dashboard Route
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect('/login')

    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")
    expenses = cursor.fetchall()

    total_expenses = sum(expense[2] for expense in expenses)
    total_transactions = len(expenses)

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
        total_expenses=total_expenses,
        total_transactions=total_transactions,
        app_status=app_status,
        pipeline_status=pipeline_status,
        docker_status=docker_status,
        ec2_status=ec2_status,
        trivy_status=trivy_status
    )
    


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)