
import os
import django
import sys
import logging

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django_tenants.utils import schema_context
from apps.tenants.models import Tenant, PaymentConfiguration
from apps.finance.services import RazorpayService

# Get the tenant
try:
    tenant = Tenant.objects.get(schema_name='dps_kolkata')
    print(f"Found tenant: {tenant.name} ({tenant.schema_name})")
except Tenant.DoesNotExist:
    print("Tenant 'dps_kolkata' not found!")
    sys.exit(1)

# Debug Payment Configuration
with schema_context(tenant.schema_name):
    print("\n--- Payment Configuration ---")
    try:
        config = PaymentConfiguration.objects.get(tenant=tenant)
        print(f"Config found: {config}")
        print(f"Key ID Present: {bool(config.razorpay_key_id)}")
        print(f"Key Secret Present: {bool(config.razorpay_key_secret)}")
        print(f"Key ID Value: '{config.razorpay_key_id}'") # careful with secrets in real logs
        
        # Test Service
        print("\n--- Testing RazorpayService ---")
        client = RazorpayService.get_client(tenant)
        if client:
             print("Razorpay Client initialized successfully")
             
             # Try simple auth check (get order or just verify creds)
             try:
                 # Just creating a dummy order to verify keys
                 print("Attempting to create generic test order...")
                 order = client.order.create({
                     "amount": 100, # 1 rupee
                     "currency": "INR",
                     "receipt": "debug_test_001"
                 })
                 print(f"Order created successfully: {order['id']}")
             except Exception as e:
                 print(f"ERROR creating order: {e}")
        else:
             print("RazorpayService.get_client returned None!")

    except PaymentConfiguration.DoesNotExist:
        print("PaymentConfiguration DOES NOT EXIST for this tenant!")
    except Exception as e:
        print(f"Unexpected error: {e}")

