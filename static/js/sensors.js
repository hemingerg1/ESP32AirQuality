$(function () {

	async function update_data() {
		var response = await fetch("/data");
		var jsonData = await response.json();

		$("#mem_meter_label").text("Memory used: " + jsonData.mem_used + " (free = " + jsonData.mem_free + ")");
		$("#mem_meter").val(jsonData.mem_usedp.at(-1));

		$("#pm1_std").text(jsonData.pm10_std);
		$("#pm25_std").text(jsonData.pm25_std);
		$("#pm100_std").text(jsonData.pm100_std);

		$("#pm1_env").text(jsonData.pm10_env.at(-1));
		$("#pm25_env").text(jsonData.pm25_env.at(-1));
		$("#pm100_env").text(jsonData.pm100_env.at(-1));

		$("#pm3").text(jsonData.pm3);
		$("#pm5").text(jsonData.pm5);
		$("#pm10").text(jsonData.pm10);
		$("#pm25").text(jsonData.pm25);
		$("#pm50").text(jsonData.pm50);
		$("#pm100").text(jsonData.pm100);

		$("#tempc").text(jsonData.tempc + " C");
		$("#hum").text(jsonData.hum.at(-1) + " %");
		$("#press").text(jsonData.pres + " MPa");
		$("#gas_res").text(jsonData.gas_res + " \u2126");

		$("#tempf").text(jsonData.tempf.at(-1) + " F");
		$("#aq").text(jsonData.aq.at(-1) + " %");

		$("#LGdoor").text(jsonData.Ldoorsat);
		$("#SGdoor").text(jsonData.Sdoorsat);
		$("#OWdoor").text(jsonData.HOdoorsat);
		$("#ISdoor").text(jsonData.HIdoorsat);

		$("#oTempF").text(jsonData.oTempF + " F");

		warning_coloring();
		console.log("updated data");
	}

	update_data()

	// Continuos loop that runs evry 15 seconds to update the web page with the latest sensor readings
	setInterval(update_data, 15000);

})