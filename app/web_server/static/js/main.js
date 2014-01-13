$(document).ready(function() {
	$('.selectpicker').selectpicker();

	updateSensors();
	bindSensors();

    $('#add-sensor').ajaxForm({ 
        dataType:  'json', 
        success: function(data) {
        	updateSensors();
        } 
    }); 

})

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
}

var updateSensors = function() {
	apiCall('/sensor', 'GET', {}, function(data) {
		$('.sensors').html('');
		$.each(data.result, function(i, s) {
			$('.sensors').append(sensorLi(s));
		});

		bindSensors();
	});
}

var sensorLi = function(sensor) {
	var res = '';

	res += '<li data-sensor-id="' + sensor.device_id + '" ';
	if (sensor.ignored) {
		res += 'class="ignored"';
	}
	res += '><span class="device_id">' + sensor.device_id + '</span>: <span class="name">' + sensor.name + '</span>';
    res += '<span class="delete glyphicon glyphicon-remove"></span>';
    res += '</li>'

    return res;
}

var bindSensors = function() {
	$('.sensors li').click(function(e) {
		var currently_ignored = $(this).hasClass('ignored');
		var sensor_id = $(this).attr('data-sensor-id');
		var data = {ignored: !currently_ignored};

		apiCall('sensor/' + sensor_id + '/ignored', 'POST', data, function(data) {
			updateSensors();
		})
	
	});

	$('.sensors li .delete').click(function(e) {
		var sensor_id = $(this).parent('li').attr('data-sensor-id');

		apiCall('/sensor/' + sensor_id, 'DELETE', {}, function(data) {
			updateSensors();
		});

		// Avoid triggering an event on the parent li
		e.stopPropagation();
	});
}