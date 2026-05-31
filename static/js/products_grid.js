const allProductsURL =
  'https://script.google.com/macros/s/AKfycbx7XwBXljynHLRc3PtAkItuW2WSDN0jwr1gQHw7k0tC2PP3GkR3XVll4gHbynQTs0p-/exec'
const searchURL =
  'https://script.google.com/macros/s/AKfycbwdWCAIweIvAWYJdS3O68gFFRXEYdMUhdPGjGxBMhRgl6bmWh40PhIyl6dwxGwHvA-yGQ/exec' +
  '?searchText='

let startLoad
let allProducts
let filteredProducts

let Category_dict = {}
let filterAttributes = {
  Sub_Category: [],
  search: '',
}

let sortingAttributes

const port = '8000'
const currURL = window.location.href
const baseURL = currURL.replace('/products', '')
const products_gridURL = baseURL + '/products'

$(window).on('load', onLoadFunction)

///////////////////////////////////////////////////////////////////
/////////////////////////On Load Functions/////////////////////////
///////////////////////////////////////////////////////////////////

async function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + '/product_grid : entering onLoad Function')

  $('#product_grid').html('Loading......')
  allProducts = await getAllProducts()
  updateFilterAttributes([], '')
  filteredProducts = getFilteredProducts(allProducts, filterAttributes)
  setFilterPopupOptions(allProducts, filterAttributes)
  renderCategoryButtons(allProducts)
  displayProducts(filteredProducts)

  endLoad = new Date().getTime()
  console.log(endLoad + '/product_grid : exiting onLoad Function')
  console.log('Time taken to load product grid : ' + (endLoad - startLoad) / 1000 + ' seconds')
  setProductPageEventHandlers()
}

async function getAllProducts() {
  let productsJson

  const stored = sessionStorage.getItem('ALL_PRODUCTS')

  if (stored) {
    shuffled_productsJson = JSON.parse(stored)
    console.log('⚡ Loaded products from sessionStorage')
  } else {
    productsJson = await $.ajax(allProductsURL)
    shuffled_productsJson = shuffleArray(productsJson) // Shuffle products to ensure different order on each load, showcasing more products on the top

    sessionStorage.setItem('ALL_PRODUCTS', JSON.stringify(shuffled_productsJson))
    console.log('🌐 Fetched products from API')
  }
  return shuffled_productsJson
}

function getFilteredProducts(filteredProducts, filterAttributes) {
  if (filterAttributes.search !== '' && filterAttributes.search.trim() !== '') {
    const words = filterAttributes.search
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .split(/\s+/)
      .filter(Boolean)

    filteredProducts = filteredProducts.filter((product) => {
      const text = Object.values(product).join(' ').toLowerCase()
      return words.some((word) => text.includes(word))
    })
  }

  if (filterAttributes.Sub_Category.length > 0) {
    filteredProducts = filteredProducts.filter((product) =>
      filterAttributes.Sub_Category.includes(product.Sub_Category)
    )
  }

  console.log(`✅ Returning ${filteredProducts.length} products`)

  return filteredProducts
}

function setFilterPopupOptions(allProducts, filterAttributes) {
  var lookup = []
  $.each(allProducts, function () {
    if ($.inArray(this.Sub_Category, lookup) < 0) {
      lookup.push(this.Sub_Category)
    }
  })
  filter_options_html = ''

  $.each(lookup, function () {
    filter_options_html += '<div class="dropdown-item">\n'
    filter_options_html +=
      '  <input class="" type="checkbox" id="filter_checkbox_' + this + '" />\n'
    filter_options_html +=
      '  <label class="" for="filter_checkbox_' +
      this +
      '" id="filter_label_' +
      this +
      '">' +
      this +
      '</label>\n'
    filter_options_html += '</div>'
  })
  $('#filter_options_div').html(filter_options_html)

  if (filterAttributes.Sub_Category.length > 0) {
    filterAttributes.Sub_Category.forEach(function (subCategory) {
      $('#filter_checkbox_' + subCategory).prop('checked', true)
    })
  }
  $('#search_textbox').val(filterAttributes.search)
}

