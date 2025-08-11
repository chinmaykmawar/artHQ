const allProductsURL = 'https://script.google.com/macros/s/AKfycbxYeGDrnh4Hl-MCrz3ySfmnJ0ZaSd9N30tAuff4HQ-U-eA0yfL6aCePTTPJGg4ybmOh/exec'
const searchURL = 'https://script.google.com/macros/s/AKfycbzgrqYsmy812tsMexwKFqxprXriMP75WSpEVScsDwQGrb85Ep5is-WRQtVu3SSrTUUXcw/exec' + '?searchText='

var filterInput

var startLoad
var startFilter
var startSort
var baseURL

port = '8000'
currURL = window.location.href
baseURL = currURL.split(port + '/')[0] + port + '/'
products_gridURL = baseURL + '/products'

$(window).on('load', onLoadFunction)

async function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + '/product_grid :page loading')

  $(document).on('click', function (event) {
    if ($('#filter_popup').hasClass('show')) {
      if ($(event.target)[0].id.split('_')[0] != 'filter') {
        event.preventDefault()
        $('#filter_form input').each(function () {
          this.checked = false
        })
        hideFilterPopup()
        console.log('filter Popup shown and click outside')
      }
    } else if ($('#sort_popup').hasClass('show')) {
      if ($(event.target)[0].id.split('_')[0] != 'sort') {
        event.preventDefault()
        $('#filter_form input').each(function () {
          this.checked = false
        })
        hideSortPopup()
        console.log('sort Popup shown and click outside')
      }
    }
  })

  $('#product_grid').html('Loading......')
  var displayedProducts = await getProducts(setFilterInputsfromSessionStorage())

  setFilterPopupOptions(displayedProducts)
  createDiv(displayedProducts)
  setResizeImageEH()
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + '/product_grid :page loaded')
}

async function getProducts(filterInput) {
  var productsJson

  if (filterInput['searchCriteria'] == '') {
    productsJson = await $.ajax(allProductsURL)
  } else {
    productsJson = await $.ajax(searchURL + filterInput['searchCriteria'])
    var currTime = new Date().getTime() - startLoad
    console.log(currTime + ': ajax executed with  ' + productsJson.length + ' products')
  }

  var filteredProducts = []
  filteredProducts = productsJson.filter(checkProductJSON)

  if (filterInput.sub_category.length != 0) {
    filteredProducts = productsJson.filter(checkProductJSON).filter((prod) => filterInput['sub_category'].includes(prod.Sub_Category))
  }
  //var currTime2 = (new Date().getTime()) - startLoad;
  //console.log(currTime2 + ": Returning filtered List with " + filteredProducts.length + " products");
  return filteredProducts
}

function checkProductJSON(product) {
  if (product.Product_ID != 'N/A' && product.Product_ID !== '') {
    return true
  }
  return false
}

function createDiv(products) {
  //var currTime = new Date().getTime() - startLoad;
  //console.log(currTime + ": entering createDiv. no of products:" + products.length);
  currURL = window.location.href
  baseURL = currURL.replace('/products', '')
  $('#product_grid').html('')
  $.each(products, function (i) {
    var id = products[i].Product_ID
    var category = getCategory(products[i].Sub_Category)
    var title = products[i].Title
    var price = products[i].Price

    var html =
      '<div id="' + id + '_div" class="Product ' + category + ' ' + products[i].Sub_Category + ' ' + products[i].Material + ' ' + products[i].Base_Color + '_Base ' + products[i].Highlight + '_Highlight"' + ' style="flex-direction: column;"><a href="' + baseURL + '/product/' + id + '"><img id="' + id + '" src="static/assets/Product_Images/grid_images/' + id + '.jpg" alt="Product Image"></a><div class="Product_title">' + title + '</div><div class="price row">&#8377;' + price + '</div></div></div>'
    $('#product_grid').append(html)
  })
  $('#image_size-medium').click()
  //var currTime = new Date().getTime() - startLoad;
  //console.log(currTime + ":  Exiting CreateDiv");
}

