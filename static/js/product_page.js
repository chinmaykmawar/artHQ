const url='https://script.google.com/macros/s/AKfycbzJhnOp1Cg0o-wVNMSE_opcnshYy3k6ZJj-t9FAqB5enbuPgS3A3MBxWbqZRe3xZss4/exec?Product_ID='
var product_data

$(window).on('load', function (event){
    var product_id = $("#product_id").html()
    var product_data=getProductData(product_id)
})

async function getProductData(product_id) {
    console.log(product_id);
    product_data= await $.ajax( url.concat( product_id.split('/')[2]))
    setProductData(product_data)
    //setProductData(product_data)
}

function setProductData(product_data){
    $("#product_details_name").text(product_data['Title'])
    console.log($("#product_details_name").text());
    $("#product_details_price").text(product_data['Price'])
    console.log($("#product_details_price").text())
    $("#product_details_desc").text(product_data['Description'])
    console.log($("#product_details_desc").text())
}