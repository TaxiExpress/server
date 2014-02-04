
$('window').ready(function(){

  //Viajes por mes
	var viajesMes = new Array();
	var pos = 1;
	
	$.getJSON('/statistics/gettravelsbymonth/', function(json) {
    $.each( json, function( key, val ) {
			viajesMes[pos] = val;
			pos = pos + 1;				
		});
		
		var barChartData = {
      labels : ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],
			datasets : [{
        fillColor : "rgba(120,120,120,0.5)",
        strokeColor : "rgba(120,120,120,1)",
        pointColor : "rgba(120,120,120,1)",
        pointStrokeColor : "#fff",    
				data : [viajesMes[1],viajesMes[2],viajesMes[3],viajesMes[4],viajesMes[5],viajesMes[6],viajesMes[7],viajesMes[8],viajesMes[9],viajesMes[10],viajesMes[11],viajesMes[12]]
			},]
		};
			
		var options = { 
			scaleShowGridLines: true,
			scaleOverride: true,
			scaleSteps: 2,
			scaleStepWidth: 5,
			scaleStartValue: 0,
      scaleLineColor: "rgba(0.9,0.2,0,.1)",
			scaleLineWidth: 0,
			scaleShowLabels: true,
			scaleFontColor: "#000",
			barDatasetSpacing: 2,
			barStrokeWidth: 2
		};
			
    new Chart(document.getElementById("travelsByMonth").getContext("2d")).Line(lineChartData, options);

  });
	  
  //Viajes en el ultimo mes
	var posDias = 1;
	var dias = new Array();
	var diasMes = new Array();
	  
	$.getJSON('/statistics/gettravelsbylastmonth/', function(json) {
    $.each( json, function( key, val ) {
			diasMes[posDias] = val;
			dias[posDias] = key;
			posDias = posDias + 1;			
		});
		
		var lineChartData = {
     	labels : [dias[1],dias[2],dias[3],dias[4],dias[5],dias[6],
           			dias[7],dias[8],dias[9],dias[10],dias[11],dias[12],
          			dias[13],dias[14],dias[15],dias[16],dias[17],dias[18],
          			dias[19],dias[20],dias[21],dias[22],dias[23],dias[24],
          			dias[25],dias[26],dias[27],dias[28],dias[29],dias[30],dias[31]
               ],	
      datasets : [{
        fillColor : "rgba(120,120,120,0.5)",
        strokeColor : "rgba(120,120,120,1)",
        pointColor : "rgba(120,120,120,1)",
        pointStrokeColor : "#fff",        			
  			data : [diasMes[1],diasMes[2],diasMes[3],diasMes[4],diasMes[5],diasMes[6],
            		diasMes[7],diasMes[8],diasMes[9],diasMes[10],diasMes[11],diasMes[12],
            		diasMes[13],diasMes[14],diasMes[15],diasMes[16],diasMes[17],diasMes[18],
            		diasMes[19],diasMes[20],diasMes[21],diasMes[22],diasMes[23],diasMes[24],
            		diasMes[25],diasMes[26],diasMes[27],diasMes[28],diasMes[29],diasMes[30],diasMes[31]
               ]
			},]
	  };
			
		var options = { 
			scaleShowGridLines: true,
			scaleOverride: true,
			scaleSteps: 2,
			scaleStepWidth: 5,
			scaleStartValue: 0,
      scaleLineColor: "rgba(0.9,0.2,0,.1)",
			scaleLineWidth: 0,
			scaleShowLabels: true,
			scaleFontColor: "#000",
			barDatasetSpacing: 2,
			barStrokeWidth: 2
		};

		new Chart(document.getElementById("travelsLastMonth").getContext("2d")).Bar(lineChartData,options);
	
  });


  //Viajes en el último año
	var posMes = 1;
	var meses = new Array();
	var viajesUYear = new Array();
	  
	$.getJSON('/statistics/gettravelsbylastyear/', function(json) {
    $.each( json, function( key, val ) {
			viajesUYear[posMes] = val;
			meses[posMes] = key;
			posMes = posMes + 1;
  	});
		
		var lineChartData = {
     	labels : ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"],
			datasets : [ {
        fillColor : "rgba(120,120,120,0.5)",
        strokeColor : "rgba(120,120,120,1)",
        pointColor : "rgba(120,120,120,1)",
        pointStrokeColor : "#fff",    
				data : [viajesUYear[1],viajesUYear[2],viajesUYear[3],viajesUYear[4],viajesUYear[5],viajesUYear[6],viajesUYear[7],viajesUYear[8],viajesUYear[9],viajesUYear[10],viajesUYear[11],viajesUYear[12]]
			}, ]
    };
			
		var options = {
  		scaleShowGridLines: true,
  		scaleOverride: true,
  		scaleSteps: 2,
  		scaleStepWidth: 5,
  		scaleStartValue: 0,
      scaleLineColor: "rgba(0.9,0.2,0,.1)",
  		scaleLineWidth: 0,
  		scaleShowLabels: true,		
  		scaleFontColor: "#000",
  		barDatasetSpacing: 2,
  		barStrokeWidth: 2
  	};

		new Chart(document.getElementById("travelsLastYear").getContext("2d")).Bar(lineChartData, options);

	});
	
	  
  //Viajes por dia
  var posi = 0;
	var viajesDias = new Array();
	  
	$.getJSON('/statistics/gettravelsbyday/', function(json) {
    $.each( json, function( key, val ) {
			viajesDias[posi] = val;
			posi = posi + 1;
		});
		
  	var barChartData = {
     	labels : ["Lun","Mar","Mie","Jue","Vie","Sab","Dom"],
			datasets : [{
  			fillColor : "rgba(120,120,120,0.5)",
  			strokeColor : "rgba(120,120,120,1)",
  			pointColor : "rgba(120,120,120,1)",
  			pointStrokeColor : "#fff",		
				data : [viajesDias[0],viajesDias[1],viajesDias[2],viajesDias[3],viajesDias[4],viajesDias[5],viajesDias[6]]
			}, ]
  	};
	
  	var options = {					
  		scaleShowGridLines: true,
  		scaleOverride: true,
  		scaleSteps: 2,
  		scaleStepWidth: 5,
  		scaleStartValue: 0,
  		scaleLineColor: "rgba(0.9,0.2,0,.1)",
  		scaleLineWidth: 0,
  		scaleShowLabels: true,
  		scaleFontColor: "#000",
  		barDatasetSpacing: 2,
  		barStrokeWidth: 2
  	};

  	new Chart(document.getElementById("travelsByDay").getContext("2d")).Bar(barChartData, options);
	
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
