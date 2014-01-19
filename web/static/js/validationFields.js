function validateClient() { 
    // fieldValue is a Form Plugin method that can be invoked to find the 
    // current value of a field 
      
    var errorString = ''; 
    var result = true ; 

    var passwordValue = $('#createaccountClient input[name=password]').fieldValue(); 
    var repeatPasswordValue = $('#createaccountClient input[name=passwordCon]').fieldValue();         
    // passwordValue and repeatPasswordValue are arrays

    //The password must be the same
    if (passwordValue[0] != repeatPasswordValue[0]) { 
        errorString = 'Los valores de la contraseña deben ser iguales';
        result = false; 
    } 
    else{
        //The password's length must be between 8 and 20
        if ((passwordValue[0].length < '8') || (passwordValue[0].length > '20')) {
            errorString = 'La contraseña debe tener entre 8 y 20 caracteres';
            result = false; 
        }
    }

   
    if (result == false) {
        $('#createaccountClient .passwordError').addClass('showfieldError');
        $('#createaccountClient .passwordError').removeClass('hidefieldError');
        $('#createaccountClient .registerError').html(errorString); 
    }
    else{
        $('#createaccountClient .passwordError').removeClass('showfieldError');
        $('#createaccountClient .passwordError').addClass('hidefieldError');
        $('#createaccountClient .registerError').html(''); 
    }
    return result;
}
function validateDriver() { 
    // fieldValue is a Form Plugin method that can be invoked to find the 
    // current value of a field 
    $('#createaccountDriver .passwordError').removeClass('showfieldError');
    $('#createaccountDriver .passwordError').addClass('hidefieldError');
    $('#createaccountDriver .accountError').removeClass('showfieldError');
    $('#createaccountDriver .accountError').addClass('hidefieldError');   
    var errorString = ''; 
    var result = true ; 


    var passwordValue = $('#createaccountDriver input[name=password]').fieldValue(); 
    var repeatPasswordValue = $('#createaccountDriver input[name=passwordCon]').fieldValue();   

    // passwordValue and repeatPasswordValue are arrays

    //The password must be the same
    if (passwordValue[0] != repeatPasswordValue[0]) { 
        $('.passwordError').addClass('showfieldError');
        $('.passwordError').removeClass('hidefieldError');
        errorString = 'Los valores de la contraseña deben ser iguales';
        result = false; 
    } 
    else{
        //The password's length must be between 8 and 20
        if ((passwordValue[0].length < '8') || (passwordValue[0].length > '20')) {
            $('.passwordError').addClass('showfieldError');
            $('.passwordError').removeClass('hidefieldError');
            errorString = 'La contraseña debe tener entre 8 y 20 caracteres';
            result = false; 
        }
    }

    //If the value of AppPayment is 'Si' the value of 'bankAccount' and 'recipientName'  must be set
    if($("input[name=appPayment]").is(':checked')) {  
        if ($('input[name=bankAccount]').fieldValue() == '' || $('input[name=recipientName]').fieldValue() == ''){
            if (errorString == ''){          
                errorString = 'Debe introducir Número de cuenta bancaria y Titular de la cuenta';
            }
            else{
                errorString = errorString + '<br />' + 'Debe introducir Número de cuenta bancaria y Titular de la cuenta';
            }
            $('#createaccountDriver .accountError').addClass('showfieldError');
            $('#createaccountDriver .accountError').removeClass('hidefieldError');    
            result = false;
        }
    } 

    if (result == false) {
        $('#createaccountDriver .registerError').html(errorString); 
    }
    else{
        $('#createaccountDriver .registerError').html(''); 
    }
    return result;
}

function ConcatPrefixPhone(){
        $('#phone').val("+34" + $('#phone').val());
}