/* ===== CART SYSTEM ===== */

function getCart() {
  return JSON.parse(sessionStorage.getItem('CART') || '[]')
}

function saveCart(cart) {
  sessionStorage.setItem('CART', JSON.stringify(cart))
}

function addToCart(product) {
  let cart = getCart()

  const existing = cart.find((p) => p.Product_ID === product.Product_ID)

  if (existing) {
    existing.qty += 1
  } else {
    product.qty = 1
    cart.push(product)
  }

  saveCart(cart)
  renderCart()
  openCart()
}

/* ===== UI ===== */

function openCart() {
  $('#cart_drawer').addClass('active')
  $('#cart_overlay').addClass('active')
}

function closeCart() {
  $('#cart_drawer').removeClass('active')
  $('#cart_overlay').removeClass('active')
}

/* ===== RENDER ===== */

function renderCart() {
  const cart = getCart()
  $('#cart_items').html('')

  let total = 0

  cart.forEach((item) => {
    total += item.Price * item.qty

    const html = `
      <div class="cart_item">
        <img src="/static/assets/Product_Images/${item.Product_ID}/${item.Product_ID}_1.jpg">
        <div class="cart_item_details">
          <div>${item.Title}</div>
          <div>₹${item.Price}</div>
          <div class="qty_control">
            <button onclick="updateQty('${item.Product_ID}', -1)">-</button>
            ${item.qty}
            <button onclick="updateQty('${item.Product_ID}', 1)">+</button>
          </div>
        </div>
      </div>
    `
    $('#cart_items').append(html)
  })

  $('#cart_total_price').text('₹' + total)
  $('#cart_count').text(cart.length)
}

function updateQty(id, delta) {
  let cart = getCart()

  cart = cart
    .map((item) => {
      if (item.Product_ID === id) {
        item.qty += delta
      }
      return item
    })
    .filter((item) => item.qty > 0)

  saveCart(cart)
  renderCart()
}

$('#add_to_cart_btn').on('click', function () {
  const stored = JSON.parse(sessionStorage.getItem('ALL_PRODUCTS'))
  const product = stored.find((p) => p.Product_ID === product_id)

  addToCart(product)
})

$('#cart_overlay, #cart_back').on('click', closeCart)

$('#checkout_btn').on('click', function () {
  window.location.href = '/checkout'
})
