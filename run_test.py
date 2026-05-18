#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import and run tests
from django.test.utils import get_runner
from django.conf import settings

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, interactive=True)

# Run only specific test classes
from products.tests import StockTest
from sales.tests import SaleValidationTest, DuplicateCheckTest, EdgeCaseTest
from inventory.tests import InventoryTest

import unittest

# Create test suite
suite = unittest.TestSuite()
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(StockTest))
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(SaleValidationTest))
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(InventoryTest))
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(DuplicateCheckTest))
suite.addTest(unittest.TestLoader().loadTestsFromTestCase(EdgeCaseTest))

# Run tests
result = unittest.TextTestRunner(verbosity=2).run(suite)

# Print summary
print("\n" + "="*50)
print("TEST SUMMARY")
print("="*50)
print(f"Tests Run: {result.testsRun}")
print(f"Failures: {len(result.failures)}")
print(f"Errors: {len(result.errors)}")

if result.wasSuccessful():
    print("\n✅ ALL TESTS PASSED!")
else:
    print("\n❌ SOME TESTS FAILED!")
