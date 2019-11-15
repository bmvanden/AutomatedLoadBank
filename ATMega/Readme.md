### ATMega Main Functions
* Respond to requests from Pi to update data over I2C.
* Control current flow through main power resistors based on targetCurrent sent from Pi.
* Control fan speed based on data from Pi.
* Shut down load and put fans at maximum speed if safety input from Pi goes low or I2C
communication with Pi is lost. (Uses Watchdog timer that is refreshed when I2C data
updates)
* Safety pin should always be high to apply load on fuel cell.
