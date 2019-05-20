"""
Filename: main.py
Project:  EcoCar - Automated Resistive Load Bank
Version:  0.1
Created:  May 20, 2019    Modified:  May 20, 2019
Authors:  Ben Vandenberg      bmvanden@ualberta.ca
          Nikolai Marianicz   marianic@ualberta.ca
Purpose:  Overall control of project. This file should be called on
		  Raspbian operating system with dependencies listed in 
		  README.md to start user interface.
Notes:   -In addition to base Python installation, Pillow package is required to run
          this software. (PIL is for Python Image Library, but its functionality has
          been superceded by Pillow)
"""

from controller import Controller

#Construct and run controller
if __name__ == '__main__':
	c = Controller()
	c.run()