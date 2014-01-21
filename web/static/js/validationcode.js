$(document).ready(function() {
    $('.close').click(function() {
        $('.overlay-container').fadeOut().end().find('.window-container').removeClass('window-container-visible');
    });
    $('.acept').click(function() {
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
    	if ($('#phone').val() == ""){
        	$('#validation-form .error').html('Debe ingresar un numero de teléfono'); 
        }
        else{
        	tmpPhone = '+34' + $('#phone').val()
	        $.ajax({
		        type: "POST",
		        url: "/recoverValidationCode/",
		        data: {
		            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		            tipo: $('.tipo').val(),
		            phone: tmpPhone,
		        },
		        success: function(content) {
		            $('#validation-form .error').html(content);
		        },
		        error: function(xhr, textStatus, errorThrown) {
		            alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
		        }
	    	});	
    	}	
     });
});

