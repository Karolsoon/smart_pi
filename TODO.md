1. Main
  1. LCD mode select (printer -> controller <- mode?)
    1. Get current lines of LCD
    2. 
  2. DB handler
    1. Insert sensor data
      1. Handle datetime within DB handler *OK*
      2. Add insert_dt columns (handled by DB) 
      2. Add read last measurements for each room/sensor type (window function?) *OK*
      3. Add validation after inserting *OK*
        1. insert_ts = ts_id ? (+/- 2sec?) *OK*
        2. Add log if not (check just last item)
      4. Handle timestamps in 3NF style (pointless, 8bytes)
      5. Partition table by year-month of ts_id
    2. Queue entries in case of connection issues
  3. Thread watch (restart service-threads LCD and API)


"User story"
1. Powerup
2. Get current sensors reading
  1. Get reading from DB
  2. If reading not available replace with default placeholder
3. Start API
4. Start sensor reading cycle

I turn on the RPi. I see the current temperature, pressure and lux and a 
weather forecast for the next 4 hours.