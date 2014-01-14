$(document).ready(function() { 
    $('ul.tabs li').on('click',function(){
	    var activeTab = $(this).find('a').attr('href');
	    if (activeTab == "#client"){
	    	//Clear Driver fields and mark that it's a Client
	    	$('#createaccountClient input[name=tipo]').val("C");
	    	$('#createaccountDriver input[name=email]').val("");
	    	$('#createaccountDriver input[name=phone]').val("");
	    	$('#createaccountDriver input[name=first_name]').val("");
	    	$('#createaccountDriver input[name=last_name]').val("");				    	
	    	$('#createaccountDriver input[name=password]').val("");
	    	$('#createaccountDriver input[name=passwordCon]').val("");
	    	$('#createaccountDriver input[name=license]').val("");
	    	$('#createaccountDriver input[name=plate]').val("");				    	
	    	$('#createaccountDriver input[name=model]').val("");
	    	$('#createaccountDriver input[name=capacity]').val("");
	    	$('#createaccountDriver select[name=accessible]').val("1");
	    	$('#createaccountDriver select[name=animals]').val("1");
	    	$('#createaccountDriver select[name=appPayment]').val("1");
	    	$('#createaccountDriver input[name=bankAccount]').val("");
	    	$('#createaccountDriver input[name=recipientName]').val("");				          
	    }
	    else{
	    	//Clear Client fields and mark that it's a Driver
	    	$('#createaccountDriver input[name=tipo]').val("D");
	    	$('#createaccountClient input[name=email]').val("");
	    	$('#createaccountClient input[name=phone]').val("");
	    	$('#createaccountClient input[name=password]').val("");
	    	$('#createaccountClient input[name=passwordCon]').val("");
	    }
	});
});