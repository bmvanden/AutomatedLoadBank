"""
Filename: view.py
Project:  EcoCar - Automated Resistive Load Bank
Version:  0.1
Created:  May 20, 2019    Modified:  May 20, 2019
Authors:  Ben Vandenberg      bmvanden@ualberta.ca
          Nikolai Marianicz   marianic@ualberta.ca
Purpose:  GUI view
Notes: 
"""

import tkinter as tk 

class View:
	def __init__(self, root, model):
		self.frame = tk.Frame(root)
		self.model = model