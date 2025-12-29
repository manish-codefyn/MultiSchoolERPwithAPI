
import os
import django
import sys

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from apps.finance.services import RazorpayService

print(f"--- Settings Debug ---")
print(f"Key ID: {getattr(settings, 'RAZORPAY_KEY_ID', 'MISSING')}")
# print(f"Key Secret: {getattr(settings, 'RAZORPAY_KEY_SECRET', 'MISSING')}") # Don't print secret in logs

print("\n--- RazorpayService Order Test ---")
client = RazorpayService.get_client()

if not client:
    print("ERROR: RazorpayService.get_client returned None!")
else:
    print("Razorpay Client initialized.")
    try:
        print("Attempting to create generic test order (Amount: 100 paise)...")
        order = client.order.create({
            "amount": 100,
            "currency": "INR",
            "receipt": "debug_final_001"
        })
        print(f"SUCCESS: Order created! ID: {order['id']}")
    except Exception as e:
        print(f"FAILURE: Error creating order: {e}")
