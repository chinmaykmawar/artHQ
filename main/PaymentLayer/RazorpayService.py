from asyncio.log import logger
import json
from django.http import JsonResponse, HttpResponse
import razorpay
import hashlib
import hmac
import requests
from main import settings
from razorpay.errors import SignatureVerificationError

class RazorpayService:
    def __init__(self):
        self.client=None
        try:
            self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
            logger.info("Razorpay client initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing Razorpay client: {str(e)}")
    
    def create_order(self, amount, data):
        try:
            order = self.client.order.create({
                "amount": int(amount),  # paise
                "currency": "INR",
                "receipt": str(data.get('receipt'))
            })
        
            logger.info("Razorpay order created successfully.")

            return JsonResponse({
                'status': 'success',
                'order_id': order['id'],
                'amount': order['amount'],
                'key': settings.RAZORPAY_KEY_ID,
                'error': None
            })

        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            return JsonResponse({
                'status': 'failed',
                'order_id': None,
                'amount': None,
                'key': None,
                'error': str(e)})

    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        try:
            self.client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
            })

            logger.info(f"Payment verified successfully for order {razorpay_order_id}")
            return True

        except SignatureVerificationError:
            logger.warning(f"Invalid payment signature for order {razorpay_order_id}")
            return False

        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return False
        
        #self.client.utility.verify_payment_signature(...) TBD
        
        # 🔐 Verify signature
        # generated_signature = hmac.new(
        #     bytes(settings.RAZORPAY_SECRET, 'utf-8'),
        #     bytes(razorpay_order_id + "|" + razorpay_payment_id, 'utf-8'),
        #     hashlib.sha256
        #     ).hexdigest()

        # return (generated_signature == razorpay_signature)

        
            

