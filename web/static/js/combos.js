$(document).ready(function() {
    //Llamada al servidor para recuperar los paises
    options = "";
    $.ajax({
        type: "GET",
        url: "/getcountries/",
        success: function(result) {
            if (result.length != 0){
                options = "<option value='" + "0" + "'>" + "Seleccione país..." + "</option>";
            }
            for (i = 0, len = result.length; i < len; i++) {
            	country = result[i];
                options += "<option value='" + country.code + "'>" + country.name + "</option>";
            } 
            $('#country').html(options);
        },
        error: function(xhr, textStatus, errorThrown) {
            alert("Please report this error: " + errorThrown + xhr.status + xhr.responseText);
        }
    });   

    $('.cbocountry').change(function() {
    	posicion=document.getElementById('country').options.selectedIndex; 
    	codCountry=document.getElementById('country').options[posicion].value;
    	if (codCountry != "0"){
    	    //Llamada al servidor para recuperar las provincias del pais seleccionado
    	    $.ajax({
                type: "GET",
                url: "/getstates/",
                data:{country: codCountry},
                success: function(result) {
                    if (result.length != 0){
                        options = "<option value='" + "0" + "'>" + "Seleccione provincia..." + "</option>";
                    }
                    else{
            	        $('#state').html("");
    		            $('#city').html("")
                    }
                    for (i = 0, len = result.length; i < len; i++) {
            	        state = result[i];
                        options += "<option value='" + state.code + "'>" + state.name + "</option>";
                    } 
                    $('#state').html(options);
                },
                error: function(xhr, textStatus, errorThrown) {
                    alert("Please report this error: " + errorThrown + xhr.status + xhr.responseText);
                }
            });
    	}
    	else{
    	    $('#state').html("");
    	    $('#city').html("")
    	}
    });

    $('.cbostate').change(function() {
    	posicion=document.getElementById('state').options.selectedIndex; 
        codState=document.getElementById('state').options[posicion].value;
        if (codState != "0"){
            //Llamada al servidor para recuperar los municipio de la provincia seleccionada
            $.ajax({
                type: "GET",
                url: "/getcities/",
                data:{state: codState},
                success: function(result) {
                    if (result.length != 0){
                       options = "<option value='" + "0" + "'>" + "Seleccione municipio..." + "</option>";
                    }
                    else{
    		            $('#city').html("")
                    }
                    for (i = 0, len = result.length; i < len; i++) {
            	        city = result[i];
                        options += "<option value='" + city.code + "'>" + city.name + "</option>";
                    } 
                    $('#city').html(options);
                },
                error: function(xhr, textStatus, errorThrown) {
                    alert("Please report this error: " + errorThrown + xhr.status + xhr.responseText);
                }
            });
        }
        else{
            $('#city').html("")
        }
    });
});
