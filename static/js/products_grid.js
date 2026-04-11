const allProductsURL = 'https://script.google.com/macros/s/AKfycbw30Y_it1AKRYAZeuXPsFkoVw0Ku_sBLgvd-odIfU1wBy2eCoY75hPuMHTnYLsB3OxErw/exec'
const searchURL = 'https://script.google.com/macros/s/AKfycbwdWCAIweIvAWYJdS3O68gFFRXEYdMUhdPGjGxBMhRgl6bmWh40PhIyl6dwxGwHvA-yGQ/exec' + '?searchText='

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

//$(document).on('error', 'img', logFailedProdIDs)

async function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + '/product_grid :page loading')

  // attach once using jQuery (delegated)

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
  //var displayedProducts = await getProducts(setFilterInputsfromSessionStorage())
  var displayedProducts = await getFilteredProducts()

  setFilterPopupOptions(displayedProducts)
  createDiv(displayedProducts)
  setResizeImageEH()
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + '/product_grid :page loaded')
}

async function getFilteredProducts() {
  let productsJson

  // 🔥 1. Try sessionStorage first
  const stored = sessionStorage.getItem('ALL_PRODUCTS')

  if (stored) {
    productsJson = JSON.parse(stored)
    console.log('⚡ Loaded products from sessionStorage')
  } else {
    // 🔥 2. Fetch from API
    productsJson = await $.ajax(allProductsURL)

    // 🔥 3. Store in sessionStorage
    sessionStorage.setItem('ALL_PRODUCTS', JSON.stringify(productsJson))
    console.log('🌐 Fetched products from API')
  }

  // 🔥 4. Get filters
  const filterInput = setFilterInputsfromSessionStorage()

  let filteredProducts = productsJson

  // 🔥 5. Apply search filter
  if (filterInput.searchCriteria) {
    const words = filterInput.searchCriteria
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .split(/\s+/)
      .filter(Boolean)

    filteredProducts = filteredProducts.filter((product) => {
      const text = Object.values(product).join(' ').toLowerCase()
      return words.some((word) => text.includes(word))
    })
  }

  // 🔥 6. Apply sub_category filter
  if (filterInput.sub_category.length > 0) {
    filteredProducts = filteredProducts.filter((product) => filterInput.sub_category.includes(product.Sub_Category))
  }

  console.log(`✅ Returning ${filteredProducts.length} products`)

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

    var openingDiv = '<div id="' + id + '_div"'

    var class_html = 'class="Product ' + category + ' ' + products[i].Sub_Category + ' ' + products[i].Material + ' ' + products[i].Base_Color + '_Base ' + products[i].Highlight + '_Highlight"'
    var style_html = ' style="flex-direction: column;">'
    var a_html = '<a href="' + baseURL + '/product/' + id + '">'
    var img_html = '<img id="' + id + '" src="static/assets/Product_Images/' + id + '/' + id + '_1.jpg" alt="Product Image"></a>'
    var title_html = '<div class="Product_title">' + title + '</div>'
    var price_html = '<div class="price row">&#8377;' + price + '</div></div></div>'
    var html = openingDiv + ' ' + class_html + ' ' + style_html + a_html + img_html + title_html + price_html
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
  } else {
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
