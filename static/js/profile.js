$(document).ready(function () {
  loadProfile()
})

$('#save_profile_btn').on('click', updateProfile)

async function loadProfile() {
  try {
    const response = await fetch('/user/profile/')
    const result = await response.json()
    if (result.status === 'failed') {
      alert(result.error)
      window.location.href = '/login/'
      return
    }

    populateProfile(result)
  } catch (e) {
    console.error(e)
    alert('Unable to load profile.')
  }
}

function populateProfile(result) {
  $('#username').val(result.username)
  $('#first_name').val(result.first_name)
  $('#last_name').val(result.last_name)
  $('#email').val(result.email)
  $('#phone').val(result.phone)
  $('#address').val(result.address)
  $('#city').val(result.city)
  $('#state').val(result.state)
  $('#pincode').val(result.pincode)
}

async function updateProfile() {
  const data = {
    first_name: $('#first_name').val().trim(),
    last_name: $('#last_name').val().trim(),
    email: $('#email').val().trim(),
    phone: $('#phone').val().trim(),
    address: $('#address').val().trim(),
    city: $('#city').val().trim(),
    state: $('#state').val().trim(),
    pincode: $('#pincode').val().trim(),
  }
  $('#save_profile_btn').prop('disabled', true)
  try {
    const response = await fetch('/user/update-profile/', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(data),
    })

    const result = await response.json()
    if (result.status === 'success') {
      alert('Profile updated successfully.')
    } else {
      alert(result.error)
    }
  } catch (e) {
    console.error(e)
    alert('Unable to update profile.')
  } finally {
    $('#save_profile_btn').prop('disabled', false)
  }
}
