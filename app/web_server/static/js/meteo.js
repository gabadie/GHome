$(document).ready(function() {

    $('#get-weather').ajaxForm({
        dataType:  'json',
        success : function(data){
            var node = document.getElementById("weather");
	    node.innerHTML = "";

	    if (data.ok) {
		var loc = document.createElement('div'); 
		loc.innerHTML = data.location + " (" + data.latitude + ", " + data.longitude + ")";
		node.appendChild(loc);

		var actual = document.createElement('div');
		actual.innerHTML = "Il est " + data.weather[0].timestamp + ", le ciel est " + data.weather[0].weather.status;
		node.appendChild(actual);

		var prev = document.createElement('div');
		var table = document.createElement('table');
		var tbody = document.createElement('tbody');
		var line = document.createElement('tr');
		line.innerHTML = "<td>Jour et heure</td><td>Ciel</td><td>Vitesse du vent (km/h)</td><td>Direction du vent (°)</td><td>Température (TODO)</td><td>Humidité (%)</td>";
		tbody.appendChild(line)

		for(var i = 1; i < data.weather.length; i++)
		{
		    var weather = data.weather[i].weather;
		    var tmpLine = document.createElement('tr');
		    tmpLine.innerHTML = "<td>" + data.weather[i].timestamp + "</td><td>" + weather.status + "</td><td>" +  weather.measured.wind_speed + "</td><td>" +  weather.measured.wind_direction + "</td><td>" +  weather.measured.temperature + "</td><td>" +  weather.measured.humidity + "</td>";
		    tbody.appendChild(tmpLine);
		}
		table.appendChild(tbody);
		table.setAttribute("class", "table table-striped");
		prev.appendChild(table);
		node.appendChild(prev);
            }
            else {
                node.innerHTML = "Les données météo n'ont pu être récupérées"
            }
            
            $.each(data.result, function(i, content) {
		var div = document.createElement('div'); 
		div.innerHTML = content;
                document.getElementById("weather").appendChild(div);
            });

        }
        });
});

