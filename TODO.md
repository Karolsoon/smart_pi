1. Test coverage for app.py?
2. Repair testing - add mock imports to revive testing capabilities
3. Adapt test for HomeMode4x20 template and lines - 'outdoor' added on line 4
4. Add ThreadWatch class to check if all threads are running and revive dead threads
5. Add logging capabilities - currently only cronlog available which resets on each app restart
6. Add sensor readings validation (i.e. pressure 680hPa, temperature 35C+)

Technical debt!!!!
1. Remove hotfix in lcdprinter.py Line 105 (set_formatting is not clean at all)
2. app.py Line 89 (handle exception when pressure_trend is None)
3. app.py Line 44-60 (handle exceptions, extract methods)
4. LOGGING FUNCTIONALLITY!
5. Make pressure trend query less frequent (1 per hour)
6. dbquery.py Line 99 (again, handle None in case of pressure trend) 