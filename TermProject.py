"""
StockSmart Inventory Manager
Term Project

A desktop inventory management application for a small business.
Uses Tkinter for the GUI and SQLite for persistent storage.

Requirements:
- Python 3.10+
- No third-party libraries required
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).with_name("inventory.db")
LOW_STOCK_DEFAULT = 5


def initialize_database():
    """Create the database tables if they do not already exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL CHECK(price >= 0),
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                reorder_level INTEGER NOT NULL DEFAULT 5 CHECK(reorder_level >= 0)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                transaction_date TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(product_id)
            )
            """
        )
        conn.commit()


def add_product(sku, name, category, price, quantity, reorder_level=LOW_STOCK_DEFAULT):
    """Add a new product to inventory."""
    if not sku.strip() or not name.strip() or not category.strip():
        raise ValueError("SKU, product name, and category are required.")

    price = float(price)
    quantity = int(quantity)
    reorder_level = int(reorder_level)

    if price < 0 or quantity < 0 or reorder_level < 0:
        raise ValueError("Price, quantity, and reorder level cannot be negative.")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO products (sku, name, category, price, quantity, reorder_level)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (sku.strip(), name.strip(), category.strip(), price, quantity, reorder_level),
        )
        product_id = cursor.lastrowid
        if quantity > 0:
            cursor.execute(
                """
                INSERT INTO transactions
                (product_id, transaction_type, quantity, transaction_date)
                VALUES (?, 'INITIAL STOCK', ?, ?)
                """,
                (product_id, quantity, datetime.now().isoformat(timespec="seconds")),
            )
        conn.commit()


def record_sale(product_id, quantity_sold):
    """Record a sale and reduce stock while preventing negative inventory."""
    quantity_sold = int(quantity_sold)
    if quantity_sold <= 0:
        raise ValueError("Sale quantity must be greater than zero.")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT quantity FROM products WHERE product_id = ?",
            (product_id,),
        )
        row = cursor.fetchone()

        if row is None:
            raise ValueError("Product was not found.")

        current_quantity = row[0]
        if quantity_sold > current_quantity:
            raise ValueError(
                f"Not enough stock. Only {current_quantity} item(s) are available."
            )

        cursor.execute(
            "UPDATE products SET quantity = quantity - ? WHERE product_id = ?",
            (quantity_sold, product_id),
        )
        cursor.execute(
            """
            INSERT INTO transactions
            (product_id, transaction_type, quantity, transaction_date)
            VALUES (?, 'SALE', ?, ?)
            """,
            (product_id, quantity_sold, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()


def restock_product(product_id, quantity_added):
    """Increase stock and record a restock transaction."""
    quantity_added = int(quantity_added)
    if quantity_added <= 0:
        raise ValueError("Restock quantity must be greater than zero.")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT product_id FROM products WHERE product_id = ?",
            (product_id,),
        )
        if cursor.fetchone() is None:
            raise ValueError("Product was not found.")

        cursor.execute(
            "UPDATE products SET quantity = quantity + ? WHERE product_id = ?",
            (quantity_added, product_id),
        )
        cursor.execute(
            """
            INSERT INTO transactions
            (product_id, transaction_type, quantity, transaction_date)
            VALUES (?, 'RESTOCK', ?, ?)
            """,
            (product_id, quantity_added, datetime.now().isoformat(timespec="seconds")),
        )
        conn.commit()


def get_inventory(search_text=""):
    """Return inventory rows, optionally filtered by SKU, name, or category."""
    like_value = f"%{search_text.strip()}%"
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product_id, sku, name, category, price, quantity, reorder_level
            FROM products
            WHERE sku LIKE ? OR name LIKE ? OR category LIKE ?
            ORDER BY name
            """,
            (like_value, like_value, like_value),
        )
        return cursor.fetchall()


def get_low_stock_items():
    """Return products at or below their reorder level."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT product_id, sku, name, category, price, quantity, reorder_level
            FROM products
            WHERE quantity <= reorder_level
            ORDER BY quantity ASC, name ASC
            """
        )
        return cursor.fetchall()


def get_summary():
    """Return dashboard totals for products, units, inventory value, and sales."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                COUNT(*),
                COALESCE(SUM(quantity), 0),
                COALESCE(SUM(price * quantity), 0)
            FROM products
            """
        )
        product_count, unit_count, inventory_value = cursor.fetchone()

        cursor.execute(
            """
            SELECT COALESCE(SUM(t.quantity), 0)
            FROM transactions t
            WHERE t.transaction_type = 'SALE'
            """
        )
        units_sold = cursor.fetchone()[0]

        return product_count, unit_count, inventory_value, units_sold


