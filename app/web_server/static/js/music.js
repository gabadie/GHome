$(document).ready(function() {



    $('#play-music').ajaxForm({
        url: '/player', type: 'post',dataType:  'json',
        success : function(data){
            $('#pausing').attr('src',"../static/img/player_pause.png");
            $('#song_text').text(data.name);
            $('#tag_text').text("Catégorie "+ data.tags);
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
            $('#pausing').attr('src',data.src);
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
            $('#song_text').text(data.name);
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
            $('#song_text').text(data.name);
        }
    });
    });


});


  function on_tag_click(this_button){
      $.ajax({
      url: '/player/tags',
      type: 'POST',
      async: true,
      dataType: "json",
      data: JSON.stringify(this_button),
      contentType: 'application/json;charset=UTF-8',
      success : function(data){
            $('#pausing').attr('src',"../static/img/player_pause.png");
            $('#song_text').text(data.name);
            $('#tag_text').text("Catégorie "+ data.tags);
        }
    });
    };