#########################################################################################
# Filename: GUI_Test.py
# Title:    EcoCar - Automated Resistive Load Bank GUI
# Version:  0.1
# Date:     September 27, 2018
# Authors:   Ben Vandenberg      bmvanden@ualberta.ca
#	     Nikolai Marianicz   marianic@ualberta.ca
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
import configparser
import math
import RPi.GPIO as GPIO
from smbus2 import SMBusWrapper
import I2Ctest.py

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT, initial = 1)
GPIO.setup(9, GPIO.OUT)
GPIO.output(9, 0)

#How to get data from a config file:
# Option 1: name config file as .py extension, import values (easiest way, editable with IDLE
# Option 2: import ConfigParser

#variable used for example down below
#testvalueimportant = 5
parser = configparser.ConfigParser()
parser.read('CarConfig.ini')

class EcoCar:
    name = None
    method = None
    CCurrent = None
    SCurrent = None
    ECurrent = None
    CurrentStep = None
    CCurrentStep = None
    SCurrentStep = None
    ECurrentStep = None
    CurrentStepStep = None

class OperatingSpecs:
    BatVolt = None
    CellVolt = None
    CellCurr = None
    TempLower = None
    TempUpper = None
    TempCell = None
    
InsOS = OperatingSpecs()

YourEcoCar = EcoCar()
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
    
    YourEcoCar.name = "Alice"
    process_select()
    
def sofie_select():

    YourEcoCar.name = "Sofie"
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
    
    baseFrame = tk.Frame(root, height=480, width=800)
    baseFrame.pack_propagate(False)
    baseFrame.place(x=0, y=0)

    title = tk.Label(baseFrame, text="Select Processes to Run on %s" % (YourEcoCar.name))
    title.config(font=("Arial", 24), pady=50)
    title.pack()

    selectConditioning = tk.Button(root, text="Run Conditioning Cycle", command=Conditioning_Cycle)
    selectConditioning.config(font=("Arial", 16), bg='black', fg='white')
    selectConditioning.place(width=300, height=50, x=150, y=100)

    selectStarve = tk.Button(root, text="Run Air Starve", command=Starve_Cycle)
    selectStarve.config(font=("Arial", 16), bg='black', fg='white')
    selectStarve.place(width=300, height=50, x=150, y=200)

    selectPolCurve = tk.Button(root, text="Run Pol Curve", command=Curve_Cycle)
    selectPolCurve.config(font=("Arial", 16), bg='black', fg='white')
    selectPolCurve.place(width=300, height=50, x=150, y=300)

def Conditioning_Cycle():
    
    YourEcoCar.CCurrent = parser['%s' % YourEcoCar.name].getfloat('CCurrent')
    YourEcoCar.method = "Conditioning"
    YourEcoCar.CCurrentStep = int(math.floor(YourEcoCar.CCurrent*2))
    YourEcoCar.CCurrent = YourEcoCar.CCurrentStep/2
    run_screen()

def Starve_Cycle():
    YourEcoCar.method = "Air Starve"
    run_screen()

