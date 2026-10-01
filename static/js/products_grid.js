let allProducts
let allProductDict = {}
let filteredProducts = []
let imageTsfs = {
  width: 150,
  height: 200,
}
let sortingAttributes
let Category_dict = {
  Jewellery: ['Bracelet', 'Container', 'Earrings', 'Keychain', 'Necklace', 'Set'],
  'Home Decor': ['Candle Holders', 'Coasters', 'Tray'],
}
let filterAttributes = {
  Sub_Category: null,
  search: '',
}

const port = '8000'
const currURL = window.location.href
const baseURL = currURL.replace('/products', '')
const products_gridURL = baseURL + '/products'

let startLoad

$(window).on('load', onLoadFunction)

///////////////////////////////////////////////////////////////////
/////////////////////////On Load Functions/////////////////////////
///////////////////////////////////////////////////////////////////

async function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + '/product_grid : entering onLoad Function')

  $('#product_grid').html('Loading......')
  await getAllProducts()
  setInitFilterAttributes()
  setFilteredProducts()
  setFilterPopupOptions()
  renderCategoryButtons()
  if ($('#main_content').width() < 450) {
    setImageDimentions(2)
  } else {
    imageTsfs.width = Math.ceil(150)
    imageTsfs.height = Math.ceil((150 * 4) / 3)
  }
  displayProducts()

  endLoad = new Date().getTime()
  console.log(endLoad + '/product_grid : exiting onLoad Function')
  console.log('Time taken to load product grid : ' + (endLoad - startLoad) / 1000 + ' seconds')
  setProductPageEventHandlers()
}

async function getAllProducts() {
  let productsJson
  const storedData = sessionStorage.getItem('ALL_PRODUCTS')
  if (storedData) {
    allProducts = JSON.parse(storedData)
    console.log('⚡ Loaded products from sessionStorage')
  } else {
    productsJson = await $.ajax('get-all-products/n')
    allProducts = shuffleArray(productsJson.data) // Shuffle products to ensure different order on each load, showcasing more products on the top

    sessionStorage.setItem('ALL_PRODUCTS', JSON.stringify(allProducts))
    console.log('🌐 Fetched products from API')
  }
  allProducts.forEach(function (product) {
    allProductDict[product.Product_ID] = product
  })
}

function displayProducts() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering displayProducts. no of products:' + filteredProducts.length)
  var currURL = window.location.href
  var baseURL = currURL.replace('/products', '')
  $('#product_grid').html('')

  //ignored_products = ['HCo01BlG', 'JER10002PiG', 'JER30001Pin', 'JNK20001Pin', 'JBR30001BlW', 'JER10002ReG', 'JER10006PiG']
  var img_common_html = '<img src="https://res.cloudinary.com/guixlbdm/image/upload/'

  $.each(filteredProducts, function (i) {
    var id = filteredProducts[i].Product_ID
    var category = getCategory(filteredProducts[i].Sub_Category)
    var title = filteredProducts[i].Title
    var price = filteredProducts[i].Price

    var openingDiv = '<div id="' + id + '_div"'

    var class_html =
      'class="Product ' +
      category +
      ' ' +
      filteredProducts[i].Sub_Category +
      ' ' +
      filteredProducts[i].Material +
      ' ' +
      filteredProducts[i].Base_Color +
      '_Base ' +
      filteredProducts[i].Highlight +
      '_Highlight"'

    var style_html = ' style="flex-direction: column;">'

    var a_html = '<a href="' + baseURL + '/product/' + id + '">'
    var img_format_html = 'c_auto,h_' + imageTsfs.height + ',w_' + imageTsfs.width
    var img_specific_html = '/' + filteredProducts[i].images[0] + '"></a>'
    var img_html = img_common_html + img_format_html + img_specific_html
    var title_html = '<div class="Product_title">' + title + '</div>'
    var price_html = '<div class="price row">&#8377;' + price + '</div></div></div>'
    var html = openingDiv + ' ' + class_html + ' ' + style_html + a_html + img_html + title_html + price_html
    $('#product_grid').append(html)
  })
  $('#product_grid').css('grid-template-columns', 'repeat(auto-fill, ' + imageTsfs.width + 'px)')
  //$('#image_size-medium').click()
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
  updateFilterSubCategories(selected_Categories)
}