function displayProducts(products) {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering displayProducts. no of products:' + products.length)
  var currURL = window.location.href
  var baseURL = currURL.replace('/products', '')
  $('#product_grid').html('')

  ignored_products = [
    'HCo01BlG',
    'JER10002PiG',
    'JER30001Pin',
    'JNK20001Pin',
    'JBR30001BlW',
    'JER10002ReG',
    'JER10006PiG',
  ]

  $.each(products, function (i) {
    if (ignored_products.includes(products[i].Product_ID)) {
      return true // Skip this iteration
    }
    var id = products[i].Product_ID
    var category = getCategory(products[i].Sub_Category)
    var title = products[i].Title
    var price = products[i].Price

    var openingDiv = '<div id="' + id + '_div"'

    var class_html =
      'class="Product ' +
      category +
      ' ' +
      products[i].Sub_Category +
      ' ' +
      products[i].Material +
      ' ' +
      products[i].Base_Color +
      '_Base ' +
      products[i].Highlight +
      '_Highlight"'
    var style_html = ' style="flex-direction: column;">'
    var a_html = '<a href="' + baseURL + '/product/' + id + '">'
    var img_html =
      '<img id="' +
      id +
      '" src="/static/assets/Product_Images/' +
      id +
      '/' +
      id +
      '_1.jpg" alt="Product Image"></a>'
    var title_html = '<div class="Product_title">' + title + '</div>'
    var price_html = '<div class="price row">&#8377;' + price + '</div></div></div>'
    var html =
      openingDiv + ' ' + class_html + ' ' + style_html + a_html + img_html + title_html + price_html
    $('#product_grid').append(html)
  })
  $('#image_size-medium').click()
  //var currTime = new Date().getTime() - startLoad;
  //console.log(currTime + ":  Exiting CreateDiv");
}

///////////////////////////////////////////////////////////////////
/////////////////////////Filter Functions//////////////////////////
///////////////////////////////////////////////////////////////////

function filterFormSubmit() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering filterFormSubmit')

  hideFilterPopup()
  selected_Categories = []

  $('#filter_form input').each(function () {
    if (this.checked) {
      selected_Categories.push(this.id.split('_')[2])
    }
  })

  $('#product_grid').html('Loading...')
  updateFilterAttributes(selected_Categories, filterAttributes.search)
  filteredProducts = getFilteredProducts(allProducts, filterAttributes)
  setFilterPopupOptions(allProducts, filterAttributes)
  displayProducts(filteredProducts)
}

function updateFilterAttributes(Sub_Categories, searchText, forcedUpdate = false) {
  if (forcedUpdate) {
    filterAttributes.Sub_Category = Sub_Categories
    filterAttributes.search = searchText
    sessionStorage.setItem('filterAttributes', JSON.stringify(filterAttributes))
    return
  }

  var savedFilterAttributes = sessionStorage.getItem('filterAttributes')

  if (savedFilterAttributes !== null && savedFilterAttributes.trim() !== '') {
    filterAttributes = JSON.parse(savedFilterAttributes)
  } else {
    filterAttributes = {
      Sub_Category: [],
      search: '',
    }
  }

  if (Array.isArray(Sub_Categories) && Sub_Categories.length > 0) {
    filterAttributes.Sub_Category = Sub_Categories
  }

  console.log('Sub_Category filter:' + filterAttributes.Sub_Category.join(', '))

  if (typeof searchText === 'string') {
    filterAttributes.search = searchText
  }
  console.log('search filter:' + filterAttributes.search)

  sessionStorage.setItem('filterAttributes', JSON.stringify(filterAttributes))
}

