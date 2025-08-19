const url = 'https://script.google.com/macros/s/AKfycbzJhnOp1Cg0o-wVNMSE_opcnshYy3k6ZJj-t9FAqB5enbuPgS3A3MBxWbqZRe3xZss4/exec?Product_ID='
var product_id, product_data, startLoad, currTime, mouseCurrPos, ptrId

const slides_flexbox = $('.slider-container')
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

$(window).on('load', function (event) {
  startLoad = new Date().getTime()
  console.log(startLoad + ':page loading')
  product_id = window.location.href.split('/')[4]
  getProductData(product_id)
  getProductImages(product_id)
  setSlideAnimation()
})

$(document).on('click', function (event) {
  if (event.target.id) {
    switch (event.target.parentNode.id) {
      case 'product_details_nav':
        switch (event.target.id) {
          case 'product_details_nav_home':
            window.location.href = products_gridURL
            break
          case 'product_details_nav_cat':
            sessionStorage.setItem('filtertype', 'category')
            sessionStorage.setItem('filtertext', event.target.innerHTML)
            window.location.href = products_gridURL
            break
          case 'product_details_nav_cat':
            sessionStorage.setItem('filtertype', 'sub_category')
            sessionStorage.setItem('filtertext', event.target.html())
            window.location.href = products_gridURL
            break
        }
        break
    }
  }
})

async function getProductData(product_id) {
  currTime = new Date().getTime() - startLoad
  console.log(currTime + '/getProductData:' + product_id)
  product_data = await $.ajax(url.concat(product_id))
  populateProductDetails(product_data)
  currTime = new Date().getTime() - startLoad
  console.log(currTime + '/getProductData:' + product_data)
}

function getProductImages(product_id) {
  currTime = new Date().getTime() - startLoad
  console.log(currTime + '/getProductImages : Entering')

  var folder_path = baseURL + 'static/assets/Product_Images/product_page_images/' + product_id + '/'

  currTime = new Date().getTime() - startLoad
  console.log(currTime + '/getProductImages :' + folder_path)
  var img_html

  content_width = $('#product_grid').width()
  for (i = 1; i < 8; i++) {
    img_html = '<img id="' + product_id + '" src="' + folder_path + product_id + '_' + i + '.jpg" alt="Product Image"></img>'
    slide_html = '<div class="slide">' + img_html + '</div>'
    $('#product_images').append(slide_html)
    $('#product_images>div').css('max-width', content_width)
    currTime = new Date().getTime() - startLoad
    console.log(currTime + '/getProductImages :' + product_id + '_' + i + '.jpg added')
  }
}

function populateProductDetails(product_data) {
  var catCode = product_data['Cat Code']
  var category
  switch (catCode) {
    case 'H':
      category = 'Home Decor'
      break
    case 'J':
      category = 'Jewellery'
      break
  }
  var sub_Cat = product_data['Sub_Category']

  var NavHome = '<p id="product_details_nav_home" >Home</p>'
  var NavCatPage = '<p id="product_details_nav_cat">' + category + '</p>'
  var NavSub_CatPage = '<p id="product_details_nav_subCat">' + sub_Cat + '</p>'
  var chevron = '<p>></p>'
  $('#product_details_nav').html(NavHome + chevron + NavCatPage + chevron + NavSub_CatPage)
  $('#product_title').html(product_data['Title'])
  $('#product_details_price').text(product_data['Price'])
  $('#product_details_desc').text(product_data['Description'])

  /*
    {
  Product_ID: "HDCoaRes01BiG",
  Sub_Category: "Coasters",
  Base_Color: "Blue",
  Highlight: "Gold",
  Design: "01",
  Material: "Resin",
  "Bar Code": "",
  "Sub-Cat Code": "Coa",
  "Cat Code": "HD",
  "Design Code": "01",
  "Material Code": "Res",
  "Color Code": "BiG",
  "": "",
}
    */
}

