$(document).ready(function() {
    product_template = loadTemplate('#product-template');

    // Rendering all the products
    apiCall('/product', 'GET', {}, function(data) {
        renderProducts(data.result);
    });

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
    $.each(['top', 'bottom', 'feet'], function(i, type) {
        console.log(products);
        $.each(products[type], function(i, p) {
            $('.fashion-products.' + type).append(product_template(p));
        });

        $('.fashion-products.' + type + ' li').eq(0).addClass('active');
    });

    $('.carousel').carousel()

}
