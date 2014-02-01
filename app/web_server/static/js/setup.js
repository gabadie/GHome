loadTemplate = function(template_id) {
    var source = $(template_id).html();
    return Handlebars.compile(source);
}

$(document).ready(function() {
    sensor_template = loadTemplate('#sensor-template');
    lamp_template = loadTemplate('#lamp-template');

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
    $.getJSON('/sensor', function(data) {
            $('.sensors').html('');
            $.each(data.result, function(i, s) {
                $('.sensors').append(sensor_template(s));
            });

            bindSensors();
    });
}

var updateLamps = function() {
    $.getJSON('/lamp', function(data) {
        $('.lamps').html('');
        $.each(data.result, function(i, l) {
            $('.lamps').append(lamp_template(l));
        });
    });


}


var bindSensors = function() {

    $('.sensors li .heading').unbind();
    $('.sensors li .heading').click(function(e) {
        $li = $(this).closest('li');
        $('.sensors li').not($li).find('.details').hide(200);

        $li.find('.details').stop();

        $li.find('.details').toggle(400);

    });

    $('.sensors li .sensor-toggle').unbind();
    $('.sensors li .sensor-toggle').click(function(e) {
        $li = $(this).closest('li.sensor');
        var currently_ignored = $li.hasClass('ignored');
        var sensor_id = $li.attr('data-sensor-id');
        var data = {value: !currently_ignored};

        var detailed = $li.find('.details').is(':visible');

        apiCall('sensor/' + sensor_id + '/ignored', 'POST', data, function(data) {
            var sensor = data.result;
            $li.replaceWith(sensor_template(sensor));
            $new_li = $("[data-sensor-id='" + sensor.device_id + "']");
            $new_li.find('.details').show();

            bindSensors();
        });

        if (currently_ignored) {
            $li.removeClass('ignored');
        }
        else {
            $li.addClass('ignored');
        }

    });

    $('.sensors li .delete').unbind();
    $('.sensors li .delete').click(function(e) {
        var sensor_id = $(this).parent('li').attr('data-sensor-id');

        apiCall('/sensor/' + sensor_id, 'DELETE', {}, function(data) {
            updateSensors();
        });

        // Avoid triggering an event on the parent li
        e.stopPropagation();
    });
}
