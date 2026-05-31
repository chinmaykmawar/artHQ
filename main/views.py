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
    #data= {'razorpay_order_id': 'order_SusxLSisJmQY4e', 'razorpay_payment_id': 'pay_SusxdudoAxgw5q', 'razorpay_signature': '72a65e063c71f000618e775007a8a82790cf2a3647b50e2e935e6c11b5b7113f', 'name': 'Name_Chinmay', 'phone': '8800156300', 'address': 'Addressssssssss', 'city': 'City', 'pincode': '226022', 'email': 'chinmaykmawar@gmail.com', 'cart': [{'Name': 'JER10005PiW', 'Price': 199, 'Title': 'Handcrafted Dual-Tone Earrings with Iridescent Studs & Textured Pink Floral Accents – Artistic Statement Jewelry for Women', 'Description': 'Celebrate artistry and individuality with these handcrafted dual-tone earrings, featuring a unique blend of elegance and bold design. The upper studs glow with a soft iridescent sheen, shifting colors gently like moonlight, while the lower textured pink floral discs sparkle with golden accents and delicate detailing. Together, they create a playful yet sophisticated balance — perfect for women who embrace both subtle charm and vibrant expression.\n\nLightweight and versatile, these earrings can elevate everyday outfits, add a festive pop to traditional wear, or become the highlight of a creative, contemporary look. Each pair is uniquely made, ensuring your earrings are as distinctive as you are.', 'Product_ID': 'JER10005PiW', 'Sub_Category': 'Earrings', 'Base_Color': 'Pink', 'Highlight': 'White', 'Design': 10005, 'Bar Code': '', 'Sub-Cat Code': 'ER', 'qty': 1}], 'delivery_charge': 99, 'items_total': 199, 'grand_total': 298}
    #save_to_sheets(data)
    #return JsonResponse({"status": "success"})


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

    print(f"Data: {data}\n\n")

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

    print(f"Payload: {payload}\n\n")

    try:
        response = requests.post(url, json=payload)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

    except Exception as e:
        print("ERROR:", str(e))

@csrf_exempt
def get_orders(request):
    data = json.loads(request.body)
    url = "https://script.google.com/macros/s/AKfycbx7XwBXljynHLRc3PtAkItuW2WSDN0jwr1gQHw7k0tC2PP3GkR3XVll4gHbynQTs0p-/exec"
    try:
        response = requests.post(url,json=data)
        return HttpResponse(response.text,content_type='application/json')
    except Exception as e:
        return JsonResponse({"error": str(e)},status=500)