function showFilterPopup() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering showFilterPopup')
  $('#filter_popup').addClass('show')
  $('#filter_popup_button').addClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'none')
  $('#sort_popup_button').addClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'none')
}

function hideFilterPopup() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering hideFilterPopup')
  $('#filter_popup').removeClass('show')
  $('#filter_popup_button').removeClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'auto')
  $('#sort_popup_button').removeClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'auto')
}

function clearFilter() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering clearFilter')

  $('#filter_form input').each(function () {
    this.checked = false
  })

  filterAttributes = {
    Sub_Category: [],
    search: filterAttributes.search, // Retain the search text while clearing filters
  }
  sessionStorage.setItem('filterAttributes', JSON.stringify(filterAttributes))
  filteredProducts = getFilteredProducts(allProducts, filterAttributes)
  setFilterPopupOptions(allProducts, filterAttributes)
  displayProducts(filteredProducts)
}

function clickOutsideFilterPopup(event) {
  event.preventDefault()
  $('#filter_form input').each(function () {
    this.checked = false
  })

  if (filterAttributes.Sub_Category.length > 0) {
    filterAttributes.Sub_Category.forEach(function (subCategory) {
      $('#filter_checkbox_' + subCategory).prop('checked', true)
    })
  }

  hideFilterPopup()

  console.log('filter Popup shown and click outside')
}

///////////////////////////////////////////////////////////////////
/////////////////////////Sorting Functions/////////////////////////
///////////////////////////////////////////////////////////////////

function showSortPopup() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering showSortPopup')
  $('#sort_popup').addClass('show')
  $('#filter_popup_button').addClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'none')
  $('#sort_popup_button').addClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'none')
}

function hideSortPopup() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering hideSortPopup')
  $('#sort_popup').removeClass('show')
  $('#filter_popup_button').removeClass('button_disabled')
  $('#filter_popup_button').css('pointer-events', 'auto')
  $('#sort_popup_button').removeClass('button_disabled')
  $('#sort_popup_button').css('pointer-events', 'auto')
}

function sortFormSubmit() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering sortFormSubmit')

  hideSortPopup()

  var selector = $("input[name='sort_radio_button']:checked").val()
  var params = selector.match(/.{1,5}/g)

  //currTime = new Date().getTime() - startSort
  //console.log(currTime + ': params : ' + params)

  switch (params[0]) {
    case 'alpha':
      filteredProducts.sort(sortByProduct_ID)
      break
    case 'color':
      filteredProducts.sort(sortByColor)
      break
  }
  if (params[1] != 'asc') {
    filteredProducts = filteredProducts.reverse()
  }

  //currTime = new Date().getTime() - startSort;
  //console.log(currTime + ": exiting sortProducts. no of products:" + filteredProducts.length);

  displayProducts(filteredProducts)
}

function clickOutsideSortPopup(event) {
  event.preventDefault()
  hideSortPopup()
  console.log('sort Popup shown and click outside')
}

function sortByProduct_ID(a, b) {
  return a.Product_ID < b.Product_ID ? -1 : a.Product_ID > b.Product_ID ? 1 : 0
}

function sortByColor(a, b) {
  return a.Base_Color < b.Base_Color ? -1 : a.Base_Color > b.Base_Color ? 1 : 0
}

///////////////////////////////////////////////////////////////////
/////////////////////////Helper and UI Functions///////////////////
///////////////////////////////////////////////////////////////////

function getCategory(sc) {
  //var currTime = new Date().getTime() - startLoad
  //console.log(currTime + ': entering getCategory')

  if (sc == 'Coasters' || sc == 'Candle Holders' || sc == 'Tray') {
    return 'Home_Decor'
  } else {
    return 'Jewellery'
  }
}

function getSubCategories(cat, allProducts) {
  subCategories = []
  allProducts.forEach((p) => {
    if (getCategory(p.Sub_Category) == cat && !subCategories.includes(p.Sub_Category)) {
      subCategories.push(p.Sub_Category)
    }
  })
  return subCategories
}

