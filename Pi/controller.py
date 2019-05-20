"""
Filename: controller.py
Project:  EcoCar - Automated Resistive Load Bank
Version:  0.1
Created:  May 20, 2019    Modified:  May 20, 2019
Authors:  Ben Vandenberg      bmvanden@ualberta.ca
          Nikolai Marianicz   marianic@ualberta.ca
Purpose:  GUI controller
Notes:
"""

import tkinter as tk

from model import Model 
from view import View 


class Controller:
	def __init__(self):
		self.root = tk.Tk()
		self.model = Model()
		self.view = View(self.root, self.model)

	def run(self):
		self.root.title("Automated Load Bank")
		self.root.deiconify()
		self.root.mainloop()
		