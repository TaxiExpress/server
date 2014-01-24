$(document).ready(function() {
    $('.close').click(function() {
        $('.overlay-container').fadeOut().end().find('.window-container').removeClass('window-container-visible');
    	$(location).attr('href','/')
    });

    $('.aceptIndex').click(function() {
    	if($("#tipo").is(':checked')) {  
            tipo='C' 
        } else {  
            tipo='D'  
        } 

    	if ($('#phone').val() == "" || $('#validationCode').val() == ""){
        	$('#validation-form .error').html('Debe ingresar un numero de teléfono y código de validación'); 
        }
        else{
			tmpPhone = '+34' + $('#phone').val()
		    $.ajax({
		        type: "POST",
		        url: "/validatecode/",
		        data: {
		            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		            tipo: tipo,
		            phone: tmpPhone,
		            validationCode: $('#validationCode').val() ,
		        },
		        success: function(content) {
		        	if (content == '201'){
		        		if (tipo == 'C'){
		        			$(location).attr('href','mantclient_data.html')
		        		}
		        		else{
		        			$(location).attr('href','mantdriver_data.html')
		        		}	
		    		}
		        	else{
		        		$('#validation-form .error').html(content);
		        	}
		            
		        },
		        error: function(xhr, textStatus, errorThrown) {
		            alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
		        }
	    	});	
        }      
    });

    $('.aceptRegister').click(function() {

    	if ($('#phone').val() == "" || $('#validationCode').val() == ""){
        	$('#validation-form .error').html('Debe ingresar un numero de teléfono y código de validación'); 
        }
        else{
			tmpPhone = '+34' + $('#phone').val()
		    $.ajax({
		        type: "POST",
		        url: "/validatecode/",
		        data: {
		            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		            tipo: $('#tabTipo').val(),
		            phone: tmpPhone,
		            validationCode: $('#validationCode').val() ,
		        },
		        success: function(content) {
		        	if (content == '201'){
		        		if ($('#tabTipo').val() == 'C'){
		        			$(location).attr('href','mantclient_data.html')
		        		}
		        		else{
		        			$(location).attr('href','mantdriver_data.html')
		        		}	
		    		}
		        	else{
		        		$('#validation-form .error').html(content);
		        	}
		            
		        },
		        error: function(xhr, textStatus, errorThrown) {
		            alert("Please report this error: "+errorThrown+xhr.status+xhr.responseText);
		        }
	    	});	
        }      
    });

    $('.validationRefIndex').click(function(){
        if ($('#phone').val() == ""){
        	$('#validation-form .error').html('Debe ingresar un numero de teléfono'); 
        }
        else{
        	tmpPhone = '+34' + $('#phone').val()
	        $.ajax({
		        type: "POST",
		        url: "/recovervalidationcode/",
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

    $('.validationRefRegister').click(function(){
        if ($('#phone').val() == ""){
        	$('#validation-form .error').html('Debe ingresar un numero de teléfono'); 
        }
        else{
        	tmpPhone = '+34' + $('#phone').val()
	        $.ajax({
		        type: "POST",
		        url: "/recovervalidationcode/",
		        data: {
		            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		            tipo: $('#tabTipo').val(),
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

