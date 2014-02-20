function validateClientPassword() { 
    
    var errorString = ''; 
    var result = true ; 
     

    //The new passwords must be the same
    if ($('#mantclient input[name=newPassAux]').val() != $('#mantclient input[name=newPass2]').val()) { 
        errorString = 'Los valores de las nuevas contraseñas deben ser iguales';
        result = false; 
    } 
    else{
        //The password's length must be between 8 and 20
        if ((($('#mantclient input[name=newPassAux]').val()).length < '8') || (($('#mantclient input[name=newPass2]').val()).length > '20')) {
            errorString = 'La contraseña debe tener entre 8 y 20 caracteres';
            result = false; 
        }
    }

    if (result == false) {
        $('#mantclient .passwordError').addClass('showfieldError');
        $('#mantclient .passwordError').removeClass('hidefieldError');
        $('#mantclient .registerError').html(errorString); 
    }
    else{
        $('#mantclient .passwordError').removeClass('showfieldError');
        $('#mantclient .passwordError').addClass('hidefieldError');
        $('#mantclient .registerError').html(''); 
    }

    tx =  $('#mantclient #oldPassAux').val();    
    i = 0;
    while (i < 5000)
    {
        hashObj = new jsSHA(tx, "TEXT");
        tx = hashObj.getHash("SHA-256", "HEX");
        i++;
    }
    $('#mantclient #oldPass').val(tx);  

    tx =  $('#mantclient #newPassAux').val();    
    i = 0;
    while (i < 5000)
    {
        hashObj = new jsSHA(tx, "TEXT");
        tx = hashObj.getHash("SHA-256", "HEX");
        i++;
    }
    $('#mantclient #newPass').val(tx); 

    return result;
}

function validateDriverPassword() { 
    
    var errorString = ''; 
    var result = true ; 
    

    //The new passwords must be the same
    if ($('#mantdriver input[name=newPassAux]').val() != $('#mantdriver input[name=newPass2]').val()) { 
        errorString = 'Los valores de las nuevas contraseñas deben ser iguales';
        result = false; 
    } 
    else{
        //The password's length must be between 8 and 20
        if ((($('#mantdriver input[name=newPassAux]').val()).length < '8') || (($('#mantdriver input[name=newPass2]').val()).length > '20')) {
            errorString = 'La contraseña debe tener entre 8 y 20 caracteres';
            result = false; 
        }
    }

   
    if (result == false) {
        $('#mantdriver .passwordError').addClass('showfieldError');
        $('#mantdriver .passwordError').removeClass('hidefieldError');
        $('#mantdriver .registerError').html(errorString); 
    }
    else{
        $('#mantdriver .passwordError').removeClass('showfieldError');
        $('#mantdriver .passwordError').addClass('hidefieldError');
        $('#mantdriver .registerError').html(''); 
    }

    tx =  $('#mantdriver #oldPassAux').val();    
    i = 0;
    while (i < 5000)
    {
        hashObj = new jsSHA(tx, "TEXT");
        tx = hashObj.getHash("SHA-256", "HEX");
        i++;
    }
    $('#mantdriver #oldPass').val(tx);  

    tx =  $('#mantdriver #newPassAux').val();    
    i = 0;
    while (i < 5000)
    {
        hashObj = new jsSHA(tx, "TEXT");
        tx = hashObj.getHash("SHA-256", "HEX");
        i++;
    }
    $('#mantdriver #newPass').val(tx); 

    return result;
}

function validatePassword() { 
    
    var errorString = ''; 
    var result = true ; 
     
    //The new passwords must be the same
    if ($('#resetPass input[name=newPassAux]').val() != $('#resetPass input[name=newPass2]').val()) { 
        errorString = 'Los valores de las nuevas contraseñas deben ser iguales';
        result = false; 
    } 
    else{
        //The password's length must be between 8 and 20
        if ((($('#resetPass input[name=newPassAux]').val()).length < '8') || (($('#resetPass input[name=newPass2]').val()).length > '20')) {
            errorString = 'La contraseña debe tener entre 8 y 20 caracteres';
            result = false; 
        }
    }

    if (result == false) {
        $('#resetPass .passwordError').addClass('showfieldError');
        $('#resetPass .passwordError').removeClass('hidefieldError');
        $('#resetPass .registerErrorRec').html(errorString); 
    }
    else{
        $('#resetPass .passwordError').removeClass('showfieldError');
        $('#resetPass .passwordError').addClass('hidefieldError');
        $('#resetPass .registerErrorRec').html(''); 
    }

    tx =  $('#resetPass #newPassAux').val();    
    i = 0;
    while (i < 5000)
    {
        hashObj = new jsSHA(tx, "TEXT");
        tx = hashObj.getHash("SHA-256", "HEX");
        i++;
    }
    $('#resetPass #newPass').val(tx); 

    return result;
}