def get_transaction_history():
    """Return transaction history joined with product information."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                t.transaction_id,
                p.sku,
                p.name,
                t.transaction_type,
                t.quantity,
                t.transaction_date
            FROM transactions t
            JOIN products p ON p.product_id = t.product_id
            ORDER BY t.transaction_id DESC
            LIMIT 200
            """
        )
        return cursor.fetchall()


def export_low_stock_report(file_path):
    """Export a plain-text low-stock report."""
    rows = get_low_stock_items()
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("StockSmart Low Stock Report\n")
        file.write("=" * 70 + "\n")
        file.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")

        if not rows:
            file.write("No products currently need restocking.\n")
            return

        for _, sku, name, category, price, quantity, reorder_level in rows:
            file.write(
                f"{sku} | {name} | {category} | "
                f"In Stock: {quantity} | Reorder Level: {reorder_level} | "
                f"Price: ${price:.2f}\n"
            )


class InventoryApp:
    """Tkinter graphical interface for StockSmart."""

    def __init__(self, root):
        self.root = root
        self.root.title("StockSmart Inventory Manager")
        self.root.geometry("1050x700")
        self.root.minsize(900, 600)

        self.create_widgets()
        self.refresh_all()

    def create_widgets(self):
        title = ttk.Label(
            self.root,
            text="StockSmart Inventory Manager",
            font=("Arial", 20, "bold"),
        )
        title.pack(pady=(12, 4))

        subtitle = ttk.Label(
            self.root,
            text="Track stock, sales, restocking, and inventory history",
        )
        subtitle.pack(pady=(0, 10))

        summary_frame = ttk.Frame(self.root)
        summary_frame.pack(fill="x", padx=15, pady=5)

        self.product_count_var = tk.StringVar()
        self.unit_count_var = tk.StringVar()
        self.value_var = tk.StringVar()
        self.sold_var = tk.StringVar()

        for col, (label, variable) in enumerate([
            ("Products", self.product_count_var),
            ("Units in Stock", self.unit_count_var),
            ("Inventory Value", self.value_var),
            ("Units Sold", self.sold_var),
        ]):
            card = ttk.LabelFrame(summary_frame, text=label)
            card.grid(row=0, column=col, padx=5, sticky="nsew")
            ttk.Label(card, textvariable=variable, font=("Arial", 14, "bold")).pack(
                padx=18, pady=10
            )
            summary_frame.columnconfigure(col, weight=1)

        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=15, pady=8)

        ttk.Label(controls, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(controls, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<KeyRelease>", lambda event: self.refresh_inventory())

        ttk.Button(controls, text="Add Product", command=self.open_add_product).pack(
            side="left", padx=4
        )
        ttk.Button(controls, text="Record Sale", command=self.open_record_sale).pack(
            side="left", padx=4
        )
        ttk.Button(controls, text="Restock", command=self.open_restock).pack(
            side="left", padx=4
        )
        ttk.Button(controls, text="Low Stock", command=self.show_low_stock).pack(
            side="left", padx=4
        )
        ttk.Button(controls, text="History", command=self.show_history).pack(
            side="left", padx=4
        )

        columns = ("id", "sku", "name", "category", "price", "quantity", "reorder")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=20)

        headings = {
            "id": "ID",
            "sku": "SKU",
            "name": "Product",
            "category": "Category",
            "price": "Price",
            "quantity": "In Stock",
            "reorder": "Reorder Level",
        }
        widths = {
            "id": 55,
            "sku": 110,
            "name": 230,
            "category": 150,
            "price": 90,
            "quantity": 90,
            "reorder": 110,
        }

        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="center")

        self.tree.column("name", anchor="w")
        self.tree.column("category", anchor="w")

        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=8)

    def refresh_all(self):
        self.refresh_inventory()
        product_count, unit_count, inventory_value, units_sold = get_summary()
        self.product_count_var.set(str(product_count))
        self.unit_count_var.set(str(unit_count))
        self.value_var.set(f"${inventory_value:,.2f}")
        self.sold_var.set(str(units_sold))

    def refresh_inventory(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in get_inventory(self.search_var.get()):
            display_row = (
                row[0],
                row[1],
                row[2],
                row[3],
                f"${row[4]:.2f}",
                row[5],
                row[6],
            )
            self.tree.insert("", "end", values=display_row)

    def selected_product_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Product", "Please select a product first.")
            return None
        values = self.tree.item(selected[0], "values")
        return int(values[0])

    def open_add_product(self):
        window = tk.Toplevel(self.root)
        window.title("Add Product")
        window.resizable(False, False)

        fields = [
            ("SKU", ""),
            ("Product Name", ""),
            ("Category", ""),
            ("Price", "0.00"),
            ("Starting Quantity", "0"),
            ("Reorder Level", str(LOW_STOCK_DEFAULT)),
        ]
        entries = {}

        for row, (label, default) in enumerate(fields):
            ttk.Label(window, text=label).grid(row=row, column=0, padx=10, pady=6, sticky="e")
            entry = ttk.Entry(window, width=30)
            entry.insert(0, default)
            entry.grid(row=row, column=1, padx=10, pady=6)
            entries[label] = entry

        def save():
            try:
                add_product(
                    entries["SKU"].get(),
                    entries["Product Name"].get(),
                    entries["Category"].get(),
                    entries["Price"].get(),
                    entries["Starting Quantity"].get(),
                    entries["Reorder Level"].get(),
                )
                messagebox.showinfo("Success", "Product added successfully.")
                window.destroy()
                self.refresh_all()
            except sqlite3.IntegrityError:
                messagebox.showerror("Duplicate SKU", "That SKU already exists.")
            except (ValueError, TypeError) as exc:
                messagebox.showerror("Invalid Data", str(exc))

        ttk.Button(window, text="Save Product", command=save).grid(
            row=len(fields), column=0, columnspan=2, pady=12
        )

    def open_record_sale(self):
        product_id = self.selected_product_id()
        if product_id is None:
            return

        quantity = self.ask_quantity("Record Sale", "Quantity sold:")
        if quantity is None:
            return

        try:
            record_sale(product_id, quantity)
            messagebox.showinfo("Sale Recorded", "Inventory has been updated.")
            self.refresh_all()
        except ValueError as exc:
            messagebox.showerror("Cannot Record Sale", str(exc))

    def open_restock(self):
        product_id = self.selected_product_id()
        if product_id is None:
            return

        quantity = self.ask_quantity("Restock Product", "Quantity received:")
        if quantity is None:
            return

        try:
            restock_product(product_id, quantity)
            messagebox.showinfo("Restocked", "Inventory has been updated.")
            self.refresh_all()
        except ValueError as exc:
            messagebox.showerror("Cannot Restock", str(exc))

    def ask_quantity(self, title, prompt):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.resizable(False, False)
        window.grab_set()

        ttk.Label(window, text=prompt).pack(padx=20, pady=(15, 5))
        entry = ttk.Entry(window, width=15)
        entry.pack(padx=20, pady=5)
        entry.focus()

        result = {"value": None}

        def submit():
            try:
                value = int(entry.get())
                if value <= 0:
                    raise ValueError
                result["value"] = value
                window.destroy()
            except ValueError:
                messagebox.showerror("Invalid Quantity", "Enter a whole number greater than 0.")

        ttk.Button(window, text="Submit", command=submit).pack(pady=(5, 15))
        window.wait_window()
        return result["value"]

    def show_low_stock(self):
        rows = get_low_stock_items()
        window = tk.Toplevel(self.root)
        window.title("Low Stock Report")
        window.geometry("780x450")

        text = tk.Text(window, wrap="none")
        text.pack(fill="both", expand=True, padx=10, pady=10)

        text.insert("end", "LOW STOCK / RESTOCK REPORT\n")
        text.insert("end", "=" * 70 + "\n\n")

        if not rows:
            text.insert("end", "No products currently need restocking.")
        else:
            for _, sku, name, category, price, quantity, reorder_level in rows:
                text.insert(
                    "end",
                    f"{sku} | {name} | {category} | "
                    f"Stock: {quantity} | Reorder at: {reorder_level} | ${price:.2f}\n",
                )

        text.configure(state="disabled")

        def export():
            report_path = Path(__file__).with_name("low_stock_report.txt")
            export_low_stock_report(report_path)
            messagebox.showinfo("Report Exported", f"Saved to:\n{report_path}")

        ttk.Button(window, text="Export Report", command=export).pack(pady=(0, 10))

    def show_history(self):
        rows = get_transaction_history()
        window = tk.Toplevel(self.root)
        window.title("Transaction History")
        window.geometry("900x500")

        columns = ("id", "sku", "product", "type", "quantity", "date")
        tree = ttk.Treeview(window, columns=columns, show="headings")

        for col, title in zip(
            columns,
            ("ID", "SKU", "Product", "Type", "Quantity", "Date/Time"),
        ):
            tree.heading(col, text=title)

        tree.column("id", width=60)
        tree.column("sku", width=110)
        tree.column("product", width=220)
        tree.column("type", width=120)
        tree.column("quantity", width=90)
        tree.column("date", width=180)

        for row in rows:
            tree.insert("", "end", values=row)

        tree.pack(fill="both", expand=True, padx=10, pady=10)


def main():
    """Start the StockSmart application."""
    initialize_database()
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
