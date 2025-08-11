var startLoad

var searchTextBoxExtened = false

$(window).on('load', onLoadFunction)

function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + '/navbar :page loading')
  $('#search_button').on('click', function (event) {
    tb_width = $('#search_textbox').width()
    if (tb_width < 25) {
      event.stopPropagation()
      extendSearchTextBox()
    } else {
      search()
    }
  })
  //$('#search_textbox').on('mousedown', extendSearchTextBox)
  $('#search_textbox').on('touchstart', extendSearchTextBox)
  $('#search_textbox').on('keydown', function (event) {
    if (event.keyCode == 13) {
      search()
    }
  })
}

function extendSearchTextBox() {
  console.log('extend called')
  $(document).on('click', function (event) {
    if (event.target.id != 'search_textbox') {
      event.preventDefault()
      reduceSearchTextBox()
    }
  })
  $('img').addClass('click_disabled')
  $('#navbar_div').addClass('expanded')
  $('#search_textbox').focus()
  console.log('search textbox extended')
}

function reduceSearchTextBox() {
  console.log('reduce called')
  $(document).off('click')
  $('img').removeClass('click_disabled')
  $('#navbar_div').removeClass('expanded')
  console.log('search textbox reduced')
}

function search() {
  var text = $('#search_textbox')[0].value
  if (text != '') {
    sessionStorage.setItem('searchText', $('#search_textbox')[0].value)
    port = '8000'
    currURL = window.location.href
    baseURL = currURL.split(port + '/')[0] + port + '/'
    products_gridURL = baseURL + '/products'
    window.location.href = products_gridURL
  }
}
