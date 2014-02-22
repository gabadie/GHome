$(document).ready(function() {
    $('.addCategory').click(showHiddenArticles);
    $('.hideCategory').click(hideHiddenArticles);
});

function showHiddenArticles() {
    var category = $(this).data('category');
    var $categ = $(this).closest(".category-wrapper");
    $categ.find(".article.more").css('display', 'inline-block');

    $categ.find(".addCategory").hide();
    $categ.find(".hideCategory").show();
}

function hideHiddenArticles() {
    var category = $(this).data('category');
    var $categ = $(this).closest(".category-wrapper");
    $categ.find(".article.more").hide();

    $categ.find(".addCategory").show();
    $categ.find(".hideCategory").hide();
}
