### Pi Code Overview
* main.py starts multithreading, so graphical user interface (GUI) and ATMega communication can run independently. 
* I2CThread.py refreshes data to and from ATMega periodically (currently set to 1 second intervals).
* configuration.py is a user editable file to store fuel cell parameters (max/min current, vehicle name, etc.)
* model.py loads data from configuration.py when it is initialized. It then stores all the current and target 
operating parameters for the fuel cell. model.py refreshes its data from I2CThread.py.
* GUIThread.py initializes an instance of model.py when it is started. It then displays values from model.py 
on the user interface. It also has event handlers to watch for user input and save them to model.py.

### Main Functions Performed by Pi
* Monitor temperature of enclosure (electronics area and main power resistors). Adjust fan speed as necessary
to control temperature. Shut down system using digital safety output if it gets too hot.
* Communicate operating status and parameters to user via TkInter GUI. 
* Receive user input through event handlers on GUI.
* Send target current draw to ATMega based on user input.
