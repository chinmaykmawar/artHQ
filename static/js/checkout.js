RAZORPAY_KEY_ID_TEST = 'rzp_test_Sh4tdflR7VHLCl'
RAZORPAY_KEY_ID_LIVE = 'rzp_live_Svwpu3AEgbK6V6'
const DELIVERY_CHARGE = 99
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

  const checkoutData = get_checkoutData()

  // 1️⃣ Create order from backend

  const result = await createOrder(checkoutData)

  if (result.status === 'failed') {
    alert(`Error creating order: ${result.error}`)
    console.log('Error creating Order:', result)
    return
  } else if (result.amount !== checkoutData.totals.grand_total) {
    alert(`Order amount mismatch. Please contact support.`)
    console.log('Order amount mismatch', result)
    return
  } else {
    checkoutData.paymentData = {
      order_id: result.order_id,
      key: result.key,
    }
  }

  $('#place_order_btn').prop('disabled', true)

  const params = get_orderParams(checkoutData)
  console.log('Razorpay Options:', params)

  // 2️⃣ Open Razorpay checkout
  const rzp = new Razorpay(params)
  rzp.open()
}

function get_checkoutData() {
  const cart = getCart()

  let itemsTotal = 0
  let qty = 0

  cart.forEach((item) => {
    itemsTotal += item.Price * item.qty * 100 //total in paise
    qty += item.qty
  })

  let deliveryCharge = DELIVERY_CHARGE * 100 //in paise

  if (itemsTotal / 100 >= FREE_DELIVERY_THRESHOLD) {
    deliveryCharge = 0
  }

  const checkoutData = {
    cart: cart,
    totals: {
      items_total: itemsTotal,
      delivery_charge: deliveryCharge,
      grand_total: itemsTotal + deliveryCharge,
      quantity: qty,
    },
    customer: {
      name: $('#name').val(),
      phone: $('#phone').val(),
      address: $('#address').val(),
      city: $('#city').val(),
      pincode: $('#pincode').val(),
      email: $('#email').val(),
    },
  }
  return checkoutData
}

async function createOrder(checkoutData) {
  const order = {
    method: 'POST',
    body: JSON.stringify({
      amount: checkoutData.totals.grand_total,
      receipt: Date.now(),
    }),
  }
  console.log('Razorpay Order:', order)
  try {
    const orderRes = await fetch('/create-order/', order)
    console.log('Razorpay Order creation response:', orderRes)

    if (orderRes.ok) {
      const result = await orderRes.json()
      console.log('Razorpay Order Data:', result)
      return result
    } else {
      result = {status: 'failed', error: 'Create Order response invalid'}
      return result
    }
  } catch (e) {
    alert(`Unable to contact Server`)
    console.log('Unbale to reach Server', e)
    result = {status: 'failed', error: 'Unable to contact Server'}
    return resultreturn
  }
}

function get_orderParams(checkoutData) {
  const params = {
    key: checkoutData.paymentData.key,
    amount: checkoutData.totals.grand_total, // Amount in paise
    currency: 'INR',
    name: 'ArtHQ',
    description: 'Order Payment',
    order_id: checkoutData.paymentData.order_id,

    handler: function (response) {
      order_callback(response, checkoutData)
    },

    prefill: {
      name: $('#name').val(),
      contact: $('#phone').val(),
    },
    notes: {
      customer_name: $('#name').val(),
      quantity: checkoutData.totals.quantity,
    },
    theme: {
      color: '#000',
    },
  }

  return params
}

async function order_callback(response, checkoutData) {
  if (!populatePaymentData(response, checkoutData)) {
    const result = await verifyPayment(checkoutData)
    showResult(result, checkoutData)
  }
}

function populatePaymentData(response, checkoutData) {
  if (response.razorpay_order_id !== checkoutData.paymentData.order_id) {
    alert('Order ID mismatch. Please contact support.')
    console.log('Order ID mismatch', response, checkoutData)
    return false
  }
  checkoutData.paymentData.gateway = 'razorpay'
  checkoutData.paymentData.transactionId = response.razorpay_payment_id
  checkoutData.paymentData.verificationToken = response.razorpay_signature
}

async function verifyPayment(checkoutData) {
  try {
    const verifyRes = await fetch('/verify-payment/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(checkoutData),
    })
    const result = await verifyRes.json()
    return result
  } catch (e) {
    console.log('Unable to verify payment', checkoutData)
    alert('Unable to verify payment. In case funds have been deited, the same will be refunded in 4-6 business days')
    return
  }
}

function showResult(result, checkoutData) {
  if (result.status === 'success') {
    console.log(`Payment ID : ${checkoutData.paymentData.transactionId} verified successfully`)

    // ✅ Remove only purchased items
    removePurchasedItems(checkoutData.cart)

    // 👉 Redirect to success page
    window.location.href = `/order-success/?order_id=${checkoutData.paymentData.order_id}`
  } else if (result.status === 'failed' && result.error === 'Failed to verify payment') {
    alert(`Payment ID : ${checkoutData.paymentData.transactionId} verification failed`)
  } else if (result.status === 'failed' && result.error === 'Failed to save order') {
    alert(`An error occurred while saving the order. Payment will be refunded in 5-6 business days.`)
  } else {
    alert(`An unexpected error occurred. Please contact support.`)
  }
}

/* INIT */
$(document).ready(function () {
  renderCheckout()
})

// BUTTON
$('#place_order_btn').on('click', function () {
  startPayment()
})