function setSlideAnimation() {
  slides = Array.from($('.slide'))

  let isDragging = false,
    startPos = 0,
    currentTranslate = 0,
    prevTranslate = 0,
    animationID,
    currentIndex = 0

  $('.slide img').each(function (index) {
    $(this).on('dragstart', (e) => e.preventDefault())
    $(this).on('pointerdown', pointerDown(index))
    $(this).on('pointerup', pointerUp)
    $(this).on('pointerleave', pointerUp)
    $(this).on('pointermove', pointerMove)
  })

  // make responsive to viewport changes
  $(window).on('resize', setPositionByIndex)

  // prevent menu popup on long press
  window.oncontextmenu = function (event) {
    event.preventDefault()
    event.stopPropagation()
    return false
  }

  $('#carousel_buttton1').on('click', carouselButttonClick)

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
    slides_flexbox.addClass('grabbing')
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
  content_width = $('#product_grid').width()

  logText = logText + '/pointerUp=> Entering'
  logText = logText + (', eventType:' + event.type)
  logText = logText + (', target: ' + event.target.id)
  logText = logText + (', MousePos: ' + mouseCurrPos)
  logText = logText + (', mouse Start Pos: ' + mouseStartPos)
  logText = logText + (', current Index:' + currentIndex)
  logText = logText + (', grid Width :' + content_width)
  var movedBy = currTrans - prevTrans
  logText = logText + (', CurrTrans :' + currTrans)
  logText = logText + (', PrevTrans:' + prevTrans)

  // if moved enough negative then snap to next slide if there is one
  if (movedBy < -(content_width / 2) && currentIndex < slides.length - 1) currentIndex += 1

  // if moved enough positive then snap to previous slide if there is one
  if (movedBy > content_width / 2 && currentIndex > 0) currentIndex -= 1

  slides_flexbox.removeClass('grabbing')
  //event.target.releasePointerCapture(ptrId)

  logText = logText + (', MovedBy :' + movedBy)
  logText = logText + (', current Index:' + currentIndex)
  logText = logText + (', X pos:' + event.clientX)
  currTime = new Date().getTime() - startLoad
  console.log(currTime + logText)

  setPositionByIndex()
}

function animation() {
  setFlexBoxPosition()

  logText = ''
  logText = logText + ('MousePos: ' + mouseCurrPos)
  logText = logText + (', Curr Trans: ' + currTrans)
  currTime = new Date().getTime() - startLoad
  console.log(currTime + '/Animate=>' + logText)
  if (isDragging) requestAnimationFrame(animation)
}

function setPositionByIndex() {
  currTrans = currentIndex * -content_width
  prevTrans = currTrans
  //currTime = new Date().getTime() - startLoad
  //console.log(currTime + '/setPositionByIndex=> currentTranslate :' + currTrans + ', content Width:' + content_width)
  setFlexBoxPosition()
  //hideSlides()
}

function setFlexBoxPosition() {
  slides_flexbox.css('transform', `translateX(${currTrans}px)`)
  //currTime = new Date().getTime() - startLoad
  //console.log(currTime + '/setFlexBoxPosition=> currTranslate:'+currTrans+', Execution Complete')
}

function carouselButttonClick() {
  console.log('working.......')
  var first_img, testMouseStartPos, testMouseEndPos, testMouseCurrPos, down_event, up_event, move_event, leave_event, increment, intervalID, route

  first_img = $('.slide img')[0]
  testMouseStartPos = 300
  testMouseEndPos = 100
  increment = -1

  down_event = new PointerEvent('pointerdown', {clientX: testMouseStartPos})
  first_img.dispatchEvent(down_event)

  route = 1

  switch (route) {
    case 0:
      testMouseCurrPos = testMouseStartPos
      intervalID = setInterval(() => {
        testMouseCurrPos += increment
        move_event = new PointerEvent('pointermove', {clientX: testMouseCurrPos})
        first_img.dispatchEvent(move_event)
        console.log(testMouseCurrPos)
        if (testMouseCurrPos < testMouseEndPos) {
          clearInterval(intervalID)
          up_event = new PointerEvent('pointerup', {clientX: testMouseEndPos})
          leave_event = new PointerEvent('pointerleave', {clientX: testMouseEndPos})
          first_img.dispatchEvent(up_event)
        }
      }, 10)
      break
    case 1:
      for (testMouseCurrPos = testMouseStartPos; testMouseCurrPos > testMouseEndPos; testMouseCurrPos += increment) {
        //for(var i = 300; i < 8; i++){
        move_event = new PointerEvent('pointermove', {clientX: testMouseCurrPos})
        first_img.dispatchEvent(move_event)
        setTimeout(() => {
        console.log(testMouseCurrPos)  
        }, 10);
        
      }
      up_event = new PointerEvent('pointerup', {clientX: testMouseEndPos})
      leave_event = new PointerEvent('pointerleave', {clientX: testMouseEndPos})
      first_img.dispatchEvent(up_event)
      break
  }
}
