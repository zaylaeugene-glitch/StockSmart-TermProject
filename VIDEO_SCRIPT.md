# StockSmart Project Presentation Script

## Opening / Introduction (about 30–45 seconds)

Hello, my name is Zayla. My project is called **StockSmart Inventory Manager**.

My GitHub username is: <YOUR GITHUB USERNAME>.

I am recording this video from Charlotte, North Carolina, United States.

The date of this recording is: <DATE>.

StockSmart is a Python desktop application designed to help a small business track products, sales, restocking activity, and low inventory.

## Project Purpose (about 45 seconds)

The purpose of the application is to replace manual inventory tracking with a simple graphical system. Employees can add products, record sales, restock products, search inventory, review low-stock items, and view transaction history.

I built the interface with Tkinter and used SQLite to store inventory permanently.

## Demonstration (about 2–3 minutes)

1. Start `TermProject.py`.
2. Show the dashboard totals.
3. Click **Add Product** and add a sample item.
4. Show that the new product appears in the inventory table.
5. Select the product and click **Record Sale**.
6. Show that the quantity and units-sold total update.
7. Select the product and click **Restock**.
8. Show the **Low Stock** report.
9. Show the **Transaction History**.
10. Demonstrate the Search box.

Explain that the program validates user input and prevents a user from selling more units than are currently available.

## Code / Design Explanation (about 1 minute)

The program includes a required `main()` function and several additional top-level functions.

Some examples are:
- `initialize_database()` to create the database.
- `add_product()` to add inventory.
- `record_sale()` to reduce stock after a sale.
- `restock_product()` to increase inventory.
- `get_low_stock_items()` to identify products that need to be reordered.

I also created an `InventoryApp` class to organize the graphical user interface.

## Closing (about 20–30 seconds)

This project helped me combine several Python concepts into one larger application, including functions, object-oriented programming, databases, conditionals, loops, error handling, and a graphical user interface.

In the future, StockSmart could be expanded with employee accounts, barcode scanning, supplier management, cloud storage, and support for multiple business locations.

Thank you for watching my StockSmart Inventory Manager demonstration.
