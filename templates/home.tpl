{% set page = 'home' %}
{% include "header.tpl" page %}

<div class="content">

  <div class="flex_current">
     <div class="flex_box">
       <div class="box-topic">Temperature</div>
       <div class="number" id="temp"></div>
     </div>
     <div class="flex_box">
       <div class="box-topic">Humidity</div>
       <div class="number" id="hum"></div>
     </div>    
     <div class="flex_box">
       <div class="box-topic">Air Quality</div>
       <div class="number aq" id="aq"></div>
     </div>
     <div class="flex_box">
       <div class="box-topic">PM 2.5</div>
       <div class="number pm25" id="pm25"></div>
     </div>
     <div class="flex_box">
       <div class="box-topic">PM 10</div>
       <div class="number pm100" id="pm100"></div>
     </div>
   </div>

   <div class='flex_charts'>
      <div class="chart_column">
        <div id="temp_chart" class="chart">Temperature</div>
        <div id="aq_chart" class="chart">Air Quality</div>
      </div>
      <div class="chart_column">
        <div id="hum_chart" class="chart">Humidity</div>
        <div id="pm_chart" class="chart">PM</div>
      </div>
   </div>

</body>
</html>