function showHiddenArticles(category) {
        var categ = document.getElementById(category);
        var hiddenArticles = categ.getElementsByClassName("hiddenArticle");

        for(var i=0; i<hiddenArticles.length; i++)
        {
            hiddenArticles[i].style.display = "block";
        }

        var buttonAdd = categ.getElementsByClassName("addCategory")[0];
        buttonAdd.style.display = "none";

        var buttonHide = categ.getElementsByClassName("hideCategory")[0];
        buttonHide.style.display = "block";
}

function hideHiddenArticles(category) {
        var categ = document.getElementById(category);
        var hiddenArticles = categ.getElementsByClassName("hiddenArticle");

        for(var i=0; i<hiddenArticles.length; i++)
        {
            hiddenArticles[i].style.display = "none";
        }

        var buttonAdd = categ.getElementsByClassName("addCategory")[0];
        buttonAdd.style.display = "block";

        var buttonHide= categ.getElementsByClassName("hideCategory")[0];
        buttonHide.style.display = "none";
}