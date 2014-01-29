$(document).ready(function() {

    $('#play-music').ajaxForm({
        url: '/player', type: 'post',dataType:  'json',
        success : function(data){
            $('#fileName').text(data.name);
        }
        } );

  $('#pausing').click(function(){
      $.ajax({
      url: '/player/pause',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify("data"),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
            $('#pausing').text(data.result);
            $('#fileName').text(data.name);
        }
    });
    });

    $('#next').click(function(){
      $.ajax({
      url: '/player/next',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify("data"),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
            $('#pausing').text(data.result);
            $('#fileName').text(data.name);
        }
    });
    });

  $('#previous').click(function(){
      $.ajax({
      url: '/player/previous',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify("data"),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
            $('#pausing').text(data.result);
            $('#fileName').text(data.name);
        }
    });
    });


});
