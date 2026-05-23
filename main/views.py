import os
import razorpay
import json
import hmac
import hashlib
import requests
import json
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
RAZORPAY_SECRET = 'xSwba14fAdI9j1a9I96wZuzD'
RAZORPAY_KEY_ID = 'rzp_test_Sh4tdflR7VHLCl'

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_SECRET))


# ✅ CREATE ORDER
@csrf_exempt
def create_order(request):
    try:
        data = json.loads(request.body)

        amount = float(data.get('amount', 0))

        if amount <= 0:
            return JsonResponse({"error": "Invalid amount"}, status=400)

        order = client.order.create({
            "amount": int(amount * 100),  # paise
            "currency": "INR",
            "receipt": str(data.get('receipt'))
        })

        return JsonResponse({
            "order_id": order['id'],
            "amount": order['amount']
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ VERIFY PAYMENT + SAVE
@csrf_exempt
def verify_payment(request):
    data = json.loads(request.body)

    razorpay_order_id = data['razorpay_order_id']
    razorpay_payment_id = data['razorpay_payment_id']
    razorpay_signature = data['razorpay_signature']

    # 🔐 Verify signature
    generated_signature = hmac.new(
        bytes(RAZORPAY_SECRET, 'utf-8'),
        bytes(razorpay_order_id + "|" + razorpay_payment_id, 'utf-8'),
        hashlib.sha256
    ).hexdigest()

    if generated_signature == razorpay_signature:

        # ✅ SAVE TO GOOGLE SHEETS
        save_to_sheets(data)

        return JsonResponse({"status": "success"})
    else:
        return JsonResponse({"status": "failed"})


# ✅ GOOGLE SHEETS API 
def save_to_sheets(data):
    url = "https://script.google.com/macros/s/AKfycbx7XwBXljynHLRc3PtAkItuW2WSDN0jwr1gQHw7k0tC2PP3GkR3XVll4gHbynQTs0p-/exec"

    cart_items = data.get("cart", [])

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
        "address": data.get("address"),
        "city": data.get("city"),
        "pincode": data.get("pincode"),

        "total_amount": data.get("amount"),
        "cart": cart_string
    }
    try:
        response = requests.post(url, json=payload)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

    except Exception as e:
        print("ERROR:", str(e))