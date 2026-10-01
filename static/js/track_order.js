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
  console.log(orders)
  if (orders.status === 'success') {
    renderOrders(orders.data)
  } else {
    $('#track_results').html('Unable to fetch orders. Please try again later.')
  }
}

function renderOrders(orders) {
  if (!orders.length) {
    $('#track_results').html('<p>No orders found.</p>')
    return
  }

  let html = `
    <div class="table_container">
    <table class="track_table">
        <thead>
            <tr>
                <th>Order ID</th>
                <th>Created</th>
                <th>Name</th>
                <th>Phone</th>
                <th>Address</th>
                <th>Products</th>
                <th>Amount</th>
                <th>Tracking</th>
            </tr>
        </thead>
        <tbody>`

  orders.forEach((order) => {
    html += `
        <tr>
            <td>${order.order_id}</td>
            <td>${order.created_at || '-'}</td>
            <td>${order.customer_name}</td>
            <td>${order.phone}</td>
            <td>${order.address}</td>
            <td>${order.order_summary}</td>
            <td>₹${order.total_amount}</td>
            <td>${order.tracking_id || '-'}</td>
        </tr>`
  })

  html += `
        </tbody>
    </table>
    </div>`

  $('#track_results').html(html)
}

function populateData() {
  const orderIds = JSON.parse(sessionStorage.getItem('order_IDs') || 'null')
  const phone = JSON.parse(sessionStorage.getItem('phone_number') || 'null')

  if (orderIds) {
    $('#order_ids').val(orderIds)
  } else if (phone) {
    $('#phone').val(phone)
  } else {
    return
  }
}

$(document).ready(function () {
  populateData()
})
