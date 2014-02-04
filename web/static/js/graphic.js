
$('window').ready(function(){

  var f = new Date();
  var MonthNames = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"];
  var DayNames = ["Lun","Mar","Mie","Jue","Vie","Sab","Dom"];

	  
  //Viajes en el ultimo mes
	var posDias = 1;
	var diasMes = new Array();
	  
	$.getJSON('/statistics/gettravelsbylastmonth/', function(json) {
    $.each( json, function( key, val ) {
			diasMes[posDias] = val;
			posDias = posDias + 1;			
		});

    var dias = []
    var dataYear = []
    var l = 0;
    var k = new Date();
    var today = f.getDate();
    console.log("entro");
    while ( (k.getDate()-1) != today ){
      console.log k.getDate();
      dias[l] = k.getDate();
      dataYear[l] = diasMes[k.getDate()];
      k = new Date(k.getTime()-(86400000))
      l++;      
    }
		
		var lineChartData = {
     	labels : dias,	
      datasets : [{
        fillColor : "rgba(120,120,120,0.5)",
        strokeColor : "rgba(120,120,120,1)",
        pointColor : "rgba(120,120,120,1)",
        pointStrokeColor : "#fff",        			
  			data : dataYear
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

		new Chart(document.getElementById("travelsLastMonth").getContext("2d")).Line(lineChartData,options);
	
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
		
    var labels = [];
    var data = [];
    var j = f.getMonth()+1;
    var max = 0;

    for (var i=0; i<12; i++) { 
      labels[i] = MonthNames[j];
      data[i] = viajesUYear[j+1];
      if ((viajesUYear[j+1])>max){
        max = viajesUYear[j+1]
      }
      j++;
      if (j == 12) {
        j = 0;
      }
    }

    var steps = (Math.round(max/5))+1;

		var lineChartData = {
     	labels : labels,
			datasets : [ {
        fillColor : "rgba(120,120,120,0.5)",
        strokeColor : "rgba(120,120,120,1)",
        pointColor : "rgba(120,120,120,1)",
        pointStrokeColor : "#fff",    
				data : data
			}, ]
    };
			
		var options = {
  		scaleShowGridLines: true,
  		scaleOverride: true,
  		scaleSteps: steps,
  		scaleStepWidth: 5,
  		scaleStartValue: 0,
      scaleLineColor: "rgba(0.9,0.2,0,.1)",
  		scaleLineWidth: 0,
  		scaleShowLabels: true,		
  		scaleFontColor: "#000",
  		barDatasetSpacing: 2,
  		barStrokeWidth: 2
  	};

		new Chart(document.getElementById("travelsLastYear").getContext("2d")).Line(lineChartData, options);

	});
	
  //Viajes por mes
  var viajesMes = new Array();
  var pos = 1;
  
  $.getJSON('/statistics/gettravelsbymonth/', function(json) {
    $.each( json, function( key, val ) {
      viajesMes[pos] = val;
      pos = pos + 1;        
    });
    
    var dataMonth = []
    for (var i=0; i<13; i++) { 
      dataMonth[i] = viajesMes[i+1];
    }

    var barChartData = {
      labels : MonthNames,
      datasets : [{
        fillColor : "rgba(120,120,120,0.5)",
        strokeColor : "rgba(120,120,120,1)",
        pointColor : "rgba(120,120,120,1)",
        pointStrokeColor : "#fff",    
        data : dataMonth
      },]
    };
      
    var options = { 
      scaleShowGridLines: true,
      scaleOverride: true,
      scaleSteps: 4,
      scaleStepWidth: 25,
      scaleStartValue: 0,
      scaleLineColor: "rgba(0.9,0.2,0,.1)",
      scaleLineWidth: 0,
      scaleShowLabels: true,
      scaleFontColor: "#000",
      barDatasetSpacing: 2,
      barStrokeWidth: 2
    };
      
    new Chart(document.getElementById("travelsByMonth").getContext("2d")).Bar(barChartData, options);

  });
	  
  //Viajes por dia
  var posi = 0;
	var viajesDias = new Array();
	  
	$.getJSON('/statistics/gettravelsbyday/', function(json) {
    $.each( json, function( key, val ) {
			viajesDias[posi] = val;
			posi = posi + 1;
		});
		
    var dataDaysWeek = []
    for (var i=0; i<7; i++) { 
      dataDaysWeek[i] = viajesDias[i];
    }

  	var barChartData = {
     	labels : DayNames,
			datasets : [{
  			fillColor : "rgba(120,120,120,0.5)",
  			strokeColor : "rgba(120,120,120,1)",
  			pointColor : "rgba(120,120,120,1)",
  			pointStrokeColor : "#fff",		
				data : dataDaysWeek
			}, ]
  	};
	
  	var options = {					
  		scaleShowGridLines: true,
  		scaleOverride: true,
  		scaleSteps: 4,
  		scaleStepWidth: 25,
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
