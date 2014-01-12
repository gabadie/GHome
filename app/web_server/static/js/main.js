(
	$(document).ready(function() {
		console.log("lol");

		$('.devices li').click(function() {
			var currently_ignored = $(this).hasClass('ignored');
			var data = {ignored: !currently_ignored};

			// $.ajax({
			//   url: "/device/ignored",
			//   type: 'POST',
			//   async: true,
			//   dataType: "json",
			//   data: JSON.stringify(data),
			//   contentType: 'application/json;charset=UTF-8',
			//   success: function (data) {
			//       	//
			//   }
			// });
		
		});


	    $('#add-device').ajaxForm({ 
	        dataType:  'json', 
	        success: function(data) {
	        	renderDevices(data);
	        } 
	    }); 

	})


)