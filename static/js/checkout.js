RAZORPAY_KEY_ID_TEST = 'rzp_test_Sh4tdflR7VHLCl'
RAZORPAY_KEY_ID_LIVE = 'rzp_live_Svwpu3AEgbK6V6'
const DELIVERY_CHARGE = 0
const FREE_DELIVERY_THRESHOLD = 2500

function getCart() {
  imm_checkout = JSON.parse(sessionStorage.getItem('CHECKOUT') || '[]')
  if (imm_checkout.length > 0) {
    return imm_checkout
  }

  return JSON.parse(sessionStorage.getItem('CART') || '[]')
}

function renderCheckout() {
  const cart = getCart()

  let itemsTotal = 0

  $('#checkout_items').html('')

  cart.forEach((item) => {
    itemsTotal += item.Price * item.qty

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

  let deliveryCharge = DELIVERY_CHARGE

  if (itemsTotal >= FREE_DELIVERY_THRESHOLD) {
    deliveryCharge = 0

    $('#free_delivery_message').html(`
      🎉 Congratulations! You have unlocked FREE delivery.
    `)
  } else {
    const remaining = FREE_DELIVERY_THRESHOLD - itemsTotal

    $('#free_delivery_message').html(`
      Add items worth ₹${remaining}
      more to unlock FREE delivery 🚚
    `)
  }

  const grandTotal = itemsTotal + deliveryCharge

  $('#items_total_price').text('₹' + itemsTotal)

  $('#delivery_charge').text(deliveryCharge === 0 ? 'FREE' : '₹' + deliveryCharge)

  $('#total_price').text('₹' + grandTotal)
}

function validateForm() {
  const name = $('#name').val().trim()

  const phone = $('#phone').val().trim()

  const email = $('#email').val().trim()

  const address = $('#address').val().trim()

  const city = $('#city').val().trim()

  const pincode = $('#pincode').val().trim()

  // NAME
  if (name.length < 3) {
    alert('Please enter valid name')
    return false
  }

  // PHONE
  const phoneRegex = /^[6-9]\d{9}$/

  if (!phoneRegex.test(phone)) {
    alert('Please enter valid 10 digit mobile number')
    return false
  }

  // EMAIL
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if (!emailRegex.test(email)) {
    alert('Please enter valid email address')
    return false
  }

  // ADDRESS
  if (address.length < 10) {
    alert('Please enter complete address')
    return false
  }

  // CITY
  if (city.length < 2) {
    alert('Please enter valid city')
    return false
  }

  // PINCODE
  const pincodeRegex = /^\d{6}$/

  if (!pincodeRegex.test(pincode)) {
    alert('Please enter valid 6 digit pincode')
    return false
  }

  return true
}

function removePurchasedItems(purchasedCart) {
  let imm_checkout = JSON.parse(sessionStorage.getItem('CHECKOUT') || '[]')
  if (imm_checkout.length > 0) {
    imm_checkout.forEach((checkoutItem) => {
      const purchasedItem = purchasedCart.find((item) => item.Product_ID === checkoutItem.Product_ID)
      if (purchasedItem) {
        checkoutItem.qty -= purchasedItem.qty
      }
    })

    imm_checkout = imm_checkout.filter((item) => item.qty > 0)
    if (imm_checkout.length > 0) {
      alert(`Not all items in immediate checkout were purchased. Removing only the purchased items from checkout...`)
    } else {
      sessionStorage.setItem('CHECKOUT', JSON.stringify([]))
    }
  } else {
    let currentCart = JSON.parse(sessionStorage.getItem('CART') || '[]')

    // Remove items that were purchased
    currentCart.forEach((currentItem) => {
      const purchasedItem = purchasedCart.find((item) => item.Product_ID === currentItem.Product_ID)

      if (purchasedItem) {
        currentItem.qty -= purchasedItem.qty
      }
    })

    currentCart = currentCart.filter((item) => item.qty > 0)

    sessionStorage.setItem('CART', JSON.stringify(currentCart))
  }
  console.log('Purchased items removed from cart/checkout')
}

async function startPayment() {
  if (!validateForm()) {
    return
  }

  const cart = getCart()

  let itemsTotal = 0
  let qty = 0

  cart.forEach((item) => {
    itemsTotal += item.Price * item.qty
    qty += item.qty
  })

  let deliveryCharge = DELIVERY_CHARGE

  if (itemsTotal >= FREE_DELIVERY_THRESHOLD) {
    deliveryCharge = 0
  }

  const total = itemsTotal + deliveryCharge

  // 1️⃣ Create order from backend
  order = {
    method: 'POST',
    body: JSON.stringify({
      amount: total,
      receipt: Date.now(),
    }),
  }
  console.log('Razorpay Order:', order)

  const orderRes = await fetch('/create-order/', order)
  console.log('Razorpay Order creation response:', orderRes)

  const orderData = await orderRes.json()
  console.log('Razorpay Order Data:', orderData)

  // 2️⃣ Open Razorpay checkout
  $('#place_order_btn').prop('disabled', true)

  var options = {
    key: RAZORPAY_KEY_ID_LIVE,
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
        email: $('#email').val(),

        cart: cart,

        delivery_charge: deliveryCharge,
        items_total: itemsTotal,
        grand_total: total,
      }

      const verifyRes = await fetch('/verify-payment/', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(orderData),
      })

      const result = await verifyRes.json()

      if (result.status === 'success') {
        console.log(`Payment ID : ${orderData.razorpay_payment_id} verified successfully`)

        // ✅ Remove only purchased items
        removePurchasedItems(cart)

        // 👉 Redirect to success page
        window.location.href = `/order-success/?order_id=${response.razorpay_order_id}`
      } else {
        alert(`Payment ID : ${orderData.razorpay_payment_id} verification failed`)
      }
    },

    prefill: {
      name: $('#name').val(),
      contact: $('#phone').val(),
    },
    notes: {
      customer_name: $('#name').val(),
      quantity: qty,
    },
    theme: {
      color: '#000',
    },
  }
  console.log('Razorpay Options:', options)

  var rzp = new Razorpay(options)
  rzp.open()
}

/* INIT */
$(document).ready(function () {
  renderCheckout()
})

// BUTTON
$('#place_order_btn').on('click', function () {
  startPayment()
})
