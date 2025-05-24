const url = 'https://script.google.com/macros/s/AKfycbyMzsf3M4IFiE2AMnmEgxi8rge3_geTFRpnAPr71rDcCCt0sapvJpopbOdzyzhjI0Sn/exec'

var startLoad
var startFilter
var startSort

$(window).on('load', onLoadFunction)

$(document).on('click', function (event) {
  if ($(event.target)[0].id) {
    var eleid = $(event.target)[0].id
    if (eleid.startsWith('HDCoa') || eleid.startsWith('JECon')) {
      sessionStorage.setItem('Product_ID', 'HDCoaRes01BiG')
      sessionStorage.setItem('Product_ID', eleid);
      href = 'http://localhost:8000/product'
    }
  }
})

async function onLoadFunction() {
  startLoad = new Date().getTime()
  console.log(startLoad + ':page loading')
  var displayedProducts = await getProducts(setFilterFromSessionStorage())
  
  setFilterOptions(displayedProducts)
  setEventHandlers()
  createDiv(displayedProducts)
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ':page loaded')
  //sessionStorage.setItem('Product_ID', 'HDCoaRes01BiG');
  //window.location.href = '..\\product\\HDCoaRes01BiG'
}

async function filterFormSubmit() {
  //startFilter = new Date().getTime();
  //console.log(startFilter + ": filter form submitted");

  hideFilterPopup()
  var filterInput = []

  $('#filter_form input').each(function () {
    if (this.checked) {
      filterInput.push(this.id.split('_')[2])
    }
  })
  8

  var displayedProducts = await getProducts(filterInput)
  createDiv(displayedProducts)
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
  hide + FilterPopup()
  onLoadFunction()
}

async function getProducts(filterInput) {
  //console.log(startLoad + ": before ajax query");
  var productsJson = await $.ajax(url)
  //var currTime = (new Date().getTime()) - startLoad;
  //console.log(currTime + ": after ajax query");
  var filteredProducts = []
  for (i = 0; i < productsJson.data.length; i++) {
    var isRetained = false

    if (filterInput.length == 0) {
      isRetained = true
    } else {
      $.each(filterInput, function (j) {
        if (productsJson.data[i].Sub_Category == filterInput[j]) {
          isRetained = true
        }
      })
    }
    if (productsJson.data[i].Product_ID != '#N/A' && productsJson.data[i].Product_ID != '' && isRetained == true) {
      const product = {}
      $.each(productsJson.data[i], function (k, v) {
        product[k] = v
      })
      filteredProducts.push(product)
    }
  }
  //var currTime2 = (new Date().getTime()) - startLoad;
  //console.log(currTime2 + ": Returning filtered List with " + filteredProducts.length + " products");
  return filteredProducts
}

function createDiv(products) {
  //var currTime = new Date().getTime() - startLoad;
  //console.log(currTime + ": entering createDiv. no of products:" + products.length);
  $('#product_grid').html('')
  $('#product_count').html(products.length + ' products')
  baseURL="http://localhost:8000"

  $.each(products, function (i) {
    var id = products[i].Product_ID
    var category = getCategory(products[i].Sub_Category)
    var title = products[i].Title
    var price = products[i].Price
    
    var html = '<div id="'+id+'_div" class="Product ' + category + ' ' + products[i].Sub_Category + ' ' + products[i].Material + ' ' + products[i].Base_Color + '_Base ' + products[i].Highlight + '_Highlight"'+' style="flex-direction: column;"><a href="http://localhost:8000/product/'+id+'"><img id="'+id+'" src="static/assets/Product_Images/grid_images/'+id+'.jpg" alt="Product Image"></a><div class="Product_title">'+title+'</div><div class="price row"><div class="MRP_text col">MRP</div><div class="price_text col">'+price+'</div></div></div>'
    $('#product_grid').append(html)
  })
  //var currTime = new Date().getTime() - startLoad;
  //console.log(currTime + ":  Exiting CreateDiv");
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

function setFilterFromSessionStorage() {
  //var currTime = new Date().getTime() - startLoad
  //console.log(currTime + ':entering Set Filter')
  var filterInput = []
  if (sessionStorage.getItem('filtertext') != null) {
    var filtertext = [sessionStorage.getItem('filtertext')]
    sessionStorage.removeItem('filtertext')
    if (sessionStorage.getItem('filtertype') == 'category') {
      filtertext = getSubCategories(filtertext)
    }
    sessionStorage.removeItem('filtertype')
    var currTime = new Date().getTime() - startLoad
    console.log(currTime + ': filter text fetched with length : ' + filtertext.length)
    $.each(filtertext, function () {
      var id = '#filter_checkbox_' + this
      $(id).prop('checked', true)
      var currTime = new Date().getTime() - startLoad
      console.log(currTime + ':' + id + ' checkbox checked ')
    })
    $('#filter_form input').each(function () {
      if (this.checked) {
        filterInput.push(this.id.split('_')[2])
      }
    })
  }
  return filterInput
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

function setFilterOptions(sortedProducts) {
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
    divhtml3 = '  <label class="" for="filter_checkbox_' + this + '">' + this + '</label>\n'
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

function setEventHandlers(){
  $('#image_size-large').on('click', function(){
    var currTime = new Date().getTime() - startLoad
    console.log(currTime + ':image size large clicked')
    setImageSizes(210)
  } )
  $('#image_size-medium').on('click', function(){setImageSizes(150)})
  $('#image_size-small').on('click', function(){setImageSizes(90)})
}

function setImageSizes(width){
  var currTime = new Date().getTime() - startLoad
  console.log(currTime + ':entering set Image size for width -'+ width)
  height=width*4/3
  $('#product_grid').css('grid-template-columns', 'repeat(auto-fill, '+width+'px)')
  $('#product_grid img').each(function () {
    $(this).css('width',width)
    $(this).css('height',height)
  })
}