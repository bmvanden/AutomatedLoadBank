#########################################################################################
# Filename: GUI_Test.py
# Title:    EcoCar - Automated Resistive Load Bank GUI
# Version:  0.0
# Date:     September 27, 2018
# Author:   Ben Vandenberg      bmvanden@ualberta.ca
# Purpose:  Test GUI implementation in Python
# Notes:    In addition to base Python installation, Pillow package is required to run
#           this software. (PIL is for Python Image Library, but its functionality has
#           been superceded by Pillow)
#########################################################################################

import tkinter as tk
import time
from PIL import ImageTk, Image
#from scrolledtext import scrolledtext



# Function to draw disclaimer
def view_disclaimer():
    disclaimer_frame = tk.Frame(root, height=380, width=600)
    disclaimer_frame.pack_propagate(False)
    disclaimer_frame.place(x=80, y=50)

    disclaimer_label = tk.Label(disclaimer_frame, text='WARNING')
    disclaimer_label.config(font=("Arial", 24), bg='red')
    disclaimer_label.pack(fill="both")

    #disclaimer_scrollbar = tk.Scrollbar(disclaimer_frame)
    #disclaimer_scrollbar.pack(anchor='e', fill='y')

    disclaimer_button = tk.Button(disclaimer_frame, text="I Accept", command=vehicle_select)
    disclaimer_button.config(font=("Arial", 16), bg='black', fg='white')
    disclaimer_button.pack(side="bottom", fill="x")

    disclaimer_textbox = tk.Text(disclaimer_frame, width=50, height=20)
    disclaimer_textbox.config(font=("Arial", 12))
    disclaimer_textbox.pack(fill="both")
    disclaimer_textbox.insert(tk.END, "-Warning text 1\n\n-Warning text 2\n\n-Warning text 3\n\n")
    


    #scrollbar.config(command=disclaimer_textbox.yview)

    # create a Text widget with a Scrollbar attached
    #disclaimer_textbox = scrolledtext(disclaimer_frame, undo=True)
    #disclaimer_textbox['font'] = ('consolas', '12')
    #disclaimer_textbox.pack(expand=True, fill='both')

def vehicle_select():
    vehicle_select_frame = tk.Frame(root, height=480, width=800)
    vehicle_select_frame.pack_propagate(False)
    vehicle_select_frame.place(x=0, y=0)

    vehicle_select_title = tk.Label(vehicle_select_frame, text="Select a Vehicle")
    vehicle_select_title.config(font=("Arial", 24), pady=50)
    vehicle_select_title.pack()

    #panel1 = tk.Label(vehicle_select_frame, image = img)
    #panel1.pack(side = "bottom", fill = "both", expand = "yes")

    alice_button = tk.Button(vehicle_select_frame, image = alice2img, text="Alice", compound='c', command=process_select)
    alice_button.config(width=200, height=200)
    alice_button.place(x=50, y=140)
    alice_button.config(font=("Arial", 48), bg='black', fg='white')

    sofie_button = tk.Button(vehicle_select_frame, text="Sofie", image = sofieimg, compound='c')
    sofie_button.config(width=200, height=200)
    sofie_button.place(x=300, y=140)
    sofie_button.config(font=("Arial", 48), bg='black', fg='white')

    other_button = tk.Button(vehicle_select_frame, image = fuelcellimg, text="Other", compound='c')
    other_button.config(width=200, height=200)
    other_button.place(x=550, y=140)
    other_button.config(font=("Arial", 48), bg='black', fg='white')

def process_select():
    baseFrame = tk.Frame(root, height=480, width=800)
    baseFrame.pack_propagate(False)
    baseFrame.place(x=0, y=0)

    title = tk.Label(baseFrame, text="Select Processes to Run")
    title.config(font=("Arial", 24), pady=50)
    title.pack()

    selectConditioning = tk.Checkbutton(baseFrame, text="Fuel cell conditioning")
    selectConditioning.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectConditioning.pack()

    selectPreStarvePolCurve = tk.Checkbutton(baseFrame, text="Polarization curve before air starve")
    selectPreStarvePolCurve.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectPreStarvePolCurve.pack()

    selectAirStarve = tk.Checkbutton(baseFrame, text="Air starve")
    selectAirStarve.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectAirStarve.pack()

    selectPostStarvePolCurve = tk.Checkbutton(baseFrame, text="Polarization curve after air starve")
    selectPostStarvePolCurve.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectPostStarvePolCurve.pack()

    continue_button = tk.Button(root, text="Continue")
    continue_button.config(font=("Arial", 16), bg='black', fg='white')
    continue_button.place(width=200, x=300, y=375)

# Create the main window
root = tk.Tk()
root.title("EcoCar GUI")

# Couldn't seem to find images unless they were declared globally
alice2img = ImageTk.PhotoImage(Image.open("Alice2.jpg"))
sofieimg = ImageTk.PhotoImage(Image.open("Sofie.jpg"))
fuelcellimg = ImageTk.PhotoImage(Image.open("FuelCell.png"))

# Import image for background
img = ImageTk.PhotoImage(Image.open("Alice.PNG"))
panel = tk.Label(root, image = img)
panel.pack(side = "bottom", fill = "both", expand = "yes")

# Create label
title = tk.Label(root, text="EcoCar")
title.config(font=("Arial", 44))
title.place(width=300, x=10, y=10)

subtitle1 = tk.Label(root, text="Resistive Load Bank")
subtitle1.config(font=("Arial", 16))
subtitle1.place(width=300, x=10, y=70)

subtitle1 = tk.Label(root, text="Version 0.0")
subtitle1.config(font=("Arial", 16))
subtitle1.place(width=300, x=10, y=95)

continue_button = tk.Button(root, text="Continue", command=view_disclaimer)
continue_button.config(font=("Arial", 16), bg='black', fg='white')
continue_button.place(width=200, x=300, y=375)



# Set window size to match 7" SparkFun LCD (800 x 480)
root.resizable(False, False)
root.geometry("800x480")

# Run forever!
root.mainloop()

