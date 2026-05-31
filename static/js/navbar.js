// var startLoad

// var port = '8000'
// var currURL = window.location.href
// var baseURL = currURL.split(port + '/')[0] + port + '/'
// var products_gridURL = baseURL + '/products'

$(document).ready(function () {
  setNavBarEventHandlers()
})

$(window).on('load', onLoadFunction)

function onLoadFunction() {
  startLoad = new Date().getTime()
  //console.log(startLoad + '/navbar :page loading')
  var searchtext = ''
  if (sessionStorage.getItem('filterAttributes')) {
    searchtext = JSON.parse(sessionStorage.getItem('filterAttributes')).search
  }

  if (searchtext !== '') {
    extendSearchTextBox(false)
    $('#search_textbox').val(searchtext)
    console.log('search textboxt loaded with text: ' + searchtext)
  }
}

function extendSearchTextBox(focus = true) {
  console.log('extend called')

  $('img').addClass('click_disabled')
  $('#navbar_div').addClass('expanded')
  if (focus) {
    $('#search_textbox').focus()
  }
  console.log('search textbox extended')
}

function reduceSearchTextBox() {
  console.log('reduce called')
  $(document).off('click')
  $('img').removeClass('click_disabled')
  $('#navbar_div').removeClass('expanded')
  console.log('search textbox reduced')
}

function searchTextUpdated(searchText) {
  filterAttributes = JSON.parse(sessionStorage.getItem('filterAttributes'))
  sessionStorage.setItem(
    'filterAttributes',
    JSON.stringify({Sub_Category: filterAttributes.Sub_Category, search: searchText})
  )
  if (searchText === '') {
    reduceSearchTextBox()
  }
  window.location.href = products_gridURL
}

function searchProductsFromSession(searchText) {
  const stored = sessionStorage.getItem('ALL_PRODUCTS')

  if (!stored) {
    console.error('❌ No products in sessionStorage')
    return []
  }

  const products = JSON.parse(stored)

  // 🔥 Clean + split search text
  const words = searchText
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '') // remove special chars
    .split(/\s+/)
    .filter(Boolean)

  // 🔥 Filter products
  const results = products.filter((product) => {
    const text = Object.values(product).join(' ').toLowerCase()

    return words.some((word) => text.includes(word)) // ANY match
  })

  return results
}

$('#viewcart_button').on('click', function (event) {
  event.stopPropagation()
  renderCart()
  openCart()
})

function setNavBarEventHandlers() {
  $('#search_button').on('click', function (event) {
    tb_width = $('#search_textbox').width()
    if (tb_width < 25) {
      event.stopPropagation()
      extendSearchTextBox(true)
      console.log('search textboxt extended from search button click')
    } else {
      searchTextUpdated($('#search_textbox').val())
    }
  })

  $('#search_textbox').on('touchstart', extendSearchTextBox)

  $('#search_textbox').keydown(function (event) {
    if (event.key === 'Enter') {
      searchTextUpdated($('#search_textbox').val())
    } else if (event.key === 'Escape') {
      $('#search_textbox').val('')
      searchTextUpdated('')
    }
  })

  $('#search_textbox').focusout(function () {
    searchTextUpdated($('#search_textbox').val())
  })

  $('#logo').on('click', function () {
    window.location.href = '/'
  })
}
