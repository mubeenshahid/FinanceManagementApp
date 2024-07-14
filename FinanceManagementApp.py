import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from ttkthemes import ThemedTk
from tkcalendar import DateEntry


class FinanceApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Finance Management App")
        self.master.geometry("800x600")

        # Set initial theme
        self.current_theme = 'clam'
        self.style = ttk.Style(self.master)
        self.style.theme_use(self.current_theme)

        # Custom styles
        self.update_styles()

        # Database connection
        self.conn = sqlite3.connect('finance.db')
        self.create_table()

        # GUI components
        self.create_widgets()

    def update_styles(self):
        self.style.configure('TLabel', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12))
        self.style.configure('TEntry', font=('Helvetica', 12))
        self.style.configure('Treeview', font=('Helvetica', 11))
        self.style.configure('Treeview.Heading', font=('Helvetica', 12, 'bold'))

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions
        (id INTEGER PRIMARY KEY,
         date TEXT,
         description TEXT,
         amount REAL,
         category TEXT)
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.master, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Theme switcher
        theme_frame = ttk.Frame(self.main_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        self.theme_combo = ttk.Combobox(theme_frame, values=['clam', 'equilux'], state='readonly', width=10)
        self.theme_combo.set(self.current_theme)
        self.theme_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.theme_combo.bind('<<ComboboxSelected>>', self.change_theme)

        # Input frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Add Transaction", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=10)

        # Input fields
        ttk.Label(input_frame, text="Date:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Description:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.desc_entry = ttk.Entry(input_frame, width=30)
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.amount_entry = ttk.Entry(input_frame, width=30)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Category:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.category_entry = ttk.Entry(input_frame, width=30)
        self.category_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(button_frame, text="Add Transaction", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View All Transactions", command=self.view_transactions).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View by Date Range", command=self.open_date_range_window).pack(side=tk.LEFT, padx=5)

        # Treeview for displaying transactions
        tree_frame = ttk.Frame(self.main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(tree_frame, columns=("Date", "Description", "Amount", "Category"), show="headings")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar for Treeview
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

    def change_theme(self, event):
        self.current_theme = self.theme_combo.get()
        self.style.theme_use(self.current_theme)
        self.update_styles()

    def add_transaction(self):
        date = self.date_entry.get()
        description = self.desc_entry.get()
        amount = self.amount_entry.get()
        category = self.category_entry.get()

        if not all([date, description, amount, category]):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            amount = float(amount)
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO transactions (date, description, amount, category) VALUES (?, ?, ?, ?)",
                       (date, description, amount, category))
        self.conn.commit()

        messagebox.showinfo("Success", "Transaction added successfully")
        self.clear_entries()
        self.view_transactions()

    def view_transactions(self, start_date=None, end_date=None):
        cursor = self.conn.cursor()
        if start_date and end_date:
            cursor.execute("SELECT date, description, amount, category FROM transactions WHERE date BETWEEN ? AND ?", (start_date, end_date))
        else:
            cursor.execute("SELECT date, description, amount, category FROM transactions")
        transactions = cursor.fetchall()

        self.tree.delete(*self.tree.get_children())
        for transaction in transactions:
            self.tree.insert("", "end", values=transaction)

    def clear_entries(self):
        self.date_entry.set_date(datetime.now())
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

    def open_date_range_window(self):
        date_range_window = tk.Toplevel(self.master)
        date_range_window.title("Select Date Range")
        date_range_window.geometry("300x150")

        ttk.Label(date_range_window, text="Start Date:").grid(row=0, column=0, padx=5, pady=5)
        start_date = DateEntry(date_range_window, width=12, background='darkblue', foreground='white', borderwidth=2)
        start_date.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(date_range_window, text="End Date:").grid(row=1, column=0, padx=5, pady=5)
        end_date = DateEntry(date_range_window, width=12, background='darkblue', foreground='white', borderwidth=2)
        end_date.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(date_range_window, text="View Transactions", command=lambda: self.view_transactions_by_date(start_date.get_date(), end_date.get_date())).grid(row=2, column=0, columnspan=2, pady=10)

    def view_transactions_by_date(self, start_date, end_date):
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        self.view_transactions(start_date_str, end_date_str)


if __name__ == "__main__":
    root = ThemedTk(theme="clam")
    app = FinanceApp(root)
    root.mainloop()