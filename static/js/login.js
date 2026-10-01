$('#login_btn').on('click', login)

$('#password').on('keypress', function (e) {
  if (e.key === 'Enter') {
    login()
  }
})

async function login() {
  const username = $('#username').val().trim()
  const password = $('#password').val()

  if (!username) {
    alert('Please enter Username')
    return
  }

  if (!password) {
    alert('Please enter Password')
    return
  }

  $('#login_btn').prop('disabled', true)

  try {
    const response = await fetch('/user/login/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username: username, password: password}),
    })

    const result = await response.json()

    if (result.status === 'success') {
      const params = new URLSearchParams(window.location.search)
      const next = params.get('next')
      window.location.href = next || '/'
    } else {
      alert(result.error)
      $('#password').val('').focus()
    }
  } catch (e) {
    console.error(e)
    alert('Unable to contact server.')
  } finally {
    $('#login_btn').prop('disabled', false)
  }
}
