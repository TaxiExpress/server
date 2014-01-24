$(function(){
  if ($('#tabTipo').val() == 'C'){
    $('#liClient').addClass('active');
    $('.block article').hide();
    $('.block #client').show();
  }
  else{
    $('#liDriver').addClass('active');
    $('.block article').hide();
    $('.block #driver').show();
  }
  $('ul.tabs li').on('click',function(){
    $('ul.tabs li').removeClass('active');
    $(this).addClass('active')
    $('.block article').hide();
    var activeTab = $(this).find('a').attr('href');
    $(activeTab).show();
  });
})