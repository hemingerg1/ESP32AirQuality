// JQuary for formating unhealthy table values
function warning_coloring(){

var alert_color = "#cc0000",
    warning_color = "#ccc300";


$(".aq").each(function() {
        var warning = 85,
            alert = 75,
            reading = $(this).text().replace(' %', '');

        if (reading <= alert) {
            $(this).css("color", alert_color);
        }
        else if (reading > alert && reading <= warning) {
            $(this).css("color", warning_color);
        }
});

$(".pm1").each(function() {
        var warning = 12,
            alert = 22,
            reading = $(this).text();

        if (reading >= alert) {
            $(this).css("color", alert_color);
        }
        else if (reading < alert && reading >= warning) {
            $(this).css("color", warning_color);
        }
});

$(".pm25").each(function() {
        var warning = 30,
            alert = 55,
            reading = $(this).text();

        if (reading >= alert) {
            $(this).css("color", alert_color);
        }
        else if (reading < alert && reading >= warning) {
            $(this).css("color", warning_color);
        }
});

$(".pm100").each(function() {
        var warning = 150,
            alert = 250,
            reading = $(this).text();

        if (reading >= alert) {
            $(this).css("color", alert_color);
        }
        else if (reading < alert && reading >= warning) {
            $(this).css("color", warning_color);
        }
});
}