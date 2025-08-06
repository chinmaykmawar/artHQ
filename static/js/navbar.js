var startLoad

$(window).on('load', onLoadFunction)

function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + '/navbar :page loading')
  $('#search_button').on('click', search)
  $('#search_textbox').on('keydown', function(e){
    if(e.keyCode==13){
      search()
    }
  })
}

function search() {
  sessionStorage.setItem('searchText', $('#search_textbox')[0].value)
  port='8000'
  currURL = window.location.href
  baseURL=currURL.split(port+'/')[0]+port+'/'
  products_gridURL = baseURL + '/products'
  window.location.href = products_gridURL
}
