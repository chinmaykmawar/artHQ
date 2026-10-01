/* ============================================================
   ArtHQ Integration Tests
   ============================================================ */

const TEST_PRODUCT = {
  Product_ID: 'HCo01BlS',
  Title: 'Coasters',
  Description: 'Coasters',
  Price: 499,
  qty: 1,
}

const TEST_CUSTOMER = {
  name: 'Integration Test',
  phone: '9999999999',
  email: 'integration@test.com',
  address: 'ArtHQ Test Address',
  city: 'Delhi',
  pincode: '110001',
}

let createdOrderId = null

/* ============================================================
   Products API
   ============================================================ */

async function testGetProducts() {
  console.log('Testing get_all_products...')
  const response = await fetch('/get-all-products/')
  console.assert(response.ok, 'Products API failed')
  const products = await response.json().data
  console.assert(Array.isArray(products), 'Products should be array')
  console.assert(products.length > 0, 'No products returned')

  const p = products[0]
  ;['Product_ID', 'Title', 'Price', 'Description', 'Sub_Category', 'Base_Color', 'Highlight', 'Design'].forEach((key) => {
    console.assert(key in p, `Missing ${key}`)
  })
  console.log('✓ get_all_products passed')
  console.table(products.slice(0, 5))
  return products
}

/* ============================================================
   Create Razorpay Order
   ============================================================ */

async function testCreateOrder() {
  console.log('Testing create_order...')
  const amount = TEST_PRODUCT.Price * 100 + 9900
  const response = await fetch('/create-order/', {
    method: 'POST',
    body: JSON.stringify({
      amount: amount,
      receipt: Date.now(),
    }),
  })

  console.assert(response.ok, 'Create order failed')

  const result = await response.json()
  console.assert(result.status === 'success', 'Order creation failed')

  createdOrderId = result.data.order_id
  console.log('✓ create_order passed')
  console.log(result)
  return result
}

/* ============================================================
   Get Orders
   ============================================================ */

async function testGetOrders(phone = TEST_CUSTOMER.phone) {
  console.log('Testing get_orders...')
  const response = await fetch('/get-orders/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      action: 'get_orders',
      order_ids: '',
      phone: phone,
    }),
  })
  console.assert(response.ok)

  const orders = await response.json().data
  console.log(orders)
  console.assert(Array.isArray(orders), 'Orders should be array')
  console.log('✓ get_orders passed')
  return orders
}

async function testGetOrders_withflow(phone = TEST_CUSTOMER.phone) {
  console.log('Testing get_orders...')
  sessionStorage.setItem('phone_number', phone)
  window.location.href = 'track-order/'
}

/* ============================================================
   Manual Checkout Test
   ============================================================ */

async function runCheckoutTest() {
  console.clear()
  console.log('Preparing checkout test...')

  // Clear any previous data
  sessionStorage.removeItem('CHECKOUT')
  sessionStorage.removeItem('CART')

  // Put one product in cart
  sessionStorage.setItem(
    'CART',
    JSON.stringify([
      {
        Product_ID: 'JBR30002GrP',
        Title: 'Bracelet',
        Description: 'Bracelet',
        Price: 499,
        qty: 1,
      },
    ])
  )
  address = 'ArtHQ Test Address' + String(new Date().getTime())

  sessionStorage.setItem(
    'CUSTOMER_DETAILS',
    JSON.stringify({
      name: 'Integration Test',
      phone: '9999999999',
      email: 'integration@test.com',
      address: address,
      city: 'Delhi',
      pincode: '110001',
    })
  )

  console.log('Cart populated.')

  console.log('Opening checkout page...')

  // Open checkout page in same tab
  window.location.href = '/checkout/'
}

/* ============================================================
   Automated Tests
   ============================================================ */

async function runApiTests() {
  console.clear()
  console.log('========== API TESTS ==========')
  await testGetProducts()
  await testCreateOrder()
  await testGetOrders()
  console.log('✓ API tests completed')
}
