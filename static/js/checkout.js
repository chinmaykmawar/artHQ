const RAZORPAY_SECRET = 'xSwba14fAdI9j1a9I96wZuzD'

const RAZORPAY_KEY_ID = 'rzp_test_Sh4tdflR7VHLCl'

function getCart() {
  imm_checkout = JSON.parse(sessionStorage.getItem('CHECKOUT') || '[]')
  if (imm_checkout.length > 0) {
    return imm_checkout
  }

  return JSON.parse(sessionStorage.getItem('CART') || '[]')
}

function renderCheckout() {
  const cart = getCart()
  let total = 0

  $('#checkout_items').html('')

  cart.forEach((item) => {
    total += item.Price * item.qty

    const html = `
      <div class="checkout_item">
        <img src="/static/assets/Product_Images/${item.Product_ID}/${item.Product_ID}_1.jpg">
        <div class="checkout_item_details">
          <div>${item.Title}</div>
          <div>₹${item.Price} x ${item.qty}</div>
        </div>
      </div>
    `

    $('#checkout_items').append(html)
  })

  $('#total_price').text('₹' + total)
}

function validateForm() {
  if (!$('#name').val() || !$('#phone').val() || !$('#address').val()) {
    alert('Please fill all required fields')
    return false
  }
  return true
}

function removePurchasedItems(purchasedCart) {
  let currentCart = JSON.parse(sessionStorage.getItem('CART') || '[]')

  // Remove items that were purchased
  currentCart = currentCart.filter((currentItem) => {
    return !purchasedCart.some((purchasedItem) => purchasedItem.Product_ID === currentItem.Product_ID)
  })

  sessionStorage.setItem('CART', JSON.stringify(currentCart))
}

/* INIT */
$(document).ready(function () {
  renderCheckout()
})

async function startPayment() {
  const cart = JSON.parse(sessionStorage.getItem('CART') || '[]')

  let total = 0
  cart.forEach((item) => (total += item.Price * item.qty))

  // 1️⃣ Create order from backend
  const orderRes = await fetch('/create-order/', {
    method: 'POST',
    body: JSON.stringify({
      amount: total,
      receipt: Date.now(),
    }),
  })

  const orderData = await orderRes.json()

  // 2️⃣ Open Razorpay checkout
  var options = {
    key: RAZORPAY_KEY_ID,
    amount: orderData.amount,
    currency: 'INR',
    name: 'ArtHQ',
    description: 'Order Payment',
    order_id: orderData.order_id,

    handler: async function (response) {
      const orderData = {
        razorpay_order_id: response.razorpay_order_id,
        razorpay_payment_id: response.razorpay_payment_id,
        razorpay_signature: response.razorpay_signature,

        name: $('#name').val(),
        phone: $('#phone').val(),
        address: $('#address').val(),
        city: $('#city').val(),
        pincode: $('#pincode').val(),

        cart: cart,
        amount: total,
      }

      const verifyRes = await fetch('/verify-payment/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(orderData),
      })

      const result = await verifyRes.json()

      if (result.status === 'success') {
        // ✅ Remove only purchased items
        removePurchasedItems(cart)

        // 👉 Redirect to success page
        window.location.href = `/order-success/?order_id=${response.razorpay_order_id}`
      } else {
        alert('Payment verification failed')
      }
    },

    prefill: {
      name: $('#name').val(),
      contact: $('#phone').val(),
    },

    theme: {
      color: '#000',
    },
  }

  var rzp = new Razorpay(options)
  rzp.open()
}

// BUTTON
$('#place_order_btn').on('click', function () {
  startPayment()
})
