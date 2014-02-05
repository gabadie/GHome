$(document).ready(function() {
    product_template = loadTemplate('#product-template');

    // Rendering all the products
    apiCall('/product', 'GET', {}, function(data) {
        renderProducts(data.result);
    });

    // $('#fashion-query').keypress(function(e) {
    //     $this = $(this)
    //     if (e.which != 13) {
    //         return;
    //     }

    //     var params = {query: $this.val()};

    //     apiCall('/product/search', 'GET', params, function(data) {
    //         renderProducts(data.result);
    //     });

    // });


    $('#fashion-query').on('keyup', function(e) {
        var $this = $('#fashion-query')
        var query = $this.val();

        var products = $('.fashion-products');
        if (!query) {
            products.find('li').show();
        }
        else {
            products.find('li').hide();
            products.find('li:contains(' + query + ')').show();
        }

    });

});

renderProducts = function(products) {
    $('.fashion-products').html('');
    $.each(products, function(i, p) {
        $('.fashion-products').append(product_template(p));
    });
}
