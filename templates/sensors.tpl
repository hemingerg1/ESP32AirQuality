{% set page = 'sensors' %}
{% include "header.tpl" page %}

<div class="content">

   <div class="flex_current">

     <div class="flex_box">
       <div class="box-topic">PMS5003</div>
       <div class="box_table">
          <table>
            <tr>
              <th colspan=2>PM Standardized<br>( &microg / m<sup>3</sup> )</th>
            </tr>
            <tr>
              <td>PM 1</td>
              <td class="pm1" id="pm1_std"></td>
            </tr>
            <tr>
              <td>PM 2.5</td>
              <td class="pm25" id="pm25_std"></td>
            </tr>
            <tr>
              <td>PM 10</td>
              <td class="pm100" id="pm100_std"></td>
            </tr>
          </table>
       </div>

       <div class="box_table">
          <table>
            <tr>
              <th colspan=2>PM Environmental<br>( &microg / m<sup>3</sup> )</th>
            </tr>
            <tr>
              <td>PM 1</td>
              <td class="pm1" id="pm1_env"></td>
            </tr>
            <tr>
              <td>PM 2.5</td>
              <td class="pm25" id="pm25_env"></td>
            </tr>
            <tr>
              <td>PM 10</td>
              <td class="pm100" id="pm100_env"></td>
            </tr>
          </table>
       </div>
    
       <div class="box_table">
          <table>
            <tr>
              <th colspan=2>Particle Counts<br>( number / 0.1L )</th>
            </tr>
            <tr>
              <td>Particles > 0.3&microm</td>
              <td id="pm3"></td>
            </tr>
            <tr>
              <td>Particles > 0.5&microm</td>
              <td id="pm5"></td>
            </tr>
            <tr>
              <td>Particles > 1.0&microm</td>
              <td id="pm10"></td>
            </tr>
            <tr>
              <td>Particles > 2.5&microm</td>
              <td id="pm25"></td>
            </tr>
            <tr>
              <td>Particles > 5.0&microm</td>
              <td id="pm50"></td>
            </tr>
            <tr>
              <td>Particles > 10&microm</td>
              <td id="pm100"></td>
            </tr>
          </table>
       </div>
     </div>

     <div class="flex_box">
       <div class="box-topic">BME680</div>
       <div class="box_table">
          <table>
            <tr>
              <th colspan=2>Sensor Readings</th>
            </tr>
            <tr>
              <td>Temperature</td>
              <td id="tempc"></td>
            </tr>
            <tr>
              <td>Humidity</td>
              <td id="hum"></td>
            </tr>
            <tr>
              <td>Pressure</td>
              <td id="press"></td>
            </tr>
            <tr>
              <td>Gas Resistance</td>
              <td id="gas_res"></td>
            </tr>
          </table>
       </div>
     </div>  
     
     <div class="flex_box">
       <div class="box-topic">Calculated</div>
       <div class="box_table">
          <table>
            <tr>
              <th colspan=2>Calculated Data</th>
            </tr>
            <tr>
              <td>Temperature</td>
              <td id="tempf"></td>
            </tr>
            <tr>
              <td>Air Quality</td>
              <td id="aq"></td>
            </tr>
          </table>
       </div>
     </div>

   </div>

</div>


</body>
</html>