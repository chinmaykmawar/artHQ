$(document).ready(function () {
  console.log('Footer loaded')
})

function createFooterCategoryLinks() {
  const savedCategoryDict = sessionStorage.getItem('Category_dict')

  if (savedCategoryDict === null || savedCategoryDict.trim() === '') {
    return
  }

  const Category_dict = JSON.parse(savedCategoryDict)

  let html = ''

  $.each(Category_dict, function (category, subCategories) {
    html +=
      '<div class="footer_link_group">' +
      '<span class="footer_link_heading">' +
      category +
      ' :</span> '

    $.each(subCategories, function (index, subCategory) {
      html +=
        '<span class="footer_filter_link" ' +
        'data-subcategory="' +
        subCategory +
        '">' +
        subCategory +
        '</span>'

      if (index < subCategories.length - 1) {
        html += ' | '
      }
    })

    html += '</div>'
  })

  $('#footer_shop_links').html(html)
}

// $('.footer_item').on('click', function (event) {

//   switch (event.target.id) {
//     case 'footer_track_order':
//       window.location.href = '/track-order/'
//       break
//     default:
//       console.log('No matching case for footer item click')
//       break
//   }
// })
