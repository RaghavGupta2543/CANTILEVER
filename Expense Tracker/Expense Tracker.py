import sys
import sqlite3
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit, QPushButton, QTableWidget, QTableWidgetItem, QWidget, QDateEdit, QComboBox
from PyQt5.QtCore import QDate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import datetime

# Database setup
def create_connection():
    conn = sqlite3.connect('expenses.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        date TEXT,
        category TEXT,
        amount REAL,
        description TEXT
    )
    ''')
    conn.commit()
    conn.close()

def add_expense(date, category, amount, description):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO expenses (date, category, amount, description)
    VALUES (?, ?, ?, ?)
    ''', (date, category, amount, description))
    conn.commit()
    conn.close()

def get_expenses():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses')
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expenses_by_date(date):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE date = ?', (date,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expenses_by_category(category):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM expenses WHERE category = ?', (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_expenses_by_all_categories():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT category, SUM(amount) FROM expenses GROUP BY category')
    rows = cursor.fetchall()
    conn.close()
    return rows

create_table()

# Matplotlib canvas class to create a figure and add it to the PyQt5 window
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

# GUI application
class ExpenseTrackerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Expense Tracker')
        self.setGeometry(100, 100, 800, 600)

        # Layouts
        self.main_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.button_layout = QHBoxLayout()
        self.table_layout = QVBoxLayout()
        self.search_layout = QHBoxLayout()
        self.category_search_layout = QHBoxLayout()

        # Form inputs
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Food", "Bills", "Travel", "Home", "Office", "Car", "Bike"])
        
        self.amount_edit = QLineEdit()
        self.description_edit = QLineEdit()

        self.form_layout.addRow('Date:', self.date_edit)
        self.form_layout.addRow('Category:', self.category_combo)
        self.form_layout.addRow('Amount:', self.amount_edit)
        self.form_layout.addRow('Description:', self.description_edit)

        # Buttons
        self.add_expense_button = QPushButton('Add Expense')
        self.visualize_button = QPushButton('Visualize Expenses')
        self.pie_chart_button = QPushButton('Show Pie Chart')

        self.button_layout.addWidget(self.add_expense_button)
        self.button_layout.addWidget(self.visualize_button)
        self.button_layout.addWidget(self.pie_chart_button)

        # Search input and buttons
        self.search_date_edit = QDateEdit()
        self.search_date_edit.setCalendarPopup(True)
        self.search_date_edit.setDate(QDate.currentDate())
        self.search_date_button = QPushButton('Search by Date')

        self.search_category_combo = QComboBox()
        self.search_category_combo.addItems(["All"] + ["Food", "Bills", "Travel", "Home", "Office", "Car", "Bike"])
        self.search_category_button = QPushButton('Search by Category')

        self.search_layout.addWidget(self.search_date_edit)
        self.search_layout.addWidget(self.search_date_button)

        self.category_search_layout.addWidget(self.search_category_combo)
        self.category_search_layout.addWidget(self.search_category_button)

        # Expense table
        self.expense_table = QTableWidget()
        self.expense_table.setColumnCount(5)
        self.expense_table.setHorizontalHeaderLabels(['ID', 'Date', 'Category', 'Amount', 'Description'])

        self.table_layout.addWidget(self.expense_table)

        # Visualization widget
        self.visualization_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.table_layout.addWidget(self.visualization_canvas)

        # Main layout
        self.main_layout.addLayout(self.form_layout)
        self.main_layout.addLayout(self.button_layout)
        self.main_layout.addLayout(self.search_layout)
        self.main_layout.addLayout(self.category_search_layout)
        self.main_layout.addLayout(self.table_layout)

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Connect buttons to functions
        self.add_expense_button.clicked.connect(self.add_expense)
        self.visualize_button.clicked.connect(self.visualize_expenses)
        self.pie_chart_button.clicked.connect(self.show_pie_chart)
        self.search_date_button.clicked.connect(self.search_expenses_by_date)
        self.search_category_button.clicked.connect(self.search_expenses_by_category)

        # Load expenses
        self.load_expenses()

    def add_expense(self):
        date = self.date_edit.date().toString('yyyy-MM-dd')
        category = self.category_combo.currentText()
        amount = float(self.amount_edit.text())
        description = self.description_edit.text()
        add_expense(date, category, amount, description)
        self.load_expenses()

    def load_expenses(self):
        expenses = get_expenses()
        self.expense_table.setRowCount(len(expenses))
        for row, expense in enumerate(expenses):
            for col, data in enumerate(expense):
                self.expense_table.setItem(row, col, QTableWidgetItem(str(data)))

    def search_expenses_by_date(self):
        date = self.search_date_edit.date().toString('yyyy-MM-dd')
        expenses = get_expenses_by_date(date)
        self.expense_table.setRowCount(len(expenses))
        for row, expense in enumerate(expenses):
            for col, data in enumerate(expense):
                self.expense_table.setItem(row, col, QTableWidgetItem(str(data)))

    def search_expenses_by_category(self):
        category = self.search_category_combo.currentText()
        if category == "All":
            expenses = get_expenses()
        else:
            expenses = get_expenses_by_category(category)
        self.expense_table.setRowCount(len(expenses))
        for row, expense in enumerate(expenses):
            for col, data in enumerate(expense):
                self.expense_table.setItem(row, col, QTableWidgetItem(str(data)))

    def visualize_expenses(self):
        expenses = get_expenses()
        dates = [datetime.datetime.strptime(expense[1], '%Y-%m-%d') for expense in expenses]
        amounts = [expense[3] for expense in expenses]

        self.visualization_canvas.axes.clear()
        self.visualization_canvas.axes.plot(dates, amounts, marker='o')
        self.visualization_canvas.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        self.visualization_canvas.axes.xaxis.set_major_locator(mdates.DayLocator())
        self.visualization_canvas.axes.set_xlabel('Date')
        self.visualization_canvas.axes.set_ylabel('Amount')
        self.visualization_canvas.axes.set_title('Expenses Over Time')
        self.visualization_canvas.draw()

    def show_pie_chart(self):
        data = get_expenses_by_all_categories()
        if(data == []):
            return
        categories, amounts = zip(*data)

        self.visualization_canvas.axes.clear()
        self.visualization_canvas.axes.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        self.visualization_canvas.axes.set_title('Expense Distribution by Category')
        self.visualization_canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExpenseTrackerApp()
    window.show()
    sys.exit(app.exec_())
