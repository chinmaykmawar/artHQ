const url='https://script.google.com/macros/s/AKfycbzJhnOp1Cg0o-wVNMSE_opcnshYy3k6ZJj-t9FAqB5enbuPgS3A3MBxWbqZRe3xZss4/exec?Product_ID='
var product_data
var startLoad
var currTime

$(window).on('load', function (event){
    startLoad = new Date().getTime()
    console.log(startLoad + ':page loading')
    var product_id = ($("#product_id").html()).split('/')[2]
    getProductData(product_id)

    getProductImages(product_id)
})

async function getProductData(product_id) {
    currTime = new Date().getTime() - startLoad
    console.log(currTime+ "/getProductData:"+product_id)
    product_data= await $.ajax( url.concat( product_id))
    $("#product_title").html(product_data['Title'])
    $("#product_details_price").text(product_data['Price'])
    $("#product_details_desc").text(product_data['Description'])
    currTime = new Date().getTime() - startLoad
    console.log(currTime+"/getProductData:"+product_data)
}

function getProductImages(product_id){
    currTime = new Date().getTime() - startLoad;
    console.log(currTime+"/getProductImages : Entering")

    var folder_path = '../static/assets/Product_Images/product_page_images/'+product_id+'/';
    var img_main ='<img id="'+product_id+'" src="'+folder_path+product_id+'_main.jpg" alt="Product Image"></img>';
    $("#main_image").html(img_main)

    currTime = new Date().getTime() - startLoad;
    console.log(currTime+"/getProductImages : Main Image Loaded")
    console.log(currTime+"/getProductImages :"+ folder_path)
    var img_file
    var car_html

    for(i=1;i<6;i++)
    {
        //img_file ='<img id="'+product_id+'" src="'+folder_path+product_id+'_'+i+'.jpg" alt="Product Image"></img>';
        //$("#additional_images").append(img_file);
        //currTime = new Date().getTime() - startLoad;
        //console.log(currTime+"/getProductImages :"+ product_id+'_'+i+'.jpg added')
    } 

}

// get our elements
const slider = document.querySelector('.slider-container'),
  slides = Array.from(document.querySelectorAll('.slide'))

// set up our state
let isDragging = false,
  startPos = 0,
  currentTranslate = 0,
  prevTranslate = 0,
  animationID,
  currentIndex = 0

// add our event listeners
slides.forEach((slide, index) => {
  const slideImage = slide.querySelector('img')
  // disable default image drag
  slideImage.addEventListener('dragstart', (e) => e.preventDefault())
  // pointer events
  slide.addEventListener('pointerdown', pointerDown(index))
  slide.addEventListener('pointerup', pointerUp)
  slide.addEventListener('pointerleave', pointerUp)
  slide.addEventListener('pointermove', pointerMove)
})

// make responsive to viewport changes
window.addEventListener('resize', setPositionByIndex)

// prevent menu popup on long press
window.oncontextmenu = function (event) {
  event.preventDefault()
  event.stopPropagation()
  return false
}

// use a HOF so we have index in a closure
function pointerDown(index) {
  return function (event) {
    currentIndex = index
    startPos = event.clientX
    isDragging = true
    animationID = requestAnimationFrame(animation)
    slider.classList.add('grabbing')
  }
}

function pointerMove(event) {
  if (isDragging) {
    const currentPosition = event.clientX
    currentTranslate = prevTranslate + currentPosition - startPos
  }
}

function pointerUp() {
  cancelAnimationFrame(animationID)
  isDragging = false
  const movedBy = currentTranslate - prevTranslate

  // if moved enough negative then snap to next slide if there is one
  if (movedBy < -100 && currentIndex < slides.length - 1) currentIndex += 1

  // if moved enough positive then snap to previous slide if there is one
  if (movedBy > 100 && currentIndex > 0) currentIndex -= 1

  setPositionByIndex()

  slider.classList.remove('grabbing')
}

function animation() {
  setSliderPosition()
  if (isDragging) requestAnimationFrame(animation)
}

function setPositionByIndex() {
  currentTranslate = currentIndex * -window.innerWidth
  prevTranslate = currentTranslate
  setSliderPosition()
}

function setSliderPosition() {
  slider.style.transform = `translateX(${currentTranslate}px)`
}
