<!DOCTYPE html>

<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">    
    <title>Garage Monitor</title>
    <link rel="icon" type="image/x-icon" href="static/images/favicon.png">
    <link rel="stylesheet" href="static/css/index.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.3/jquery.min.js"></script>
    {% if page == 'home' %}
    <script src="https://cdn.plot.ly/plotly-2.16.1.min.js"></script>
    <script src="static/js/warning_coloring.js"></script>
    <script src="static/js/home.js"></script>
    {% elif page == 'sensors' %}
    <script src="static/js/warning_coloring.js"></script>
    <script src="static/js/sensors.js"></script>
    {% elif page == 'clock' %}
    <script src="static/js/clock.js"></script>
    {% endif %}
</head>

<body>
<div class="sidebar">
  <a href="/">Home</a>
  <a href="/sensors">All Sensors</a>
  <a href="/dash">Network Dashboard</a>
  <a href="/cam">Cameras</a>
  <a href="/clock">Clock</a>

  <div id="side_mem">
    <label id="mem_meter_label" for="mem_meter"></label><br>
    <meter id="mem_meter" min=0 max=1 high=0.75></meter>
  </div>
</div>