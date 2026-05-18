# Smart Electronics Sales System

A complete Point of Sale (POS) system for electronics shops, built with Django. Includes inventory tracking, sales management, customer records, and profit analytics.

## Tech Stack

- Python 3.13
- Django 6.0
- MySQL
- Bootstrap 5
- JavaScript
- Chart.js

## Features

### Sales & Billing
- Fast product search (name, SKU, or barcode)
- Add/remove items from cart
- Quantity adjustment with +/- buttons
- Customer name and phone collection
- Multiple payment methods (Cash, EasyPaisa, Card)
- Printable invoice (thermal printer ready)
- Keyboard shortcuts (F2=Add, F5=Checkout, F3=Search)

### Inventory Management
- Product catalog with categories and brands
- Stock tracking with automatic deduction on sale
- Low stock alerts based on reorder levels
- Purchase order system for buying new stock
- Stock increase on purchase confirmation
- Supplier records

### Dashboard & Analytics
- Today's sales, profit, and invoice count
- Monthly profit calculation
- Low stock summary
- Today's transaction list
- Recent invoices (last 5)
- Sales chart visualization

### Administration
- Django admin panel for full control
- Role-based access (Admin, Cashier)
- Product and category management
- Purchase history
- Database backup ready

## Installation

### Prerequisites
- Python 3.11 or higher
- MySQL server
- pip package manager

### Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/ZiaSaafir/Smart-Electronics-Sales-System.git
cd Smart-Electronics-Sales-System
2Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Configure MySQL database
Create database in MySQL:

sql
CREATE DATABASE farman_pos_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
Update database settings in config/settings.py:

python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'farman_pos_db',
        'USER': 'root',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
Run migrations

bash
python manage.py makemigrations
python manage.py migrate
Create admin user

bash
python manage.py createsuperuser
Run development server

bash
python manage.py runserver
Access the application

POS Interface: http://127.0.0.1:8000/pos/

Admin Panel: http://127.0.0.1:8000/admin/

Dashboard: http://127.0.0.1:8000/dashboard/

Project Structure
text
farman_pos/
├── config/          # Project settings and URLs
├── products/        # Product, category, brand models
├── sales/           # POS, checkout, invoice logic
├── dashboard/       # Analytics and reports
├── inventory/       # Stock management
├── purchase/        # Purchase orders and suppliers
├── templates/       # HTML templates
├── static/          # CSS, JS, images
└── manage.py        # Django management script
Keyboard Shortcuts
Key	Action
F2	Add current product to cart
F3	Focus search box
F5	Checkout / Complete sale
Ctrl+C	Clear entire cart
Screenshots
POS Billing Interface
Main sales screen with product search and cart management.

Dashboard
Real-time sales analytics and low stock alerts.

Invoice
Printable receipt with customer and payment details.

Product Management
Product catalog with stock status and search filters.

Deployment
Local Shop PC (Windows)
Install Python and MySQL on shop computer

Copy project folder to C:\farman_pos

Create virtual environment and install dependencies

Configure database with shop's MySQL

Run migrations and create admin user

Use start_pos.bat for one-click launch

Production Settings
Set DEBUG = False in production and configure ALLOWED_HOSTS with your shop's IP address.
