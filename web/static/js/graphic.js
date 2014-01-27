
$('.pruebaJson').click(function(){
	var viajes = new Array();
	var indices = new Array();
	var pos = 1;
	
	$.getJSON('/statistics/gettravelsbymonth/', function(json) {
            $.each( json, function( key, val ) {
				
				viajes[pos] = val;
				indices[pos] = key;
				pos = pos + 1;
		});
		
		var lineChartData = 
			{
            	
            	labels : [indices[1],indices[2],indices[3],indices[4],indices[5],indices[6],indices[7],indices[8],indices[9],indices[10],indices[11],indices[12]],
				datasets : [
            	{
            			fillColor : "rgba(220,220,220,0.5)",
            			strokeColor : "rgba(220,220,220,1)",
            			pointColor : "rgba(220,220,220,1)",
            			pointStrokeColor : "#fff",
						data : [viajes[1],viajes[2],viajes[3],viajes[4],viajes[5],viajes[6],viajes[7],viajes[8],viajes[9],viajes[10],viajes[11],viajes[12]]
				},  ]
			
			};

			new Chart(document.getElementById("line").getContext("2d")).Line(lineChartData);
	
      });
	  
		var pos2 = 1;
		var viajes1 = new Array();
		var anyos = new Array();
	  
			$.getJSON('/statistics/gettravelsbyyear/', function(json) {
            $.each( json, function( key, val ) {
				
				viajes1[pos2] = val;
				anyos[pos2] = key;
				pos2 = pos2 + 1;
				
			});
		
		var barChartData = 
			{
            	labels : [anyos[1],anyos[2],anyos[3]],
				datasets : [
            	{
            			fillColor : "rgba(220,220,220,0.5)",
            			strokeColor : "rgba(220,220,220,1)",
            			pointColor : "rgba(220,220,220,1)",
            			pointStrokeColor : "#fff",           			
						data : [viajes1[1],viajes1[2],viajes1[3]]
				},  ]
			
			};

			new Chart(document.getElementById("bar").getContext("2d")).Bar(barChartData);
	
      });
	  
		var pos3 = 1;
		var viajes2 = new Array();
		var horas = new Array();
			
		$.getJSON('/statistics/gettravelsbyhour/', function(json) {
            $.each( json, function( key, val ) {
				
				viajes2[pos3] = val;
				horas[pos3] = key;
				pos3 = pos3 + 1;
		});
		
		var lineChartData2 = 
			{
            	labels : [horas[1],horas[2],horas[3],horas[4],horas[5],horas[6],horas[7],horas[8],horas[9],horas[10],horas[11],horas[12],
						 horas[13],horas[14],horas[15],horas[16],horas[17],horas[18],horas[19],horas[20],horas[21],horas[22],horas[23]],
				datasets : [
            	{
            			fillColor : "rgba(220,220,220,0.5)",
            			strokeColor : "rgba(220,220,220,1)",
            			pointColor : "rgba(220,220,220,1)",
            			pointStrokeColor : "#fff",
				data : [viajes2[1],viajes2[2],viajes2[3],viajes2[4],viajes2[5],viajes2[6],viajes2[7],viajes2[8],viajes2[9],viajes2[10],viajes2[11],viajes2[12],
						 viajes2[13],viajes2[14],viajes2[15],viajes2[16],viajes2[17],viajes2[18],viajes2[19],viajes2[20],viajes2[21],viajes2[22],viajes2[23]]
				
				},  ]
			
			};

			new Chart(document.getElementById("line2").getContext("2d")).Line(lineChartData2);
	
      });
	  
		var posi = 0;
		var viajesDias = new Array();
		var dias = new Array();
	  
		$.getJSON('/statistics/gettravelsbyday/', function(json) {
            $.each( json, function( key, val ) {
				
				viajesDias[posi] = val;
				dias[posi] = key;
				posi = posi + 1;
				
		});
		
			var lineChartData3 = 
			{
            	
            	labels : ["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"],
				datasets : [
            	{
            			fillColor : "rgba(220,220,220,0.5)",
            			strokeColor : "rgba(220,220,220,1)",
            			pointColor : "rgba(220,220,220,1)",
            			pointStrokeColor : "#fff",
            			
				data : [viajesDias[0],viajesDias[1],viajesDias[2],viajesDias[3],viajesDias[4],viajesDias[5],viajesDias[6]]
				
				},  ]
			
			};

			new Chart(document.getElementById("line3").getContext("2d")).Line(lineChartData3);
	
      });
	  
		
		
    });


/*
var doughnutData = [
				{
					value: 30,
					color:"#F7464A"
				},
				{
					value : 50,
					color : "#46BFBD"
				},
				{
					value : 100,
					color : "#FDB45C"
				},
				{
					value : 40,
					color : "#949FB1"
				},
				{
					value : 120,
					color : "#4D5360"
				}
			
			];

*/
