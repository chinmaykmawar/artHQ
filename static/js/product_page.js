var product_id, product_data, startLoad, currTime, mouseCurrPos, ptrId
var content_width
var slides

let isDragging = false,
  mouseStartPos = 0,
  currTrans = 0,
  prevTrans = 0,
  animationID,
  currentIndex = 0

port = '8000'
currURL = window.location.href
baseURL = currURL.split(port + '/')[0] + port + '/'
products_gridURL = baseURL + '/products'

console.log(typeof addToCart)

/* ===== EVENTS ===== */

/* INIT */
$(document).ready(function () {
  renderCart()
})

$(window).on('load', function (event) {
  startLoad = new Date().getTime()
  console.log(startLoad + ':page loading')
  url = window.location.href.split('/')
  product_id = url[url.length - 1]
  getProductData(product_id)
  getProductImages(product_id)
  setSlideAnimation()
})

async function getProductData(product_id) {
  //product_data = await $.ajax(url.concat(product_id))

  const stored = sessionStorage.getItem('ALL_PRODUCTS')

  if (!stored) {
    console.error('❌ No products in sessionStorage')
    return null
  }

  const products = JSON.parse(stored)

  product_data = products.find((p) => p.Product_ID === product_id)

  if (!product_data) {
    console.error('❌ Product not found:', product_id)
    return null
  }

  populateProductDetails(product_data)
}

async function getProductImages(product_id) {
  const folder_path = baseURL + 'static/assets/Product_Images/' + product_id + '/'

  const images = await $.ajax(`/get-images/${product_id}/`)

  const content_width = $('#product_grid').width()

  $('#product_images').empty()
  $('#carousel_butttons').empty()

  images.forEach((file, index) => {
    const img_html = `<img src="${folder_path}${file}" alt="Product Image">`
    const slide_html = `<div class="slide">${img_html}</div>`

    $('#product_images').append(slide_html)
    $('#product_images>div').css('max-width', content_width)

    const btn_html = `<button id="carousel_buttton_${index + 1}"></button>`
    $('#carousel_butttons').append(btn_html)

    $(`#carousel_buttton_${index + 1}`).on('click', function (event) {
      event.stopPropagation()
      productImageButton_click(event.target.id.split('_')[2])
    })
  })

  setSlideAnimation()

  $('#carousel_buttton_1').addClass('active')
}

function populateProductDetails(product_data) {
  let category

  switch (product_data['Cat Code']) {
    case 'H':
      category = 'Home Decor'
      break
    case 'J':
      category = 'Jewellery'
      break
    default:
      category = 'Products'
  }

  const sub_Cat = product_data['Sub_Category']

  // NAV
  $('#product_title').html(sub_Cat)

  $('#product_details_nav').html(`
      <span id="product_details_nav_home">Home</span> >
      <span id="product_details_nav_cat">${category}</span> >
      <span id="product_details_nav_subCat">${sub_Cat}</span>
    `)

  // TITLE
  $('#product_title_right').text(product_data['Title'])

  // PRICE
  $('#product_details_price').text('₹ ' + product_data['Price'])

  // DESCRIPTION
  $('#product_details_desc').text(product_data['Description'])

  // OPTIONAL STATIC (can later be dynamic)
  $('#product_rating').html('★★★★☆ <span>(120 reviews)</span>')

  setupDescriptionToggle()
}

function setupDescriptionToggle() {
  const desc = $('#product_details_desc')
  const btn = $('#desc_toggle_btn')

  if (desc[0].scrollHeight <= 60) {
    btn.hide()
  }

  btn.off('click').on('click', function () {
    desc.toggleClass('expanded')

    if (desc.hasClass('expanded')) {
      btn.text('View Less')
    } else {
      btn.text('View More')
    }
  })
}

function setSlideAnimation() {
  slides = Array.from($('.slide'))

  $('.slide img').each(function (index) {
    $(this).on('dragstart', (e) => e.preventDefault())
    $(this).on('pointerdown', pointerDown(index))
    $(this).on('pointerup', pointerUp)
    //$(this).on('pointerleave', pointerUp)
    $(this).on('pointermove', pointerMove)
  })

  // make responsive to viewport changes
  $(window).on('resize', setFlexBoxPositionFromIndex)

  // prevent menu popup on long press
  window.oncontextmenu = function (event) {
    event.preventDefault()
    event.stopPropagation()
    return false
  }

  currTime = new Date().getTime() - startLoad
  console.log(currTime + '/setSlideAnimation : Event Listeners Set')
}

function pointerDown(index) {
  return function (event) {
    event.stopPropagation()
    var tmstp
    tmstp = event.timeStamp
    currentIndex = index
    mouseStartPos = event.clientX
    isDragging = true
    mouseCurrPos = mouseStartPos
    animationID = requestAnimationFrame(animation)
    $('.slides_flexbox').addClass('grabbing')
    //event.target.setPointerCapture(ptrId)
    currTime = new Date().getTime() - startLoad
    console.log(currTime + '/pointerDown=> Mouse Start Pos :' + mouseStartPos + ', pointerType:' + event.pointerType + ', timestamp:' + tmstp)
  }
}

function pointerMove(event) {
  if (isDragging) {
    mouseCurrPos = event.clientX
    currTrans = prevTrans + mouseCurrPos - mouseStartPos
  }
}

