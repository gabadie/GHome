/* Handlebars */
Handlebars.registerHelper('times', function(n, block) {
    var accum = '';
    for(var i = 0; i < n; ++i)
        accum += block.fn(i);
    return accum;
});

/* API related */
var apiCall = function(path, method, data, callback) {
	$.ajax({
	  url: path,
	  type: method,
	  async: true,
	  dataType: "json",
	  data: JSON.stringify(data),
	  contentType: 'application/json;charset=UTF-8',
	  success: callback
	});
};
