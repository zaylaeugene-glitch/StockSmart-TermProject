# StockSmart Inventory Manager

#### Video Demo: https://youtu.be/oReGsRulFLs
#### Student: Zayla

#### GitHub Username: zaylaeugene-glitch

#### Location: Charlotte, North Carolina, United States

## Description

StockSmart Inventory Manager is a Python desktop application designed for a small business that needs a simple and dependable way to track inventory. The goal of this project is to replace manual inventory tracking methods, such as handwritten notes or basic spreadsheets, with an application that stores product information, records sales, tracks restocking activity, identifies low-stock products, and provides a history of inventory transactions.

The program is built in Python and uses Tkinter for the graphical user interface and SQLite for permanent data storage. Both technologies are included with standard Python installations, so the program does not require a complicated setup or additional paid software. When the program starts, it automatically creates its database if one does not already exist. This makes the application easy to demonstrate and easy for a small organization to begin using.

The main screen provides an inventory dashboard showing the number of products, total units currently in stock, total estimated inventory value, and the number of units sold. Employees can search inventory by SKU, product name, or category. The application also allows users to add products, record sales, restock items, review low-stock products, view transaction history, and export a low-stock report.

A major design goal was protecting inventory accuracy. The application validates data before making changes. For example, employees cannot record a negative quantity, and the system will not allow a sale that is larger than the available inventory. Product SKUs must also be unique. These checks reduce common data-entry mistakes and make the system more dependable.

## Project Files

### `TermProject.py`

This is the main Python program. It includes the required `main()` function and several additional top-level functions, including `initialize_database()`, `add_product()`, `record_sale()`, `restock_product()`, `get_inventory()`, `get_low_stock_items()`, `get_summary()`, `get_transaction_history()`, and `export_low_stock_report()`.

The program also includes an `InventoryApp` class that manages the graphical interface. I separated the database and inventory functions from the GUI class so that the business logic is not tightly tied to the screen layout. This makes future maintenance easier and allows the application to be expanded without rewriting the entire program.

### `requirements.txt`

This file documents the external Python libraries required by the application. StockSmart intentionally uses only Python standard-library modules, including Tkinter, SQLite, datetime, and pathlib. Because no third-party libraries are needed, the requirements file explains that the project can run with a normal Python installation.

### `inventory.db`

This SQLite database file is created automatically the first time the application runs. It stores two tables: `products` and `transactions`. The products table stores current product information such as SKU, name, category, price, quantity, and reorder level. The transactions table creates an audit history of initial inventory, sales, and restocking activity.

### `low_stock_report.txt`

This file is optional and is generated when the user selects the Export Report button from the Low Stock window. It provides a simple text report of items that have reached or fallen below their reorder level.

## Design Decisions

I selected Tkinter because this project is intended for a small business that needs a straightforward desktop application. A web-based system would require additional hosting, security configuration, and infrastructure that is not necessary for the current project scope. Tkinter provides buttons, forms, tables, and dialog boxes while keeping the program relatively lightweight.

SQLite was selected because the application needs permanent structured storage but does not yet require a full database server. SQLite is appropriate for a small single-location application and allows the project to demonstrate database concepts without creating unnecessary complexity. If the business expands to multiple locations or needs many simultaneous users, the database layer could later be migrated to PostgreSQL or another enterprise database.

I also included a transaction-history table rather than simply changing product quantities. This was an important decision because knowing the current stock level is not enough for good inventory management. Managers may need to understand why stock changed, when a sale occurred, or when products were restocked. Maintaining this history provides a simple audit trail.

The application is designed with future scalability in mind. Features such as user authentication, role-based permissions, barcode scanning, supplier management, purchase orders, cloud backups, and multiple business locations could be added later. Because the project separates inventory functions from the graphical interface, future development can build on the existing structure rather than starting over.

Overall, StockSmart demonstrates Python fundamentals, functions, object-oriented programming, graphical user interfaces, database operations, validation, conditional logic, loops, error handling, file output, and modular design. The project solves a realistic business problem while leaving room for continued development.