async function filterFormSubmit() {
  //startFilter = new Date().getTime();
  //console.log(startFilter + ": filter form submitted");

  hideFilterPopup()
  filterInput['sub_category'] = []

  $('#filter_form input').each(function () {
    if (this.checked) {
      filterInput['sub_category'].push(this.id.split('_')[2])
    }
  })
  $('#product_grid').html('Loading...')
  var displayedProducts = await getProducts(filterInput)
  createDiv(displayedProducts)
}

function setFilterInputsfromSessionStorage() {
  //var currTime = new Date().getTime() - startLoad
  //console.log(currTime + ':entering Set Filter')
  filterInput = {searchCriteria: '', sub_category: []}

  var filterType
  var filterText

  if (sessionStorage.getItem('filtertype') != null) {
    filterType = sessionStorage.getItem('filtertype')
    filterText = sessionStorage.getItem('filtertext')
    sessionStorage.removeItem('filtertext')
    sessionStorage.removeItem('filtertype')
    switch (filterType) {
      case 'category':
        filterText = getSubCategories(filterText)
        break
    }

    var currTime = new Date().getTime() - startLoad
    console.log(currTime + ': filter text fetched with length : ' + filterText.length)
    $.each(filterText, function () {
      var id = '#filter_checkbox_' + this
      $(id).prop('checked', true)
      var currTime = new Date().getTime() - startLoad
      console.log(currTime + ':' + id + ' checkbox checked ')
    })
    $('#filter_form input').each(function () {
      if (this.checked) {
        filterInput['sub_category'].push(this.id.split('_')[2])
      }
    })
  }

  if (sessionStorage.getItem('searchText') != null) {
    var searchText = sessionStorage.getItem('searchText')
    $('#search_textbox').val(searchText)
    filterInput['searchCriteria'] = searchText
    sessionStorage.removeItem('searchText')
  }
  return filterInput
}

function setFilterPopupOptions(sortedProducts) {
  divhtml = $('#filter_form').html()
  lookup = new Array()
  $.each(sortedProducts, function () {
    if ($.inArray(this.Sub_Category, lookup) < 0) {
      lookup.push(this.Sub_Category)
    }
  })
  $.each(lookup, function () {
    //var currTime = new Date().getTime() - startLoad
    //console.log(currTime + ':adding filter option for' + this)
    divhtml1 = '<div class="dropdown-item">\n'
    divhtml2 = '  <input class="" type="checkbox" id="filter_checkbox_' + this + '" />\n'
    divhtml3 = '  <label class="" for="filter_checkbox_' + this + '" id="filter_label_' + this + '">' + this + '</label>\n'
    divhtml4 = '</div>'
    divhtml = divhtml1 + divhtml2 + divhtml3 + divhtml4 + divhtml
  })
  $('#filter_form').html(divhtml)
  $('#filter_popup_button').on('click', showFilterPopup)
  $('#filter_button').on('click', filterFormSubmit)
  $('#clear_filter_button').on('click', clearFilter)
  $('#sort_popup_button').on('click', showSortPopup)
  $('#sort_button').on('click', sortFormSubmit)
}

function showFilterPopup() {
  $('#filter_popup').addClass('show')
  $('#filter_popup_button').addClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'none')
  $('#sort_popup_button').addClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'none')
}

function hideFilterPopup() {
  $('#filter_popup').removeClass('show')
  $('#filter_popup_button').removeClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'auto')
  $('#sort_popup_button').removeClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'auto')
}

function clearFilter() {
  $('#filter_form input').each(function () {
    this.checked = false
  })
  if (filterInput.searchCriteria != '' || filterInput.sub_category.length != 0) {
    filterInput = {searchCriteria: '', sub_category: []}
    hideFilterPopup()

    window.location.href = products_gridURL
  }else{
    hideFilterPopup()
  }
}

