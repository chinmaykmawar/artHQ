from asyncio.log import logger
import json
from django.http import JsonResponse
from main.helpers.factory import DataFactory, PaymentFactory

def create_order(request):
    logger.info(f"Create order request received: {request.body}")
    data = json.loads(request.body)
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return JsonResponse({"error": "Invalid amount"}, status=400)
    
    ps = PaymentFactory.get_payment_service()
    return ps.create_order(amount, data)

def verify_payment(request):
    logger.info(f"Verify payment request received: {request.body}")
    checkoutData = json.loads(request.body)
        
    order_id = checkoutData['paymentData']['order_id']
    payment_id = checkoutData['paymentData']['transactionId']
    signature = checkoutData['paymentData']['verificationToken']
    
    ps= PaymentFactory.get_payment_service()
    verified = ps.verify_payment(order_id, payment_id, signature)
    
    if verified:
        result = save_order(checkoutData)
        if result:
            logger.info(f"Payment verified and saved for order: {order_id}")
            return JsonResponse({"status": "success"})
        else:
            logger.error(f"Payment verified but failed to save order: {order_id}")
            return JsonResponse({"status": "failed", "error": "Failed to save order"})
    else:
        logger.warning(f"Payment verification failed for order: {order_id}")
        return JsonResponse({"status": "failed", "error": "Failed to verify payment"})

def save_order(data):
    om = DataFactory.get_order_manager()
    return om.save_order(data)

def get_orders(request):
    om = DataFactory.get_order_manager()
    return om.get_orders(request)