$(document).ready(function() {

    var displayCurWeather = function() {
		$('#curweather').html("<h4>");
		$('#icweather').html("");

		$.getJSON('/meteo/getloc', function(data) {
    		$('#curweather').append(data.time + "</br>");

			if (data.loc) {
				$('#curweather').append(data.location + "</br>");

				$.getJSON('/meteo/currentweather', function(data) {
		    		if (data.meteo) {
		    			var temperature = Math.round((data.temperature - 273.15) * 100) / 100;
		    			$('#curweather').append(temperature + "°C, " + data.humidity + "% humidity</br>");
		    			$('#icweather').html("<img src=\"" + data.icon + "\" width=\"50px\"/>");
		    		}
			    });
			}
		});

	    
	    $('#curweather').append("</h4>");
    }


    displayCurWeather();
});
