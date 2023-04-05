$(function(){

// Page locations for charts
var tempChartDiv = document.getElementById("temp_chart");
var humChartDiv = document.getElementById("hum_chart");
var aqChartDiv = document.getElementById("aq_chart");
var pmChartDiv = document.getElementById("pm_chart");

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
var pm100Trace = {
  x: [],
  y: [],
  name: "PM 10",
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
};


// creates new charts
Plotly.newPlot(tempChartDiv, [tempTrace], layout);
Plotly.newPlot(humChartDiv, [humTrace], layout);
Plotly.newPlot(aqChartDiv, [aqTrace], layout);
Plotly.newPlot(pmChartDiv, [pm25Trace, pm100Trace], layout);




})