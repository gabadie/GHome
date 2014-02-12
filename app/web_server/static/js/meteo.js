$(document).ready(function() {

	var displayAll = function() {
		$.getJSON('/meteo/weather', function(data) {
	        var node = document.getElementById("weather");
	    	node.innerHTML = "";

	    	if (data.geo) {
	    		displayLocation(node, data);
	    		displayWeather(node, data);
	    	}
	    });
    }

	var displayLocation = function(node, data) {
		var inputloc = document.getElementById('location');
		inputloc.setAttribute("value", data.location);

		var loc = document.createElement('div'); 
		loc.innerHTML = "<h4>Météo à <b>" + data.location + "</b></h4>";
        node.appendChild(loc);
	}

	var displayWeather = function(node, data) {
		var prev = document.createElement('div');
	    if (data.meteo) {
			var actual = document.createElement('div');
			var date = data.weather[0].timestamp.split("#");
			actual.innerHTML = "<h4>Nous sommes le <b>" + date[0]
				+ "</b></br>Il est actuellement <b>" + date[1]
				+ "</b><br/>Ciel : <img src=\"" + data.weather[0].icon + "\" width=\"100px\"/></h4>";
			node.appendChild(actual);

			var table = document.createElement('table');
			var tbody = document.createElement('tbody');
			var line = document.createElement('tr');
			line.innerHTML = "<td>Date</td>"
				+ "<td>Heure</td>"
				+ "<td>Ciel</td>"
				+ "<td>Température</td>"
				+ "<td>Humidité</td>"
				+ "<td>Vitesse du vent</td>"
				+ "<td>Direction du vent</td>";
			line.setAttribute("style", "font-weight: bold;");
			tbody.appendChild(line)

			for(var i = 1; i < data.weather.length; i++)
			{
				var tmpLine = document.createElement('tr');
			    var weather = data.weather[i].weather;
			    var ktemp = parseInt(weather.measured.temperature);
			    var temperature = Math.round((ktemp - 273.15) * 100) / 100;
			    var date = data.weather[i].timestamp.split("#");

			    tmpLine.innerHTML = "<td>" + date[0]
			    	+ "</td><td>" + date[1]
			    	+ "</td><td><img src=\"" + data.weather[i].icon + "\" width=\"50px\"/></td><td>"
			    	+  temperature + "°C</td><td>"
			    	+  weather.measured.humidity + "%</td><td>"
			    	+  weather.measured.wind_speed + " km/h</td><td>"
			    	+  weather.measured.wind_direction + "°</td>";
			    tbody.appendChild(tmpLine);
			}
			table.appendChild(tbody);
			table.setAttribute("class", "table table-striped");
			table.setAttribute("style", "width: 1000px");

			prev.appendChild(table);
        } else {
            prev.innerHTML = "<h4>Les données météorologiques n'ont pu être récupérées</h4>"
        }
        node.appendChild(prev);
	}

    $('#update-location').ajaxForm({
        dataType:  'json',
        success : function(data){
        	var node = document.getElementById("weather");
	    	node.innerHTML = "";

	    	if (data.ok) {
	    		displayAll();
	    	} else {
	    		node.innerHTML = "<h4>L'adresse spécifiée n'a pu être géolocalisée</h4>";
	    	}
        }
    });
    displayAll();
});

