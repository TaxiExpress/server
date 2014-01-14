function openAccordion(id) {
	if ($('#' + id + ' .textAccordion').is(":hidden")) {
        //Plegamos todos
        $('.textAccordion').slideUp();
        $('.titleAccordion').removeClass('titleAccordionActivo');
        //Desplegamos el seleccionado
        $('#' + id + ' .textAccordion').slideDown();
        $('#' + id + ' .titleAccordion').addClass('titleAccordionActivo');

    } else {
        //Buscamos el elemento:
        if($('#' + id + ' .titleAccordion').hasClass('titleAccordionActivo')){
            $('#' + id + ' .titleAccordion').removeClass('titleAccordionActivo');
	}
        //Plegamos todos
    
    $('.textAccordion').slideUp();
    
    }       
}      

$(document).ready(function () {
      //Aquí escribimos las vinculaciones a EVENTOS de los elementos del DOM
      //Se ocultan todos los textos de contenido de los menús
      $('.textAccordion').hide();
      //Asociamos al evento onclick de los elementos del acordeon la función abrirAcordeon
      $('.titleAccordion').on("click", function (event) {
          //Recuperar el identificativo del menú que se ha pulsado. Se recupera el Id del padre (en nuestro caso el DIV que contiene el id y clase = "accordion")
          //El event.target recupera el del elemento pinchado
          var ident = $(event.target).parent().attr('id');
          //Llamar al método que despliega el menú pinchado
          openAccordion(ident);
      });
      
});
