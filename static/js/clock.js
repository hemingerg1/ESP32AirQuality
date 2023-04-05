$(function(){

async function update_data(){
    var response = await fetch("/data");
	var jsonData = await response.json();

	var t_response = await fetch("/rtc");
	var t_jsonData = await t_response.json();
	
	$("#mem_meter_label").text("Memory used: " + jsonData.mem_used + " (free = " + jsonData.mem_free + ")");
	$("#mem_meter").val(jsonData.mem_usedp.at(-1));

	var localtime = `${t_jsonData.month}/${t_jsonData.day}/${t_jsonData.year}   ${t_jsonData.hour}:${t_jsonData.min}:${t_jsonData.sec}`;
	$("#localtime").text(`Machine's RTC is currently set at:  ${'\xa0'.repeat(5)}   ${localtime}`);
	
	console.log("updated data");
}

update_data();

// Continuos loop that runs evry 15 seconds to update our web page with the latest sensor readings
setInterval(update_data, 5000);

})