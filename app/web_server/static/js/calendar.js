$(document).ready(function() {
  $('.alarm_header').on('click',function(data){
    var hours = 
    $('#hours').attr('value', Math.floor($(this).attr("alarm_minutes")/60));
    $('#minutes').attr('value',$(this).attr("alarm_minutes")%60);
  });

})