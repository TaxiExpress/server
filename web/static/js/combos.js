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
                pais = result[i];
                options += "<option value='" + pais.code + "'>" + pais.name + "</option>";
            }        
        },
        error: function(xhr, textStatus, errorThrown) {
            alert("Please report this error: " + errorThrown + xhr.status + xhr.responseText);
        }
    });   


    // options = "<option value='" + "0" + "'>" + "Seleccione país..." + "</option>";
    // options += "<option value='" + "108" + "'>" + "España" + "</option>";
    // options += "<option value='" + "109" + "'>" + "Francia" + "</option>";
    $('#country').html(options);

	$('.cbocountry').change(function() {
		posicion=document.getElementById('country').options.selectedIndex; 
    	codCountry=document.getElementById('country').options[posicion].value;
    	//Llamada al servidor para recuperar las provincias del pais seleccionado
    	if (codCountry == "108"){
    		options = "<option value='" + "0" + "'>" + "Seleccione provincia..." + "</option>";
    		options += "<option value='" + "48" + "'>" + "Bizkaia" + "</option>";
    		options += "<option value='" + "49" + "'>" + "Zamora" + "</option>";
    		$('#state').html(options);
    	}
    	else if(codCountry == "109"){
    		$('#state').html("");
    		$('#city').html("");
    	}
        
    });

    $('.cbostate').change(function() {
    	posicion=document.getElementById('state').options.selectedIndex; 
        codState=document.getElementById('state').options[posicion].value;
        //Llamada al servidor para recuperar los municipio de la provincia seleccionada
    	if (codState == "48"){
    		options = "<option value='" + "0" + "'>" + "Seleccione Municipio..." + "</option>";
    		options += "<option value='" + "013" + "'>" + "Barakaldo" + "</option>";
    		options += "<option value='" + "016" + "'>" + "Berango" + "</option>";
    		options += "<option value='" + "020" + "'>" + "Bilbao" + "</option>";
    		options += "<option value='" + "089" + "'>" + "Urduliz" + "</option>";
    		$('#city').html(options);
    	}
    	else if(codState == "49"){
    		options = "<option value='" + "0" + "'>" + "Seleccione Municipio..." + "</option>";
    		options += "<option value='" + "013" + "'>" + "Zamora1" + "</option>";
    		options += "<option value='" + "016" + "'>" + "Zamora2" + "</option>";
    		options += "<option value='" + "020" + "'>" + "Zamora3" + "</option>";
    		options += "<option value='" + "089" + "'>" + "Zamora4" + "</option>";
    		$('#city').html(options);
    	}
    });

    // $('.cbocity').change(function() {
    // 	posicion=document.getElementById('city').options.selectedIndex; 
    //     codCity=document.getElementById('city').options[posicion].value;
    //     alert(codCity);
    // });	
});
