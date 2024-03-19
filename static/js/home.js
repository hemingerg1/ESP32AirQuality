$(function () {

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
		paper_bgcolor: "#2f3e46",
		plot_bgcolor: "#59656b",
		font: { size: 10, color: "#f4f6f3" },
		colorway: ["#A2c799", "#99a2c7", "#c799a2"],
		width: chartWidth,
		height: chartHeight,
		margin: { t: 20, b: 60, r: 10, l: 20 },
		modebar: { orientation: "v" },
		xaxis: { gridcolor: "#354f52" },
		showlegend: false,
	};

	var templayout = Object.create(layout);
	templayout.yaxis = { range: [40, 90], type: 'linear', gridcolor: "#354f52" }
	templayout.title = { text: 'Temperature' }

	var humlayout = Object.create(layout);
	humlayout.yaxis = { range: [30, 70], type: 'linear', gridcolor: "#354f52" }
	humlayout.title = { text: 'Humidity' }

	var pmlayout = Object.create(layout);
	pmlayout.yaxis = { range: [0, 60], type: 'linear', gridcolor: "#354f52" }
	pmlayout.title = { text: 'PM' }
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
			dash: "dash"
		}
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
			dash: "dash"
		}
	}]

	var aqlayout = Object.create(layout);
	aqlayout.yaxis = { range: [50, 100], type: 'linear', gridcolor: "#354f52" }
	aqlayout.title = { text: 'Air Quality' }
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
			dash: "dash"
		}
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
			dash: "dash"
		}
	}]

	// creates new charts
	Plotly.newPlot(tempChartDiv, [tempTrace], templayout);
	Plotly.newPlot(humChartDiv, [humTrace], humlayout);
	Plotly.newPlot(aqChartDiv, [aqTrace], aqlayout);
	Plotly.newPlot(pmChartDiv, [pm25Trace], pmlayout);


	async function update_data() {

		let response = await fetch("/data");
		let jsonData = await response.json();

		console.log(jsonData.mem_used);

		// update memory meter
		$("#mem_meter_label").text("Memory used: " + jsonData.mem_used + " (free = " + jsonData.mem_free + ")");
		$("#mem_meter").val(jsonData.mem_usedp.at(-1));

		// update boxes at top of page
		$("#oTemp").text(jsonData.oTempF + "  F");
		$("#temp").text(jsonData.tempf.at(-1) + "  F");
		$("#hum").text(jsonData.hum.at(-1) + "  %");
		$("#aq").text(jsonData.aq.at(-1));
		$("#pm25").text(jsonData.pm25_env.at(-1));
		$("#pm100").text(jsonData.pm100_env.at(-1));

		// Find min and max values
		var minTemp = Math.floor(Math.min(...jsonData.tempf)) - 2;
		var maxTemp = Math.ceil(Math.max(...jsonData.tempf)) + 2;
		var minHum = Math.floor(Math.min(...jsonData.hum)) - 2;
		var maxHum = Math.ceil(Math.max(...jsonData.hum)) + 2;
		var minAQ = Math.min(Math.floor(Math.min(...jsonData.aq)) - 2, 70);
		var maxAQ = 100;
		var minPM25 = 0;
		var maxPM25 = Math.max(Math.ceil(Math.max(...jsonData.pm25_env)) + 2, 60);

		// Update chart ranges
		var tempUpdate = { 'yaxis.range': [minTemp, maxTemp] };
		var humUpdate = { 'yaxis.range': [minHum, maxHum] };
		var aqUpdate = { 'yaxis.range': [minAQ, maxAQ] };
		var pmUpdate = { 'yaxis.range': [minPM25, maxPM25] };

		// Update plots
		Plotly.update(tempChartDiv, { x: [jsonData.time], y: [jsonData.tempf] }, tempUpdate);
		Plotly.update(humChartDiv, { x: [jsonData.time], y: [jsonData.hum] }, humUpdate);
		Plotly.update(aqChartDiv, { x: [jsonData.time], y: [jsonData.aq] }, aqUpdate);
		Plotly.update(pmChartDiv, { x: [jsonData.time], y: [jsonData.pm25_env] }, pmUpdate);

		warning_coloring();
		console.log("updated data")
	}

	update_data()

	// Continuos loop that runs evry 15 seconds to update our web page with the latest sensor readings
	setInterval(update_data, 15000);


})