function resizeImages(width, height) {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ':entering resizeImages for width -' + width)

  $('#product_grid').css('grid-template-columns', 'repeat(auto-fill, ' + width + 'px)')
  $('#product_grid img').each(function () {
    $(this).css('width', width)
    $(this).css('height', height)
  })
}

function renderCategoryButtons(products) {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering renderCategoryButtons')

  products.forEach((p) => {
    const cat = getCategory(p.Sub_Category)
    if (!Category_dict[cat]) {
      Category_dict[cat] = []
    }
    if (!Category_dict[cat].includes(p.Sub_Category)) {
      Category_dict[cat].push(p.Sub_Category)
    }
  })
  sessionStorage.setItem('Category_dict', JSON.stringify(Category_dict))

  $('#category_buttons_div').html('')

  $('#category_buttons_div').append(`<div class="category_btn active" data-cat="ALL">ALL</div>`)

  Object.keys(Category_dict).forEach((cat) => {
    $('#category_buttons_div').append(
      `<div class="category_btn" data-cat="${cat}">${cat.replace('_', ' ').toUpperCase()}</div>`
    )
  })

  $('.category_btn').on('click', function () {
    $('.category_btn').removeClass('active')
    $(this).addClass('active')
    var selected_Sub_Categories
    var selected_Category = [$(this).data('cat')]
    if (selected_Category[0] == 'ALL') {
      selected_Sub_Categories = []
    } else {
      selected_Sub_Categories = Category_dict[selected_Category[0]]
    }

    updateFilterAttributes(selected_Sub_Categories, filterAttributes.search, true)
    filteredProducts = getFilteredProducts(allProducts, filterAttributes)
    setFilterPopupOptions(allProducts, filterAttributes)
    displayProducts(filteredProducts)
  })
}

function shuffleArray(array) {
  newarray = []
  l = array.length
  for (let i = 0; i < l; i++) {
    idx = Math.floor(Math.random() * array.length)
    newarray.push(array[idx])
    array.splice(idx, 1)
  }
  return newarray
}

///////////////////////////////////////////////////////////////////
/////////////////////////Event Handlers///////////////////////////
///////////////////////////////////////////////////////////////////

function setProductPageEventHandlers() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering setProductPageEventHandlers')

  $(document).on('click', function (event) {
    if ($('#filter_popup').hasClass('show') && $(event.target)[0].id.split('_')[0] != 'filter') {
      clickOutsideFilterPopup(event)
    } else if ($('#sort_popup').hasClass('show') && $(event.target)[0].id.split('_')[0] != 'sort') {
      clickOutsideSortPopup(event)
    }
  })

  content_width = $('#main_content').width()
  if (content_width < 450) {
    $('#image_size-medium').on('click', function () {
      var width =
        ($('#product_grid').width() -
          parseInt($('#product_grid').css('column-gap').replace('px', ''))) /
        2
      var height =
        ($(window).innerHeight() -
          $('#navbar_section').innerHeight() -
          $('#title_section').innerHeight() -
          $('#nav_section').innerHeight() -
          parseInt($('#product_grid').css('row-gap').replace('px', ''))) /
        2
      resizeImages(width, height)
    })
    $('#image_size-large').on('click', function () {
      var width = $('#product_grid').width()
      var height =
        $(window).innerHeight() -
        $('#navbar_section').innerHeight() -
        $('#title_section').innerHeight() -
        $('#nav_section').innerHeight()
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

  $('#filter_popup_button').on('click', showFilterPopup)
  $('#filter_button').on('click', filterFormSubmit)
  $('#clear_filter_button').on('click', clearFilter)
  $('#sort_popup_button').on('click', showSortPopup)
  $('#sort_button').on('click', sortFormSubmit)

  $('#image_size-medium').click()
}
