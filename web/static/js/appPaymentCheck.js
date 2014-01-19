$(document).ready(function() { 
    $("input[name=appPayment]").click(function() {
    	if($("input[name=appPayment]").is(':checked')) {  
	        $("input[name=bankAccount]").attr("disabled",false);
	        $("input[name=recipientName]").attr("disabled",false);
	    } else {  
	        $("input[name=bankAccount]").attr("disabled",true);
	        $("input[name=recipientName]").attr("disabled",true); 
	        $("input[name=bankAccount]").val("");
	        $("input[name=recipientName]").val(""); 
	    } 
	});
});