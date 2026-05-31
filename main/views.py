from asyncio.log import logger
import os
from unittest import result
import razorpay
import json
import hmac
import hashlib
import requests
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.template import loader
from django.shortcuts import redirect, render

def index(request):
    #return render(request, 'homepage.html')
    return redirect('/products')

def products_grid(request):
    return render(request, 'products_grid.html')

def product(request, id):
    return render(request, 'product_page.html', {'id':id})

def test(request):
    return render(request, 'test.html')

def test2(request, id):
    return render(request, 'test.html', {'id':id})

def checkout_view(request):
    return render(request, 'checkout.html')

def order_success(request):
    order_id = request.GET.get('order_id', '')
    return render(request, 'order_success.html', {"order_id": order_id})

def track_order(request):
    return render(request,'track_order.html')

def returns_exchange(request):
    return render(request, 'returns_exchange.html')

def privacy_policy(request):
    return render(request,'privacy_policy.html')

def terms(request):
    return render(request,'terms.html')

def our_story(request):
    return render(request,'our_story.html')

def contact_us(request):
    return render(request,'contact_us.html')

def get_product_images(request, product_id):
    folder = os.path.join(
        settings.BASE_DIR,
        'static/assets/Product_Images',
        product_id
    )

    images = []

    if os.path.exists(folder):
        for file in os.listdir(folder):
            if file.endswith('.jpg'):
                images.append(file)

    return JsonResponse(images, safe=False)

# TEST KEYS (replace later)
RAZORPAY_KEY_ID_TEST = 'rzp_test_Sh4tdflR7VHLCl'
RAZORPAY_SECRET_TEST = 'xSwba14fAdI9j1a9I96wZuzD'
RAZORPAY_KEY_ID_LIVE = 'rzp_live_Svwpu3AEgbK6V6'
RAZORPAY_SECRET_LIVE = 'HcvnBy1Z4vyuOZpmZ8pu6pcd'

# ✅ CREATE ORDER
@csrf_exempt
def create_order(request):
    logger.info(f"Create order request received: {request.body}")
    data = json.loads(request.body)
    amount = float(data.get('amount', 0))
    if amount <= 0:
        return JsonResponse({"error": "Invalid amount"}, status=400)
    

    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID_LIVE, RAZORPAY_SECRET_LIVE))
        logger.info("Razorpay client initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing Razorpay client: {str(e)}")
    
    try:
        order = client.order.create({
            "amount": int(amount * 100),  # paise
            "currency": "INR",
            "receipt": str(data.get('receipt'))
        })
        
        logger.info("Razorpay order created successfully.")

        return JsonResponse({
            "order_id": order['id'],
            "amount": order['amount']
        })

    except Exception as e:
        logger.error(f"Error creating Razorpay order: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)


# ✅ VERIFY PAYMENT + SAVE
@csrf_exempt
def verify_payment(request):
    logger.info(f"Verify payment request received: {request.body}")
    data = json.loads(request.body)

    razorpay_order_id = data['razorpay_order_id']
    razorpay_payment_id = data['razorpay_payment_id']
    razorpay_signature = data['razorpay_signature']

    # 🔐 Verify signature
    generated_signature = hmac.new(
        bytes(RAZORPAY_SECRET_LIVE, 'utf-8'),
        bytes(razorpay_order_id + "|" + razorpay_payment_id, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    if generated_signature == razorpay_signature:

        # ✅ SAVE TO GOOGLE SHEETS
        save_to_sheets(data)
        logger.info(f"Payment verified and saved for order: {razorpay_order_id}")
        return JsonResponse({"status": "success"})
    else:
        logger.warning(f"Payment verification failed for order: {razorpay_order_id}")
        return JsonResponse({"status": "failed"})


# ✅ GOOGLE SHEETS API 
def save_to_sheets(data):


    url = "https://script.google.com/macros/s/AKfycbx7XwBXljynHLRc3PtAkItuW2WSDN0jwr1gQHw7k0tC2PP3GkR3XVll4gHbynQTs0p-/exec"
    cart_items = data.get("cart", [])

    logger.info(f"Saving order data to Google Sheets: {data}\n\n")

    cart_summary = []
    for item in cart_items:
        product_id = item.get("Product_ID")
        qty = item.get("qty", 1)

        cart_summary.append(f"{product_id} x {qty}")

    cart_string = ", ".join(cart_summary)

    payload = {
        "order_id": data.get("razorpay_order_id"),
        "payment_id": data.get("razorpay_payment_id"),

        "name": data.get("name"),
        "phone": data.get("phone"),
        'email': data.get("email"),
        "address": data.get("address"),
        "city": data.get("city"),
        "pincode": data.get("pincode"),

        "item_amount": data.get("items_total"),
        "delivery_charge": data.get("delivery_charge"),
        "total_amount": data.get("grand_total"),
        "cart": cart_string
    }

    logger.info(f"Payload: {payload}\n\n")

    try:
        response = requests.post(url, json=payload)
        result=response.json()

        if result.get("status")!="success":
            raise Exception(result.get("message"))
        logger.info(f"Google Sheets response: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Error saving data to Google Sheets: {str(e)}")
    

@csrf_exempt
def get_orders(request):
    data = json.loads(request.body)
    url = "https://script.google.com/macros/s/AKfycbx7XwBXljynHLRc3PtAkItuW2WSDN0jwr1gQHw7k0tC2PP3GkR3XVll4gHbynQTs0p-/exec"
    try:
        response = requests.post(url,json=data)
        logger.info(f"Get orders response: {response.status_code} - {response.text}")   
        return HttpResponse(response.text,content_type='application/json')
    except Exception as e:
        logger.error(f"Error fetching orders from Google Sheets: {str(e)}")
        return JsonResponse({"error": str(e)},status=500)