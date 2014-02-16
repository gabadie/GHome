$(document).ready(function() {
    sensor_template = loadTemplate('#sensor-template');
    lamp_template = loadTemplate('#lamp-template');
    connection_template = loadTemplate('#connection-template');

    Handlebars.registerPartial("connection-template", $("#connection-template").html());

    updateSensors();
    bindSensors();
    updateLamps();
    //setInterval(updateLamps, 500);

    $('#add-sensor').ajaxForm({
        dataType:  'json',
        success: function(data) {
            updateSensors();
            drawGraph();
        }
    });

    // Drawing the devices' graph
    drawGraph();
})

var drawGraph = function() {
    apiCall('/connection/graph', 'GET', {}, function(graph_data) {
        $("#devices-graph").html("");
        s = new sigma({
            graph: graph_data,
            container: 'devices-graph',
            settings: {
                showLabels: false
            }
        });

    });
}

var drawChart = function(device_id, xcharts_data) {
    var figure_id = '#readings-' + device_id;

    tt = document.createElement('div'),
      leftOffset = -(~~$('html').css('padding-left').replace('px', '') + ~~$('body').css('margin-left').replace('px', '')),
      topOffset = -32;
    tt.className = 'ex-tooltip';
    document.body.appendChild(tt);

    apiCall('/sensor/' + device_id + '/xcharts_data', 'GET', {}, function(d) {
        if (!d.ok || !d.result.length) {
            $(figure_id).parent().hide();
            return;
        }
        var data = {
          "xScale": "time",
          "yScale": "linear",
          "main": d.result

        };

        var opts = {
          "dataFormatX": function (x) { return d3.time.format('%Y-%m-%dT%H:%M:%S').parse(x); },
          "tickFormatX": function (x) { return d3.time.format('%A')(x); },
          "mouseover": function (d, i) {
            var pos = $(this).offset();
            $(tt).text(d3.time.format('%A')(d.x) + ': ' + d.y)
              .css({top: topOffset + pos.top, left: pos.left + leftOffset})
              .show();
          },
          "mouseout": function (x) {
            $(tt).hide();
          }
        };

        var myChart = new xChart('line-dotted', data, figure_id, opts);
        $(figure_id).parent().show();
    });

    $('.trigger-slider').slider()

}

var updateSensors = function() {
    $.getJSON('/sensor', function(data) {
            $('.sensors').html('');
            $.each(data.result, function(i, s) {
                $('.sensors').append(sensor_template(s));
                drawChart(s.device_id);
            });
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

    // Expanding a sensor's view (by clicking on its heading)
    $('.sensors').on('click', 'li .heading', function(e) {
        $li = $(this).closest('li');
        $('.sensors li').not($li).find('.details').hide(200);

        $li.find('.details').stop();

        $li.find('.details').toggle(400);

    });

    // Toggling a sensor's state (ignored / not ignored)
    $('.sensors').on('click', 'li .sensor-toggle', function(e) {
        $li = $(this).closest('li.sensor');
        var currently_ignored = $li.hasClass('ignored');
        var sensor_id = $li.attr('data-sensor-id');
        var data = {value: !currently_ignored};

        var detailed = $li.find('.details').is(':visible');

        if (currently_ignored) {
            $li.removeClass('ignored');
        }
        else {
            $li.addClass('ignored');
        }

        apiCall('/sensor/' + sensor_id + '/ignored', 'POST', data, function(data) {
            console.log('Ignored/Activated : ');
            console.log(data);
        });

    });

    // Deleting a sensor
    $('.sensors').on('click', '.heading .delete', function(e) {
        $this = $(this).closest('li');
        var sensor_id = $this.attr('data-sensor-id');

        apiCall('/sensor/' + sensor_id, 'DELETE', {}, function(data) {
            $this.hide(200, function() {
                $this.remove();
                drawGraph();
            });
        });

        // Avoid triggering an event on the parent li
        e.stopPropagation();
    });

    // Deleting an event binding
    $('.sensors').on('click', '.event-connection .delete', function(e) {
        var connection_li = $(this).closest('.event-connection');
        var connection_id = connection_li.attr('data-connection-id');

        apiCall('/connection/' + connection_id, 'DELETE', {}, function(data) {
            if (data.ok) {
                connection_li.hide(300, function() { connection_li.remove(); });
                drawGraph();
            }
        });
    });

    // Adding an event binding
    $('.sensors').on('click', '.callback-binding .add', function(e) {
        var $this = $(this);
        var cb_form = $this.closest('.callback-binding');

        var sensor = cb_form.find('input[name="sensor"]').val();
        var event = cb_form.find('select[name="event"]').val();
        var actuator = cb_form.find('select[name="actuator"]').val();
        var callback = cb_form.find('select[name="callback"]:enabled').val();

        var params = {sensor: sensor, event: event, actuator: actuator, callback: callback};


        apiCall('/connection', 'POST', params, function(data) {

            if (data.ok) {
                $this.closest('table').find('tr:last').before(connection_template(data.result));
                drawGraph();
            }
            else {
                notification.error("Couldn't add a binding between '" + event + "' and '"
                                    + actuator + '.' + callback + "' : " + data.result);
            }
        });

    });

    // Activating the right callbacks' list
    $('.sensors').on('change', 'select[name="actuator"]', function(e) {
        $('select[name="callback"]').prop('disabled', true);
        $('select[name="callback"][data-actuator-id="' + $(this).val() + '"]').prop('disabled', false);
    });

    // s = $('select[name="callback"][data-actuator-id="889977"]')


    $('.sensors').on('slideStop', '.trigger-slider', function(ev){
        THIS = $(this);
        console.log('Just slided !');
        console.log($(this).val());
        console.log($(this));
        $(this).parent().parent().find('.trigger-threshold-min').val($(this).val());
    });


}
