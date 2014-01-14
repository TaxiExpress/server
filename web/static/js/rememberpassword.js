$(document).ready(function() {
    $('.forgotpassword').click(function(){
    	alert('pasa');
        	$.ajax({
		        type: "GET",
		        url: 'recoverPassword',  
		        data: {
		            csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
		            email: $('#email').val(),
		        },
		        success: function(data) {
		            alert(data);

		        },
		        error: function(data) {
		        	alert("Please report this error1: " + data);
		        }
		    });

        //}
		// $('.overlay-container-password').fadeIn(function() {
		// 	window.setTimeout(function(){
  //               $('.window-container-password.zoomin').addClass('window-container-visible');
  //           }, 100);
  //       });
    });
    $('.closeEmail').click(function() {
        $('.overlay-container-password').fadeOut().end().find('.window-container-password').removeClass('window-container-visible');
    });

});