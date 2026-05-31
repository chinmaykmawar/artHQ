$('#track_order_btn').on('click', fetchOrders)

async function fetchOrders() {
  const orderIds = $('#order_ids').val().trim()

  const phone = $('#phone').val().trim()

  const response = await fetch('/get-orders/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      action: 'get_orders',
      order_ids: orderIds,
      phone: phone,
    }),
  })

  const orders = await response.json()

  renderOrders(orders)
}

function renderOrders(orders) {
  if (!orders.length) {
    $('#track_results').html('<p>No orders found.</p>')
    return
  }

  let html = ''

  orders.forEach((order) => {
    html += `
      <div class="order_card">

        <div class="order_card_row">
          <div class="order_card_label">Order ID</div>
          <div>${order.order_id}</div>
        </div>

        <div class="order_card_row">
          <div class="order_card_label">Products</div>
          <div>${order.order_summary}</div>
        </div>

        <div class="order_card_row">
          <div class="order_card_label">Amount</div>
          <div>₹${order.total_amount}</div>
        </div>

        <div class="order_card_row">
          <div class="order_card_label">Tracking</div>
          <div>${order.tracking_id}</div>
        </div>

      </div>
    `
  })

  $('#track_results').html(html)
}
