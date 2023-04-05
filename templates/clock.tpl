{% set page = 'clock' %}
{% include "header.tpl" page %}


<div class="content">
  <div class="current_time">
     <h3 id="localtime"></h3>
   </div>
   <div class="time_input">
     <h3>Input Current Time:</h3>
     <form method="post">
        <label for="year">Year:</label><br>
        <input type="text" id="year" name="year" value="2023"><br><br>
        <label for="month">Month:</label><br>
        <input type="text" id="month" name="month" value="1"><br><br>
        <label for="day">Day:</label><br>
        <input type="text" id="day" name="day" value="1"><br><br><br>
        <label for="hour">Hour (24h format):</label><br>
        <input type="text" id="hour" name="hour" value="1"><br><br>
        <label for="min">Minute:</label><br>
        <input type="text" id="min" name="min" value="1"><br><br>

        <input type="submit" value="Submit">
     </form>
  </div>

</div>

</body>
</html>