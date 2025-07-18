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

    for(i=1;i<8;i++)
    {
        img_file ='<img id="'+product_id+'" src="'+folder_path+product_id+'_'+i+'.jpg" alt="Product Image"></img>';
        $("#additional_images").append(img_file);
        currTime = new Date().getTime() - startLoad;
        console.log(currTime+"/getProductImages :"+ product_id+'_'+i+'.jpg added')
    } 

    //http://localhost:8000/static/assets/Product_Images/product_page_images/HCo01BiG/HCo01BiG_main.jpg

    /*$.ajax({
        url : "http://localhost:8000/"+folder_path,
        success: function (data) {
            currTime = new Date().getTime() - startLoad;
            console.log(currTime+"/getProductImages : Ajax Success")
            $(data).find("a").attr("href", function (i, val) {
                if( val.match(product_id)) { 
                    $("#additional_images").append( "<img src='"+ folder_path + val +"'>" );
                    console.log(folder_path+val);
                }
            });
        },
        error: function(e, status, errorThrown){
            currTime = new Date().getTime() - startLoad;
            console.log(currTime+"/getProductImages : Ajax Fail")
            console.log(e)
            console.log(status)
            console.log(errorThrown)

        }
    });*/


}
