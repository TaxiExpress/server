$(document).ready(function() {
    $('.close').click(function() {
        $('.overlay-container').fadeOut().end().find('.window-container').removeClass('window-container-visible');
    });
    $('.acept').click(function() {
        //alert('aceptar');
        $.ajax({
	        type: "POST",
	        url: 'validateCode',  
	        data: {
	            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
	            tipo: $('.tipo').val(),
	            email: $('#phone').val()
	        },
	        success: function(data) {


	        },
	        error: function(data) {

	        }
	    });
    });
    $('.validationRef').click(function(){
        //Volver a pedir codigo de validación
        alert("codigo de validación");
     });
});