function updateFilterSubCategories(subCategories) {
  if (Array.isArray(subCategories)) {
    filterAttributes.Sub_Category = subCategories
  }
  sessionStorage.setItem('filterAttributes', JSON.stringify(filterAttributes))
  console.log('Sub_Category filter: ' + filterAttributes.Sub_Category)
  setFilteredProducts()
  setFilterPopupOptions()
  displayProducts()
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

  updateFilterSubCategories([...new Set(allProducts.map((product) => product.Sub_Category))])
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

function setFilteredProducts() {
  filteredProducts = allProducts
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
  // console.log(
  //   'Sub_Category value:',
  //   filterAttributes.Sub_Category,
  //   'type:',
  //   typeof filterAttributes.Sub_Category,
  //   'isArray:',
  //   Array.isArray(filterAttributes.Sub_Category),
  //   'length:',
  //   filterAttributes.Sub_Category?.length
  // )
  if (filterAttributes.Sub_Category != null) {
    filteredProducts = filteredProducts.filter((product) => filterAttributes.Sub_Category.includes(product.Sub_Category))
  }

  console.log(`✅ Returning ${filteredProducts.length} products`)
}

function setFilterPopupOptions() {
  var subCategories = [...new Set(allProducts.map((product) => product.Sub_Category))]
  filter_options_html = ''
  $.each(subCategories, function () {
    filter_options_html += '<div class="dropdown-item">\n'
    filter_options_html += '  <input class="" type="checkbox" id="filter_checkbox_' + this + '" />\n'
    filter_options_html += '  <label class="" for="filter_checkbox_' + this + '" id="filter_label_' + this + '">' + this + '</label>\n'
    filter_options_html += '</div>'
  })
  $('#filter_options_div').html(filter_options_html)
  if (filterAttributes.Sub_Category != null) {
    if (filterAttributes.Sub_Category.length > 0) {
      filterAttributes.Sub_Category.forEach(function (subCategory) {
        $('#filter_checkbox_' + subCategory).prop('checked', true)
      })
    }
  }
  $('#search_textbox').val(filterAttributes.search)
}

function setInitFilterAttributes() {
  const savedFilterAttributes = sessionStorage.getItem('filterAttributes')
  if (savedFilterAttributes) {
    filterAttributes = JSON.parse(savedFilterAttributes)
  } else {
    filterAttributes.Sub_Category = [...new Set(allProducts.map((product) => product.Sub_Category))]
    filterAttributes.search = ''
  }
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
    case 'price':
      filteredProducts.sort(sortByPrice)
      break
  }
  if (params[1] != 'asc') {
    filteredProducts = filteredProducts.reverse()
  }
  //currTime = new Date().getTime() - startSort;
  //console.log(currTime + ": exiting sortProducts. no of products:" + filteredProducts.length);
  displayProducts()
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

function sortByPrice(a, b) {
  return a.Price < b.Price ? -1 : a.Price > b.Price ? 1 : 0
}

///////////////////////////////////////////////////////////////////
/////////////////////////Helper and UI Functions///////////////////
///////////////////////////////////////////////////////////////////

function getCategory(subCategory) {
  var category = null

  $.each(Category_dict, function (key, values) {
    if (values.includes(subCategory)) {
      category = key
      return false // break $.each()
    }
  })
  return category
}

function getSubCategories(cat) {
  var subCategories = []
  allProducts.forEach((p) => {
    if (getCategory(p.Sub_Category) == cat && !subCategories.includes(p.Sub_Category)) {
      subCategories.push(p.Sub_Category)
    }
  })
  return subCategories
}

function renderCategoryButtons() {
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ': entering renderCategoryButtons')

  sessionStorage.setItem('Category_dict', JSON.stringify(Category_dict))
  $('#category_buttons_div').html('')
  $('#category_buttons_div').append(`<div class="category_btn active" data-cat="ALL">ALL</div>`)
  Object.keys(Category_dict).forEach((cat) => {
    $('#category_buttons_div').append(`<div class="category_btn" data-cat="${cat}">${cat.replace('_', ' ').toUpperCase()}</div>`)
  })

  $('.category_btn').on('click', function () {
    var currTime = new Date().getTime() - startLoad
    console.log(currTime + ': entering categoryBtn_Click event Handler for button ' + $(this).data('cat'))
    $('.category_btn').removeClass('active')
    $(this).addClass('active')
    var selected_Sub_Categories
    var selected_Category = [$(this).data('cat')]
    if (selected_Category[0] == 'ALL') {
      selected_Sub_Categories = null
    } else {
      selected_Sub_Categories = getSubCategories(selected_Category[0])
    }
    updateFilterSubCategories(selected_Sub_Categories)
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

function setImageDimentions(no_of_columns) {
  var width = (1 / no_of_columns) * ($('#product_grid').width() - (no_of_columns - 1) * parseInt($('#product_grid').css('column-gap').replace('px', '')))
  // var height =
  //   (1 / no_of_rows) *
  //   ($(window).innerHeight() - $('#navbar_section').innerHeight() - $('#title_section').innerHeight() - $('#nav_section').innerHeight() - parseInt($('#product_grid').css('row-gap').replace('px', '')))
  imageTsfs.width = Math.floor(width)
  imageTsfs.height = Math.floor((width * 4) / 3)
}

function resizeImages() {
  var product_divs = $('#product_grid>div')
  var common_html = 'https://res.cloudinary.com/guixlbdm/image/upload/'
  $.each(product_divs, function (i) {
    var pid = this.id.split('_')[0]
    var format_html = 'c_auto,h_' + imageTsfs.height + ',w_' + imageTsfs.width
    var public_id = allProductDict[pid].images[0]
    var specific_html = '/' + public_id
    var img_url = common_html + format_html + specific_html
    $(this).find('img').attr('src', img_url)
    console.log(product_divs[i].id.split('_')[0])
  })
  $('#product_grid').css('grid-template-columns', 'repeat(auto-fill, ' + imageTsfs.width + 'px)')
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
      setImageDimentions(2)
      resizeImages()
    })
    $('#image_size-large').on('click', function () {
      setImageDimentions(1)
      resizeImages()
    })
  } else {
    $('#image_size-large').on('click', function () {
      imageTsfs.width = Math.ceil(150)
      imageTsfs.height = Math.ceil((150 * 4) / 3)
      resizeImages()
    })
    $('#image_size-medium').on('click', function () {
      imageTsfs.width = Math.ceil(120)
      imageTsfs.height = Math.ceil((120 * 4) / 3)
      resizeImages()
    })
    $('#image_size-small').removeClass('hidden')
    $('#image_size-small').on('click', function () {
      imageTsfs.width = Math.ceil(90)
      imageTsfs.height = Math.ceil((90 * 4) / 3)
      resizeImages()
    })
  }

  $('#filter_popup_button').on('click', showFilterPopup)
  $('#filter_button').on('click', filterFormSubmit)
  $('#clear_filter_button').on('click', clearFilter)
  $('#sort_popup_button').on('click', showSortPopup)
  $('#sort_button').on('click', sortFormSubmit)
}
