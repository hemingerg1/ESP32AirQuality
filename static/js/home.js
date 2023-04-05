$(function(){

// Page locations for charts
var tempChartDiv = $("#temp_chart")[0];
var humChartDiv = $("#hum_chart")[0];
var aqChartDiv = $("#aq_chart")[0];
var pmChartDiv = $("#pm_chart")[0];

// Create chart sizes
var chartHeight = $(".chart_column").height() / 2;
var chartWidth = $(".chart_column").width();


// History Data
var tempTrace = {
  x: [],
  y: [],
  name: "Temperature",
  mode: "lines+markers",
  type: "line",
};
var humTrace = {
  x: [],
  y: [],
  name: "Humidity",
  mode: "lines+markers",
  type: "line",
};
var aqTrace = {
  x: [],
  y: [],
  name: "Air Quality",
  mode: "lines+markers",
  type: "line",
};
var pm25Trace = {
  x: [],
  y: [],
  name: "PM 2.5",
  mode: "lines+markers",
  type: "line",
};


// Chart Layouts
var layout = {
  autosize: false,
  paper_bgcolor: "#1f222b",
  plot_bgcolor: "#2c2c38",
  font: {size: 10, color: "#9b81bc"},
  colorway: ["#A2c799", "#99a2c7", "#c799a2"],
  width: chartWidth,
  height: chartHeight,
  margin: {t: 1, b: 30},
  modebar: {orientation: "v"},
  xaxis: {gridcolor: "#3a3849"},
  yaxis: {gridcolor: "#3a3849"},
  showlegend: false,
};

var pmlayout = Object.create(layout);
pmlayout.shapes = [{
	type: 'line',
	xref: 'paper',
	x0: 0,
	x1: 1,
	y0: 30,
	y1: 30,
	line: {
		width: 2,
		color: "#ccc300",
		dash: "dash"}
	},
	{
	type: 'line',
	xref: 'paper',
	x0: 0,
	x1: 1,
	y0: 55,
	y1: 55,
	line: {
		width: 2,
		color: "#cc0000",
		dash: "dash"}
}]

var aqlayout = Object.create(layout);
aqlayout.shapes = [{
	type: 'line',
	xref: 'paper',
	x0: 0,
	x1: 1,
	y0: 85,
	y1: 85,
	line: {
		width: 2,
		color: "#ccc300",
		dash: "dash"}
	},
	{
	type: 'line',
	xref: 'paper',
	x0: 0,
	x1: 1,
	y0: 75,
	y1: 75,
	line: {
		width: 2,
		color: "#cc0000",
		dash: "dash"}
}]

// creates new charts
Plotly.newPlot(tempChartDiv, [tempTrace], layout);
Plotly.newPlot(humChartDiv, [humTrace], layout);
Plotly.newPlot(aqChartDiv, [aqTrace], aqlayout);
Plotly.newPlot(pmChartDiv, [pm25Trace], pmlayout);


async function update_data(){

    let response = await fetch("/data");
    let jsonData = await response.json();
     
    console.log(jsonData.mem_used);
	
	$("#mem_meter_label").text("Memory used: " + jsonData.mem_used + " (free = " + jsonData.mem_free + ")");
	$("#mem_meter").val(jsonData.mem_usedp.at(-1));

	$("#temp").text(jsonData.tempf.at(-1) + "  F");
	$("#hum").text(jsonData.hum.at(-1) +  "  %");
	$("#aq").text(jsonData.aq.at(-1));
	$("#pm25").text(jsonData.pm25_env.at(-1));
	$("#pm100").text(jsonData.pm100_env.at(-1));

	Plotly.update(tempChartDiv, {x:[jsonData.time], y:[jsonData.tempf]});
	Plotly.update(humChartDiv, {x:[jsonData.time], y:[jsonData.hum]});
	Plotly.update(aqChartDiv, {x:[jsonData.time], y:[jsonData.aq]});
	Plotly.update(pmChartDiv, {x:[jsonData.time], y:[jsonData.pm25_env]});

	warning_coloring();
	console.log("updated data")
}

update_data()

// Continuos loop that runs evry 15 seconds to update our web page with the latest sensor readings
setInterval(update_data, 15000);


})