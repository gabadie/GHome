function unescape(ev)
    {  
var MonParagraphe = document.getElementById("descriptionArticle");
var truci = MonParagraphe.innerText;
var res = String(truci).replace("&lt;","<");
var res2 = String(res).replace("&gt;", ">") ;
var res3 = String(res2).replace("&#34;", "'");
MonParagraphe.innerText = res3;
    }


function htmlDecode(value){ 
  return $('<div/>').html(value).text(); 
}

var MonParagraphe = document.getElementById("descriptionArticle");
MonParagraphe.innerText = htmlDecode(innerText)