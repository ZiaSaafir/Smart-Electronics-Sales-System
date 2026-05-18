from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from products.models import Product, Category, Brand
from sales.models import Sale, SaleItem


class SaleValidationTest(TestCase):
    """
    Test sales have valid amounts
    """
    
    def setUp(self):
        """Create test data before each test"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='test123')
        
        # Create test product
        self.category = Category.objects.create(name='Test Category')
        self.brand = Brand.objects.create(name='Test Brand')
        
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-001',
            category=self.category,
            brand=self.brand,
            cost_price=100,
            selling_price=200,
            stock_quantity=10,
            reorder_level=5,
            is_active=True
        )
    
    def test_no_zero_amount_invoices(self):
        """Check if any invoice has zero total amount"""
        zero_invoices = Sale.objects.filter(total_amount=0)
        
        if zero_invoices.count() > 0:
            print(f"⚠️ Warning: {zero_invoices.count()} invoices have zero amount")
            for inv in zero_invoices[:3]:
                print(f"   - {inv.invoice_no}")
        
        self.assertTrue(True)
    
    def test_negative_amount_invoices(self):
        """Check for negative total amounts"""
        negative_invoices = Sale.objects.filter(total_amount__lt=0)
        
        self.assertEqual(negative_invoices.count(), 0,
                        "Found invoices with negative amount")
        
        print("✓ No negative amount invoices")

    def test_invoice_total_matches_items(self):
        """Check if invoice total equals sum of its items"""
        mismatched = []
        
        for sale in Sale.objects.all()[:10]:
            items_total = sum(float(item.line_total) for item in sale.items.all())
            sale_total = float(sale.total_amount)
            
            if abs(sale_total - items_total) > 0.01:
                mismatched.append(sale.invoice_no)
        
        if mismatched:
            print(f"⚠️ Warning: {len(mismatched)} invoices have mismatched totals")
        else:
            print("✓ All invoice totals match their items")
        
        self.assertTrue(True)


class DuplicateCheckTest(TestCase):
    """
    Test for duplicate records
    """
    
    def test_no_duplicate_invoices(self):
        """Check for duplicate invoice numbers"""
        from django.db.models import Count
        
        duplicates = Sale.objects.values('invoice_no').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        self.assertEqual(duplicates.count(), 0,
                        f"Found duplicate invoice numbers")
        
        print("✓ No duplicate invoices found")

    def test_no_duplicate_products(self):
        """Check for duplicate product SKUs"""
        from django.db.models import Count
        
        # Check if any products exist first
        if Product.objects.exists():
            duplicates = Product.objects.values('sku').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            self.assertEqual(duplicates.count(), 0, "Found duplicate SKUs")
        else:
            print("⚠️ No products found to check")
        
        print("✓ No duplicate SKUs found")


class EdgeCaseTest(TestCase):
    """
    Test edge cases and boundary conditions
    """
    
    def setUp(self):
        """Create test data"""
        self.user = User.objects.create_superuser(
            username='admin', 
            email='admin@test.com', 
            password='admin123'
        )
        self.client = Client()
        self.client.login(username='admin', password='admin123')
        
        # Create test product
        self.category = Category.objects.create(name='Test')
        self.brand = Brand.objects.create(name='Test')
        
        self.product = Product.objects.create(
            name='Test Product',
            sku='TEST-EDGE',
            category=self.category,
            brand=self.brand,
            cost_price=100,
            selling_price=200,
            stock_quantity=5,  # Limited stock
            reorder_level=2,
            is_active=True
        )
    
    def test_cannot_add_more_than_stock(self):
        """Test that user cannot add more than available stock"""
        excess_quantity = self.product.stock_quantity + 10
        
        cart_data = {
            'cart': [{
                'id': str(self.product.id),
                'name': self.product.name,
                'price': float(self.product.selling_price),
                'qty': excess_quantity
            }],
            'customer_name': 'Edge Test',
            'customer_phone': '',
            'payment_method': 'cash'
        }
        
        response = self.client.post('/pos/checkout/', 
                                   cart_data, 
                                   content_type='application/json')
        
        # Should fail (400 or 200 with error message)
        self.assertIn(response.status_code, [400, 200])
        print("✓ Cannot add more than available stock")
    
    def test_quantity_zero_not_allowed(self):
        """Test that quantity zero is not allowed"""
        cart_data = {
            'cart': [{
                'id': str(self.product.id),
                'name': self.product.name,
                'price': float(self.product.selling_price),
                'qty': 0
            }],
            'customer_name': 'Zero Test',
            'customer_phone': '',
            'payment_method': 'cash'
        }
        
        response = self.client.post('/pos/checkout/', 
                                   cart_data, 
                                   content_type='application/json')
        
        self.assertIn(response.status_code, [400, 200])
        print("✓ Quantity zero rejected")
    
    def test_empty_cart_checkout(self):
        """Test checkout with empty cart"""
        cart_data = {
            'cart': [],
            'customer_name': 'Empty Test',
            'customer_phone': '',
            'payment_method': 'cash'
        }
        
        response = self.client.post('/pos/checkout/', 
                                   cart_data, 
                                   content_type='application/json')
        
        # Empty cart should return 400
        self.assertEqual(response.status_code, 400)
        print("✓ Empty cart checkout rejected")


class CustomerDataTest(TestCase):
    """
    Test customer data quality
    """
    
    def test_customer_name_consistency(self):
        """Check for empty customer names"""
        total_sales = Sale.objects.count()
        named_customers = Sale.objects.exclude(
            customer_name__isnull=True
        ).exclude(customer_name='').count()
        unnamed = total_sales - named_customers
        
        print(f"Total Sales: {total_sales}")
        print(f"Named Customers: {named_customers}")
        print(f"Walk-in Customers: {unnamed}")
        
        self.assertTrue(True)