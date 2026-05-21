# Smart Electronics Sales System - POS Application

##  Project Information

### Group Information
- **Group Number:** 18
- **Group Members:**
   Name  Roll Number 
   
   Moiz khalid 24p0742 
   Zia ullah   24p0660 
   Qasim       24p0672 

### Project Title
**Smart Electronics Sales System - Point of Sale (POS) Application**

### Short Description
A comprehensive Point of Sale (POS) system designed for electronics shops to manage sales, inventory, and customer transactions. The system provides an intuitive interface for cashiers to process sales, manage products, track inventory, and generate invoices. It includes role-based access control with admin and cashier privileges, real-time stock management, and printable receipts.

**Key Features:**
- Complete CRUD operations for Products, Categories, and Customers
- Real-time inventory management
- Sales transaction processing with invoice generation
- User authentication with role-based access (Admin/Cashier)
- Search and filter functionality
- Sales reports and analytics dashboard
- Printable receipts for thermal printers

---

##  GitHub Repository

**Repository URL:** [https://github.com/ZiaSaafir/Smart-Electronics-Sales-System](https://github.com/ZiaSaafir/Smart-Electronics-Sales-System)

---

##  Technologies Used

| Category | Technologies |
|----------|--------------|
| **Backend Framework** | Django 4.2 (Python Web Framework) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, JavaScript |
| **Database** | MySQL 8.0 / SQLite3 |
| **Server** | Django Development Server |
| **Additional Libraries** | django-crispy-forms, reportlab (PDF generation), Pillow (image handling) |
| **Version Control** | Git & GitHub |

---

##  Installation and Setup Guide

### System Requirements
- Windows 10/11, Linux, or macOS
- 4GB RAM minimum
- 20GB free disk space
- Internet connection (for initial setup)

### Prerequisites Installation

#### 1. Install Python 3.11
- Download from: https://www.python.org/downloads/
- **IMPORTANT:** Check "Add Python to PATH" during installation
- Verify installation:
  ```bash
  python --version
2. Install MySQL (Optional - for production)
Download from: https://dev.mysql.com/downloads/installer/

Set root password (remember it!)

Or use SQLite (no installation needed)

Step-by-Step Installation
Step 1: Clone the Repository
bash
# Clone from GitHub
git clone https://github.com/ZiaSaafir/Smart-Electronics-Sales-System.git

# Navigate to project directory
cd Smart-Electronics-Sales-System
Step 2: Create Virtual Environment
bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
Step 3: Install Dependencies
bash
pip install -r requirements.txt
Step 4: Configure Database
Option A: Using SQLite (Default - No setup required)

No additional configuration needed

Option B: Using MySQL (Recommended for production)

Create database:

sql
CREATE DATABASE farman_pos_db CHARACTER SET utf8mb4;
Update config/settings.py:

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
Step 5: Run Migrations
bash
python manage.py makemigrations
python manage.py migrate
Step 6: Create Admin User
bash
python manage.py createsuperuser
Follow prompts to create admin account.

Step 7: Create Cashier User
bash
python manage.py shell
python
from django.contrib.auth.models import User
from accounts.models import UserProfile

cashier = User.objects.create_user('cashier', 'cashier@shop.com', 'cashier123')
UserProfile.objects.create(user=cashier, role='cashier')
exit()
Step 8: Collect Static Files
bash
python manage.py collectstatic --noinput
Step 9: Run the Application
bash
python manage.py runserver
Step 10: Access the Application
Open browser and navigate to: http://127.0.0.1:8000

Admin Panel: http://127.0.0.1:8000/admin

POS Interface: http://127.0.0.1:8000/pos