def Curve_Cycle():
    YourEcoCar.SCurrent = parser['%s' % YourEcoCar.name].getfloat('SCurrent')
    YourEcoCar.ECurrent = parser['%s' % YourEcoCar.name].getfloat('ECurrent')
    YourEcoCar.CurrentStep = parser['%s' % YourEcoCar.name].getfloat('CurrentStep')
    YourEcoCar.method = "Pol Curve"

    YourEcoCar.SCurrentStep = int(math.floor(YourEcoCar.SCurrent*2))
    YourEcoCar.ECurrentStep = int(math.floor(YourEcoCar.ECurrent*2))
    YourEcoCar.CurrentStepStep = int(math.floor(YourEcoCar.CurrentStep*2))

    YourEcoCar.SCurrent = YourEcoCar.SCurrentStep/2
    YourEcoCar.ECurrent = YourEcoCar.ECurrentStep/2
    YourEcoCar.CurrentStep = YourEcoCar.CurrentStepStep/2
    
    
    run_screen()
    
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

    if((YourEcoCar.SCurrentStep > YourEcoCar.ECurrentStep) || (YourEcoCar.CurrentStepStep > YourEcoCar.ECurrentStep)):
        #Consistency Checks
        RS_title = tk.Label(RS_baseFrame, text="Error in Current Step Definitions!")
        RS_title.config(font=("Arial", 24), pady=150)
        RS_title.pack()
        
        RS_Error_button = tk.Button(RS_baseFrame, text="Start", command=vehicle_select)
        RS_Error_button.config(font=("Arial", 16), bg='black', fg='white')
        RS_Error_button.place(width=200, height=200, x=150, y=200)

    if((YourEcoCar.SCurrentStep > 120) || (YourEcoCar.ECurrentStep > 120) || (YourEcoCar.CCurrentStep > 60) || (YourEcoCar.CurrentCurrentStep > 120)):
        #This checks to ensure safe maximum opperating conditions (limits conditioning current to 30A, pol curve to 60A)
        RS_title = tk.Label(RS_baseFrame, text="Unsafe Current Parameters detected, consult operating specifications for limits")
        RS_title.config(font=("Arial", 24), pady=150)
        RS_title.pack()
        
        RS_Error_button = tk.Button(RS_baseFrame, text="Start", command=vehicle_select)
        RS_Error_button.config(font=("Arial", 16), bg='black', fg='white')
        RS_Error_button.place(width=200, height=200, x=150, y=200)
    else:
        RS_title = tk.Label(RS_baseFrame, text="Ready!")
        RS_title.config(font=("Arial", 24), pady=50)
        RS_title.pack()

        RS_start_button = tk.Button(RS_baseFrame, text="Start", command=activation_sequence)
        RS_start_button.config(font=("Arial", 16), bg='black', fg='white')
        RS_start_button.place(width=200, height=200, x=150, y=200)
            
        RS_stop_button = tk.Button(RS_baseFrame, text="Stop", command=end_run)
        RS_stop_button.config(font=("Arial", 16), bg='black', fg='white')
        RS_stop_button.place(width=200, height=200, x=450, y=200)

        RS_emerstop_button = tk.Button(RS_baseFrame, text="Emergency Stop", command=emergencystop_run)
        RS_emerstop_button.config(font=("Arial", 16), bg='black', fg='white')
        RS_emerstop_button.place(width=50, height=50, x=650, y=300)

def activation_sequence():
    
    if(YourEcoCar.method == "Conditioning"):
        conditioning_cycle()
    elif(YourEcoCar.method == "Pol Curve"):
        polarization_curve()
    elif(YourEcoCar.method == "Air Starve"):
        air_starve()

##def recap_run():
##
##    recap_sentence = "Running %s on vehicle %s" % (YourEcoCar.method, YourEcoCar.name)
##    if YourEcoCar.method == "Conditioning" :
##        second_sentence = "To be run at constant current %.1fA, step value %d" % (YourEcoCar.CCurrent, YourEcoCar.CCurrentStep)
##    elif YourEcoCar.method == "Pol Curve" :
##        second_sentence = "To be run from %.1fA to %.1fA\n in increments of %.1fA, step values %d, %d, %d" % (YourEcoCar.SCurrent, YourEcoCar.ECurrent, YourEcoCar.CurrentStep, YourEcoCar.SCurrentStep, YourEcoCar.ECurrentStep, YourEcoCar.CurrentStepStep)
##    elif YourEcoCar.method == "Air Starve" :
##        second_sentence = ""
##
##    recap_frame = tk.Frame(root, height=380, width=600)
##    recap_frame.pack_propagate(False)
##    recap_frame.place(x=80, y=50)
##
##    recap_label = tk.Label(recap_frame, text='Recap of what happened')
##    recap_label.config(font=("Arial", 24), bg='blue')
##    recap_label.pack(fill="both")
##
##    recap_button = tk.Button(recap_frame, text="Okee Dokey", command=run_screen)
##    recap_button.config(font=("Arial", 16), bg='black', fg='white')
##    recap_button.pack(side="bottom", fill="x")
##
##    recap_textbox = tk.Text(recap_frame, width=50, height=20)
##    recap_textbox.config(font=("Arial", 12))
##    recap_textbox.pack(fill="both")
##    recap_textbox.insert(tk.END, "%s\n%s" % (recap_sentence, second_sentence))

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

subtitle1 = tk.Label(root, text="Version 0.2")
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