function pointerUp(event) {
  event.stopPropagation()
  var logText = ''
  cancelAnimationFrame(animationID)
  isDragging = false
  content_width = $('.slide')[0].clientWidth
  var prevIndex = currentIndex

  $('#carousel_buttton_' + (currentIndex + 1)).removeClass('active')

  movedBy = mouseCurrPos - mouseStartPos

  // if moved enough negative then snap to next slide if there is one
  if (movedBy < -(content_width / 2) && currentIndex < slides.length - 1) currentIndex += 1

  // if moved enough positive then snap to previous slide if there is one
  if (movedBy > content_width / 2 && currentIndex > 0) currentIndex -= 1

  $('.slides_flexbox').removeClass('grabbing')
  $('#carousel_buttton_' + (currentIndex + 1)).addClass('active')

  currTime = new Date().getTime() - startLoad
  console.group('🧪 Product Debug')
  console.log(currTime + '/pointerUp : movedBy :' + movedBy + ', content_width:' + content_width + ', currentIndex:' + currentIndex + ', prevIndex:' + prevIndex)
  console.groupEnd()

  setFlexBoxPositionFromIndex()
}

function animation() {
  setFlexBoxPositionFromPointer()
  if (isDragging) requestAnimationFrame(animation)
}

function setFlexBoxPositionFromIndex() {
  currTrans = currentIndex * -content_width
  prevTrans = currTrans
  setFlexBoxPositionFromPointer()
}

function setFlexBoxPositionFromPointer() {
  $('.slides_flexbox').css('transform', `translateX(${currTrans}px)`)
}

function productImageButton_click(index) {
  var req_translate
  $('#carousel_buttton_' + (currentIndex + 1)).removeClass('active')
  currentIndex = index - 1
  $('#carousel_buttton_' + (currentIndex + 1)).addClass('active')
  req_translate = -(currentIndex * content_width)
  $('.slides_flexbox').css('transform', 'translateX(' + req_translate + 'px)')
}

function nextImage() {
  console.log('nextImage Entering')
  var curr_img, testMouseStartPos, testMouseEndPos, testMouseCurrPos, down_event, up_event, move_event, leave_event
  var increment, intervalID, curr_index

  curr_index = -Math.round(parseInt($('.slides_flexbox').css('transform').split(',')[4]) / content_width)

  if (isNaN(curr_index)) {
    curr_index = 0
  }
  curr_img = $('.slide img')[curr_index]
  testMouseStartPos = 300
  testMouseEndPos = 100
  increment = -1

  down_event = new PointerEvent('pointerdown', {clientX: testMouseStartPos})
  curr_img.dispatchEvent(down_event)

  testMouseCurrPos = testMouseStartPos
  intervalID = setInterval(() => {
    testMouseCurrPos += increment
    move_event = new PointerEvent('pointermove', {clientX: testMouseCurrPos})
    curr_img.dispatchEvent(move_event)
    //console.log(testMouseCurrPos)
    if (testMouseCurrPos < testMouseEndPos) {
      clearInterval(intervalID)
      up_event = new PointerEvent('pointerup', {clientX: testMouseEndPos})
      leave_event = new PointerEvent('pointerleave', {clientX: testMouseEndPos})
      curr_img.dispatchEvent(up_event)
    }
  }, 5)
}

function prevImage() {
  console.log('working.......')
  var curr_img, testMouseStartPos, testMouseEndPos, testMouseCurrPos, down_event, up_event, move_event, leave_event

  var increment, intervalID, curr_index

  curr_index = -Math.round(parseInt($('.slides_flexbox').css('transform').split(',')[4]) / content_width)

  if (isNaN(curr_index)) {
    curr_index = 0
  }
  curr_img = $('.slide img')[curr_index]
  testMouseStartPos = 100
  testMouseEndPos = 300
  increment = 1

  down_event = new PointerEvent('pointerdown', {clientX: testMouseStartPos})
  curr_img.dispatchEvent(down_event)

  testMouseCurrPos = testMouseStartPos
  intervalID = setInterval(() => {
    testMouseCurrPos += increment
    move_event = new PointerEvent('pointermove', {clientX: testMouseCurrPos})
    curr_img.dispatchEvent(move_event)
    console.log(testMouseCurrPos)
    if (testMouseCurrPos > testMouseEndPos) {
      clearInterval(intervalID)
      up_event = new PointerEvent('pointerup', {clientX: testMouseEndPos})
      leave_event = new PointerEvent('pointerleave', {clientX: testMouseEndPos})
      curr_img.dispatchEvent(up_event)
    }
  }, 5)
}

$('#product_details_nav').on('click', 'a', function () {
  switch (this.id) {
    case 'product_details_nav_home':
      window.location.href = products_gridURL
      break

    case 'product_details_nav_cat':
      sessionStorage.setItem('filtertype', 'category')
      sessionStorage.setItem('filtertext', this.innerHTML)
      window.location.href = products_gridURL
      break

    case 'product_details_nav_subcat':
      sessionStorage.setItem('filtertype', 'sub_category')
      sessionStorage.setItem('filtertext', this.innerHTML)
      window.location.href = products_gridURL
      break
  }
})

$('#carousel_buttons').on('click', '.carousel_button', function () {
  console.log('carousel button clicked')
})

$('#buy_now_btn').on('click', function () {
  product_data.qty = 1
  sessionStorage.setItem('CHECKOUT', JSON.stringify([product_data]))
  window.location.href = '/checkout'
})
