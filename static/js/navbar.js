var startLoad

$(window).on('load', onLoadFunction)

function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + ':page loading')
  $('#search_button').on('click', search)
}

function search() {
  sessionStorage.setItem('searchText', $('#search_textbox')[0].value)
  port='8000'
  currURL = window.location.href
  baseURL=currURL.split(port+'/')[0]+port+'/'
  products_gridURL = baseURL + '/products'
  window.location.href = products_gridURL
}
