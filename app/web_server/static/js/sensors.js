loadTemplate = function(template_id) {
    var source = $(template_id).html();
    return Handlebars.compile(source);
}

$(document).ready(function() {
    sensor_template = loadTemplate('#sensor-template');



    $('.selectpicker').selectpicker();

    updateSensors();
    bindSensors();

    updateLamps();
    setInterval(updateLamps, 500);

    $('#add-sensor').ajaxForm({
        dataType:  'json',
        success: function(data) {
            updateSensors();
        }
    });

})

var updateSensors = function() {
    apiCall('/sensor', 'GET', {}, function(data) {
        $('.sensors').html('');
        $.each(data.result, function(i, s) {
            $('.sensors').append(sensor_template(s));
        });

        bindSensors();
    });
}

var updateLamps = function() {
    apiCall('/lamp', 'GET', {}, function(data) {
        $('.lamps').html('');
        $.each(data.result, function(i, l) {
            $('.lamps').append(lampLi(l));
        });
    });
}

var lampLi = function(lamp) {
    var res = '';

    res += '<li data-sensor-id="' + lamp.device_id + '" ';
    if (lamp.turned_on) {
        res += 'class="turned_on"';
    }
    res += '><span class="device_id">' + lamp.device_id + '</span> <span class="name">' + lamp.name + '</span>';
    res += '</li>'

    return res;
}



var bindSensors = function() {
    $('.sensors li').click(function(e) {
        var currently_ignored = $(this).hasClass('ignored');
        var sensor_id = $(this).attr('data-sensor-id');
        var data = {value: !currently_ignored};

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
