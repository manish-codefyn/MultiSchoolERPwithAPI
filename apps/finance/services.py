import razorpay
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class RazorpayService:
    """
    Service to handle interactions with Razorpay Payment Gateway
    """
    
    @staticmethod
    def get_client():
        """Get authenticated Razorpay client"""
        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        
        if not key_id or not key_secret:
            logger.warning("Razorpay keys not configured.")
            return None
            
        return razorpay.Client(auth=(key_id, key_secret))

    @staticmethod
    def create_order(amount, currency="INR", receipt=None, notes=None):
        """
        Create a Razorpay order
        :param amount: Amount in currency (not subunits)
        :param currency: Currency code
        :param receipt: Internal receipt ID
        :param notes: Dictionary of notes
        """
        client = RazorpayService.get_client()
        if not client:
            return None
            
        try:
            # Convert amount to subunits (paisa)
            amount_in_paise = int(float(amount) * 100)
            
            data = {
                "amount": amount_in_paise,
                "currency": currency,
                "receipt": str(receipt) if receipt else None,
                "notes": notes or {}
            }
            
            order = client.order.create(data=data)
            return order
        except Exception as e:
            logger.error(f"Razorpay Order Creation Failed: {str(e)}")
            return None

    @staticmethod
    def verify_payment_signature(payment_id, order_id, signature):
        """
        Verify Razorpay payment signature
        """
        client = RazorpayService.get_client()
        if not client:
            return False
            
        try:
            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            client.utility.verify_payment_signature(params_dict)
            return True
        except razorpay.errors.SignatureVerificationError:
            logger.error("Razorpay Signature Verification Failed")
            return False
        except Exception as e:
            logger.error(f"Error verifying signature: {str(e)}")
            return False
