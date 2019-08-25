#########################################################################################
# Filename: GUI_Test.py
# Title:    EcoCar - Automated Resistive Load Bank GUI
# Version:  0.1
# Date:     September 27, 2018
# Authors:   Ben Vandenberg      bmvanden@ualberta.ca
#			 Nikolai Marianicz   marianic@ualberta.ca
# Purpose:  Test GUI implementation in Python
#
# Notes:   -In addition to base Python installation, Pillow package is required to run
#           this software. (PIL is for Python Image Library, but its functionality has
#           been superceded by Pillow)
#		   -I used Ben's test function as a base for the full thing, as I liked his 
#           design a lot. -Nik
#########################################################################################

import tkinter as tk
import time
from PIL import ImageTk, Image
#from scrolledtext import scrolledtext

#variable used for example down below
#testvalueimportant = 5

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

    alice_button = tk.Button(vehicle_select_frame, image = alice2img, text="Alice", compound='c', command=alice_select)
    alice_button.config(width=200, height=200)
    alice_button.place(x=50, y=140)
    alice_button.config(font=("Arial", 48), bg='black', fg='white')

    sofie_button = tk.Button(vehicle_select_frame, text="Sofie", image = sofieimg, compound='c', command=sofie_select)
    sofie_button.config(width=200, height=200)
    sofie_button.place(x=300, y=140)
    sofie_button.config(font=("Arial", 48), bg='black', fg='white')

    other_button = tk.Button(vehicle_select_frame, image = fuelcellimg, text="Other", compound='c', command=picked_other)
    other_button.config(width=200, height=200)
    other_button.place(x=550, y=140)
    other_button.config(font=("Arial", 48), bg='black', fg='white')

def alice_select():
    global carchoice
    carchoice = 0
    process_select()

def sofie_select():
    global carchoice
    carchoice = 1
    process_select()

def picked_other():
    
    pickedotherFrame = tk.Frame(root, height=480, width=800)
    pickedotherFrame.pack_propagate(False)
    pickedotherFrame.place(x=0, y=0)

    pickedothertitle = tk.Label(pickedotherFrame, text="What are we doing with this button")
    pickedothertitle.config(font=("Arial", 24), pady=50)
    pickedothertitle.pack()

    pickedother_button = tk.Button(root, text="OH NO GO BACK", command=vehicle_select)
    pickedother_button.config(font=("Arial", 16), bg='black', fg='white')
    pickedother_button.place(width=400, height=100, x=200, y=300)

def process_select():

    global methodchoice
    
    baseFrame = tk.Frame(root, height=480, width=800)
    baseFrame.pack_propagate(False)
    baseFrame.place(x=0, y=0)

    title = tk.Label(baseFrame, text="Select Processes to Run")
    title.config(font=("Arial", 24), pady=50)
    title.pack()

    selectConditioning = tk.Radiobutton(baseFrame, text="Fuel cell conditioning", variable=methodchoice, value=0)
    selectConditioning.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectConditioning.pack()

    selectPreStarvePolCurve = tk.Radiobutton(baseFrame, text="Polarization curve before air starve", variable=methodchoice, value=1)
    selectPreStarvePolCurve.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectPreStarvePolCurve.pack()

    selectAirStarve = tk.Radiobutton(baseFrame, text="Air starve", variable=methodchoice, value=2)
    selectAirStarve.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectAirStarve.pack()

    selectPostStarvePolCurve = tk.Radiobutton(baseFrame, text="Polarization curve after air starve", variable=methodchoice, value=3)
    selectPostStarvePolCurve.config(font=("Arial", 16), anchor='w', width=300, padx=230)
    selectPostStarvePolCurve.pack()

    menu_continue_button = tk.Button(root, text="Continue", command=run_screen)
    menu_continue_button.config(font=("Arial", 16), bg='black', fg='white')
    menu_continue_button.place(width=100, height=100, x=300, y=300)
	
def run_screen():

    #this code is an example of how to do updating button text in tkinter
    #note for RS_stopbutton replace after text= with: "Stop %s" % (testvalueimportant), command=additem)
    #def additem():
       # global testvalueimportant
        #testvalueimportant += 1
        #RS_stop_button.config(text="Stop %s" % (testvalueimportant))

    RS_baseFrame = tk.Frame(root, height=480, width=800)
    RS_baseFrame.pack_propagate(False)
    RS_baseFrame.place(x=0, y=0)
    
    RS_title = tk.Label(RS_baseFrame, text="Running!")
    RS_title.config(font=("Arial", 24), pady=50)
    RS_title.pack()

    RS_start_button = tk.Button(RS_baseFrame, text="Start", command=recap_run)
    RS_start_button.config(font=("Arial", 16), bg='black', fg='white')
    RS_start_button.place(width=200, height=200, x=150, y=200)
	
    RS_stop_button = tk.Button(RS_baseFrame, text="Stop", command=end_run)
    RS_stop_button.config(font=("Arial", 16), bg='black', fg='white')
    RS_stop_button.place(width=200, height=200, x=450, y=200)

    RS_emerstop_button = tk.Button(RS_baseFrame, text="Emergency Stop", command=emergencystop_run)
    RS_emerstop_button.config(font=("Arial", 16), bg='black', fg='white')
    RS_emerstop_button.place(width=50, height=50, x=650, y=300)

def recap_run():

    cars = ["Alice", "Sofie"]
    methods = ["conditioning", "polarization before air starve", "air Starve", "polarization after air starve"]
    global carchoice
    global methodchoice

    recap_sentence = "Running %s on vehicle %s" % (methods[methodchoice.get()], cars[carchoice])
    
    recap_frame = tk.Frame(root, height=380, width=600)
    recap_frame.pack_propagate(False)
    recap_frame.place(x=80, y=50)

    recap_label = tk.Label(recap_frame, text='Recap of what happened')
    recap_label.config(font=("Arial", 24), bg='blue')
    recap_label.pack(fill="both")

    recap_button = tk.Button(recap_frame, text="Okee Dokey", command=run_screen)
    recap_button.config(font=("Arial", 16), bg='black', fg='white')
    recap_button.pack(side="bottom", fill="x")

    recap_textbox = tk.Text(recap_frame, width=50, height=20)
    recap_textbox.config(font=("Arial", 12))
    recap_textbox.pack(fill="both")
    recap_textbox.insert(tk.END, "%s" % (recap_sentence))

def end_run():
    end_frame = tk.Frame(root, height=380, width=600)
    end_frame.pack_propagate(False)
    end_frame.place(x=80, y=50)

    end_label = tk.Label(end_frame, text='Ending Process')
    end_label.config(font=("Arial", 24), bg='blue')
    end_label.pack(fill="both")

    end_button = tk.Button(end_frame, text="Okee Dokey", command=vehicle_select)
    end_button.config(font=("Arial", 16), bg='black', fg='white')
    end_button.pack(side="bottom", fill="x")

    end_textbox = tk.Text(end_frame, width=50, height=20)
    end_textbox.config(font=("Arial", 12))
    end_textbox.pack(fill="both")
    end_textbox.insert(tk.END, "Oh man hope this works")

def emergencystop_run():
    #code to stop everything
    root.destroy()





# Create the main window
root = tk.Tk()
root.title("EcoCar GUI")

# define variables
carchoice = tk.IntVar()
methodchoice = tk.IntVar()

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

subtitle1 = tk.Label(root, text="Version 0.1")
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