function showSortPopup() {
  $('#sort_popup').addClass('show')
  $('#filter_popup_button').addClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'none')
  $('#sort_popup_button').addClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'none')
}

function hideSortPopup() {
  $('#sort_popup').removeClass('show')
  $('#filter_popup_button').removeClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'auto')
  $('#sort_popup_button').removeClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'auto')
}

async function sortFormSubmit() {
  startSort = new Date().getTime()
  var currTime
  console.log(startSort + ': Sort Form Submitted')
  hideSortPopup()

  var filterInput = []
  $('#filter_form input').each(function () {
    if (this.checked) {
      filterInput.push(this.id.split('_')[2])
    }
  })
  currTime = new Date().getTime() - startSort
  console.log(currTime + ': Filter Input Length : ' + filterInput.length)

  var sortedProducts = await getProducts(filterInput)

  currTime = new Date().getTime() - startSort
  console.log(currTime + ': sorted Products received with length : ' + sortedProducts.length)

  var selector = $("input[name='sort_radio_button']:checked").val()
  var params = selector.match(/.{1,5}/g)

  currTime = new Date().getTime() - startSort
  console.log(currTime + ': params : ' + params)

  switch (params[0]) {
    case 'alpha':
      sortedProducts.sort(sortByProduct_ID)
      break
    case 'color':
      sortedProducts.sort(sortByColor)
      break
  }
  if (params[1] != 'asc') {
    sortedProducts = sortedProducts.reverse()
  }

  //currTime = new Date().getTime() - startSort;
  //console.log(currTime + ": exiting sortProducts. no of products:" + sortedProducts.length);

  createDiv(sortedProducts)
}

function sortByProduct_ID(a, b) {
  var aProp = a.Product_ID
  var bProp = b.Product_ID
  return aProp < bProp ? -1 : aProp > bProp ? 1 : 0
}

function sortByColor(a, b) {
  var aProp = a.Base_Color
  var bProp = b.Base_Color
  return aProp < bProp ? -1 : aProp > bProp ? 1 : 0
}

function getCategory(sc) {
  if (sc == 'Coasters' || sc == 'Candle Holders' || sc == 'Tray') {
    return 'Home_Decor'
  } else {
    return 'Jewellery'
  }
}

function getSubCategories(cat) {
  if (cat == 'Home Decor') {
    return ['Coasters', 'Candle_Holders', 'Tray', 'Containers']
  } else {
    return []
  }
}

function setResizeImageEH() {
  content_width = $('#main_content').width()
  if (content_width < 450) {
    $('#image_size-medium').on('click', function () {
      var width = ($('#product_grid').width() - parseInt($('#product_grid').css('column-gap').replace('px', ''))) / 2
      var height = ($(window).innerHeight() - $('#navbar_section').innerHeight() - $('#title_section').innerHeight() - $('#nav_section').innerHeight() - parseInt($('#product_grid').css('row-gap').replace('px', ''))) / 2
      resizeImages(width, height)
    })
    $('#image_size-large').on('click', function () {
      var width = $('#product_grid').width()
      var height = $(window).innerHeight() - $('#navbar_section').innerHeight() - $('#title_section').innerHeight() - $('#nav_section').innerHeight()
      resizeImages(width, height)
    })
  } else {
    $('#image_size-large').on('click', function () {
      resizeImages(210, (210 * 4) / 3)
    })
    $('#image_size-medium').on('click', function () {
      resizeImages(150, (150 * 4) / 3)
    })
    $('#image_size-small').removeClass('hidden')
    $('#image_size-small').on('click', function () {
      resizeImages(90, (90 * 4) / 3)
    })
  }

  $('#image_size-medium').click()
}

function resizeImages(width, height) {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ':entering set Image size for width -' + width)
  $('#product_grid').css('grid-template-columns', 'repeat(auto-fill, ' + width + 'px)')
  $('#product_grid img').each(function () {
    $(this).css('width', width)
    $(this).css('height', height)
  })
}
