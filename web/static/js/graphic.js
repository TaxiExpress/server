
$('window').ready(function(){

	var viajesMes = new Array();
	var pos = 1;
	
	$.getJSON('/statistics/gettravelsbymonth/', function(json) {
            $.each( json, function( key, val ) {
			
				viajesMes[pos] = val;
				pos = pos + 1;
				
		});
		
		var lineChartData = 
			{
            	
            	labels : ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],
				datasets : [
            	{
            			fillColor : "rgba(220,120,120,0.5)",
            			strokeColor : "rgba(220,120,120,1)",
            			pointColor : "rgba(220,120,120,1)",
            			pointStrokeColor : "#fff",
						data : [viajesMes[1],viajesMes[2],viajesMes[3],viajesMes[4],viajesMes[5],viajesMes[6],viajesMes[7],viajesMes[8],
						viajesMes[9],viajesMes[10],viajesMes[11],viajesMes[12]]
				},  ]
			
			};
			
				var options = { 
						
						scaleShowGridLines: true,
						scaleOverride: true,
						scaleSteps: 2,
						scaleStepWidth: 10,
						scaleStartValue: 0,
						scaleLineColor: "rgba(0,0.7,0,.1)",
						scaleLineWidth: 0,
						scaleShowLabels: true,
						
						scaleFontColor: "#000",
						barDatasetSpacing: 2,
						barStrokeWidth: 2
					};
			

			new Chart(document.getElementById("line").getContext("2d")).Line(lineChartData,options);
	
      });
	  
		var posDias = 1;
		var dias = new Array();
		var diasMes = new Array();
	  
			$.getJSON('/statistics/gettravelsbylastmonth/', function(json) {
            $.each( json, function( key, val ) {
				
				diasMes[posDias] = val;
				dias[posDias] = key;
				posDias = posDias + 1;
				
			});
		
		var barChartData = 
			{
            	labels : [dias[1],dias[2],dias[3],dias[4],dias[5],dias[6],
            			dias[7],dias[8],dias[9],dias[10],dias[11],dias[12],
            			dias[13],dias[14],dias[15],dias[16],dias[17],dias[18],
            			dias[19],dias[20],dias[21],dias[22],dias[23],dias[24],
            			dias[25],dias[26],dias[27],dias[28],dias[29],dias[30],dias[31]],
				datasets : [
            	{
            			fillColor : "rgba(120,220,120,0.5)",
            			strokeColor : "rgba(120,220,120,1)",
            			pointColor : "rgba(120,220,120,1)",
            			pointStrokeColor : "#fff",           			
						data : [diasMes[1],diasMes[2],diasMes[3],diasMes[4],diasMes[5],diasMes[6],
            			diasMes[7],diasMes[8],diasMes[9],diasMes[10],diasMes[11],diasMes[12],
            			diasMes[13],diasMes[14],diasMes[15],diasMes[16],diasMes[17],diasMes[18],
            			diasMes[19],diasMes[20],diasMes[21],diasMes[22],diasMes[23],diasMes[24],
            			diasMes[25],diasMes[26],diasMes[27],diasMes[28],diasMes[29],diasMes[30],diasMes[31]]
				},  ]
			
			};
			
				var options2 = { 
						
						scaleShowGridLines: true,
						scaleOverride: true,
						scaleSteps: 2,
						scaleStepWidth: 4,
						scaleStartValue: 0,
						scaleLineColor: "rgba(0,0.7,0,.1)",
						scaleLineWidth: 0,
						scaleShowLabels: true,
						
						scaleFontColor: "#000",
						barDatasetSpacing: 2,
						barStrokeWidth: 2
					};

			new Chart(document.getElementById("bar").getContext("2d")).Bar(barChartData,options2);
			
	
      });



		var posMes = 1;
		var meses = new Array();
		var viajesUYear = new Array();
	  
			$.getJSON('/statistics/gettravelsbylastyear/', function(json) {
            $.each( json, function( key, val ) {
				
				viajesUYear[posMes] = val;
				meses[posMes] = key;
				posMes = posMes + 1;
				
			});
		
		var barChartData2 = 
			{
            	
            	labels : ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"],
				datasets : [
            	{
            			fillColor : "rgba(120,220,120,0.5)",
            			strokeColor : "rgba(120,220,120,1)",
            			pointColor : "rgba(120,220,120,1)",
            			pointStrokeColor : "#fff",

						data : [viajesUYear[1],viajesUYear[2],viajesUYear[3],viajesUYear[4],viajesUYear[5],viajesUYear[6],
            			viajesUYear[7],viajesUYear[8],viajesUYear[9],viajesUYear[10],viajesUYear[11],viajesUYear[12]]

				},  ]
			
			};
			
				var options2 = { 
						
						scaleShowGridLines: true,
						scaleOverride: true,
						scaleSteps: 2,
						scaleStepWidth: 6,
						scaleStartValue: 0,
						scaleLineColor: "rgba(0,0.7,0,.1)",
						scaleLineWidth: 0,
						scaleShowLabels: true,
						
						scaleFontColor: "#000",
						barDatasetSpacing: 2,
						barStrokeWidth: 2
					};

			new Chart(document.getElementById("bar2").getContext("2d")).Bar(barChartData2,options2);


		});

	  
		var posHora = 0;
		var viajesHoras = new Array();
		var horas = new Array();
			
		$.getJSON('/statistics/gettravelsbyhour/', function(json) {
            $.each( json, function( key, val ) {
				
				viajesHoras[posHora] = val;
				horas[posHora] = key;
				posHora = posHora + 1;

		});
		
		var BarChartData2 = 
			{
            	labels : [horas[0],horas[1],horas[2],horas[3],horas[4],horas[5],horas[6],horas[7],horas[8],horas[9],horas[10],horas[11],horas[12],
						 horas[13],horas[14],horas[15],horas[16],horas[17],horas[18],horas[19],horas[20],horas[21],horas[22],horas[23]],
				datasets : [
            	{
            			fillColor : "rgba(120,120,220,0.5)",
            			strokeColor : "rgba(120,120,220,1)",
            			pointColor : "rgba(120,120,220,1)",
            			pointStrokeColor : "#fff",

				data : [viajesHoras[0],viajesHoras[1],viajesHoras[2],viajesHoras[3],viajesHoras[4],viajesHoras[5],viajesHoras[6],viajesHoras[7],
				viajesHoras[8],viajesHoras[9],viajesHoras[10],viajesHoras[11],viajesHoras[12],viajesHoras[13],viajesHoras[14],viajesHoras[15],
				viajesHoras[16],viajesHoras[17],viajesHoras[18],viajesHoras[19],viajesHoras[20],viajesHoras[21],viajesHoras[22],viajesHoras[23]]
				
				},  ]
				
			};
			
				var options4 = { 
						
						scaleShowGridLines: true,
						scaleOverride: true,
						scaleSteps: 2,
						scaleStepWidth: 4,
						scaleStartValue: 0,
						scaleLineColor: "rgba(0.9,0.2,0,.1)",
						scaleLineWidth: 0,
						scaleShowLabels: true,
						
						scaleFontColor: "#000",
						barDatasetSpacing: 2,
						barStrokeWidth: 2
					};

			new Chart(document.getElementById("line2").getContext("2d")).Bar(BarChartData2,options4);
	
      });
	  
		var posi = 0;
		var viajesDias = new Array();
	  
		$.getJSON('/statistics/gettravelsbyday/', function(json) {
            $.each( json, function( key, val ) {
				
				viajesDias[posi] = val;
				posi = posi + 1;
				
			});
		
			var BarChartData3 = 
			{
            	
            	labels : ["Lunes","Martes","Miercoles","Jueves","Viernes","Sabado","Domingo"],
				datasets : [
            	{
            			fillColor : "rgba(120,120,120,0.5)",
            			strokeColor : "rgba(120,120,120,1)",
            			pointColor : "rgba(120,120,120,1)",
            			pointStrokeColor : "#fff",
            			
				data : [viajesDias[0],viajesDias[1],viajesDias[2],viajesDias[3],viajesDias[4],viajesDias[5],viajesDias[6]]
				
				},  ]
				
			};
			
				var options3 = { 
						
						scaleShowGridLines: true,
						scaleOverride: true,
						scaleSteps: 2,
						scaleStepWidth: 4,
						scaleStartValue: 0,
						scaleLineColor: "rgba(0.9,0.2,0,.1)",
						scaleLineWidth: 0,
						scaleShowLabels: true,
						
						scaleFontColor: "#000",
						barDatasetSpacing: 2,
						barStrokeWidth: 2
					};

			new Chart(document.getElementById("line3").getContext("2d")).Bar(BarChartData3,options3);
	
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
