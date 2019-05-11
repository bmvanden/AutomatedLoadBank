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



######################################################################################################
#                      A PREFACE TO ANY ECOCAR MEMBERS READING THIS
#
#     This document is in truth a recording of my slow decent into madness during the
#   capstone project, if you've been tasked with editing this code, although its fairly
#   straightforward, I imagine that to anyone else its probably unmaintainable. That being
#   said, ONLY edit this code if you know EXACTLY what you're doing, or if you are doing stuff,
#   test it with out a fuel cell, for sure. You shouldn't be able to break the code without manually
#   telling the device to break stuff, so thats a plus.
#
#     P.S. I'm so sorry for this
#
#     Also, if the issue is to do with outputs, you should look in the ATMega code prior to tinkering
#   with this one as I don't have direct access to any load bank outputs, I only tell the ATMega what
#   currents to output
#
#   -Nik, programmer for the Pi Side of the device.
#
######################################################################################################




import tkinter as tk
import time
from PIL import ImageTk, Image
import configparser
import math
import RPi.GPIO as GPIO
from smbus2 import SMBusWrapper #BV For I2C communication
import glob                     #BV Config file parser

address = 0x08

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT, initial = 1)
GPIO.setup(9, GPIO.OUT)
GPIO.output(9, 0)
#Sets charging relay low to start, puts emergency pin high



#os.system('sudo modprobe w1-gpio')
#os.system('sudo modprobe w1-therm')
#os.system('sudo dtoverlay w1-gpio gpiopin=5')
#os.system('sudo dtoverlay w1-gpio gpiopin=18')
#os.system('sudo dtoverlay w1-gpio gpiopin=6')
#(Commented out for testing, we did this manually in the terminal) initialization for temp sensors

base_dir = '/sys/bus/w1/devices/'
device_folder_high = base_dir + '28-00000af6a9ee'
device_folder_low = base_dir + '28-00000af6bc8e'
device_file_high = device_folder_high + '/w1_slave'
device_file_low = device_folder_low + '/w1_slave'
#finds paths for the temperature sensors

##How to get data from a config file:
## Option 1: name config file as .py extension, import values (easiest way, editable with IDLE
## Option 2: import ConfigParser

#variable used for example down below
#testvalueimportant = 5
parser = configparser.ConfigParser()
parser.read('CarConfig.ini')
#initialization for configuration file

class EcoCar:
    """Holds operating parameters of selected vehicle"""
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
    ConditioningTime = 20
    AirStarveTime = 6
#Class for variables related to ecocar

class OperatingSpecs:
    """Holds variables for current values of load bank operation"""
    BatVolt = None
    CellVolt = None
    CellCurr = None
    TempLower = 31
    TempUpper = None
    FanSpeedLower = 10
    FanSpeedUpper = 10
#Class for variables related to operation
    
#BV Create an instance of each class
InsOS = OperatingSpecs()

YourEcoCar = EcoCar()







def read_temp_raw(file_name):
    """Gets raw data from temperature sensor

    file_name -- address of temperature sensor
    """

    f = open(file_name, 'r')
    lines = f.readlines()
    f.close()
    return lines
#gets direct output from terminal
 
def read_temp(file_name):
    """Converts raw data from temperature sensor to degrees celsius

    file_name -- address of temperature sensor
    """

    lines = read_temp_raw(file_name)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.1)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0      #BV Why do we need temperature in Fahrenheit?
        return temp_c
#converts direct ouput to legible output in celcius
    
def tempSensing():
    #InsOS.TempLower = read_temp(device_file_low)   #BV Uncomment these to enable temperature sensing
    #print(InsOS.TempLower)
    InsOS.TempUpper = read_temp(device_file_high)
    print(InsOS.TempUpper)

#Calls temperature sensing

def translate(value, leftMin, leftMax, rightMin, rightMax):
    """Uses predefined limits for enclosure temperature to convert
    temperature sensor readings to an appropriate fan speed. Fan speed
    will typically be output to the ATMega via I2C using an integer
    between 1 and 10.

    value -- temperature sensor reading
    leftMin -- lowest temperature at which fan will be activated
    leftMax -- temperature for maximum fan speed
    rightMin -- output value for minimum fan speed (typical: 1)
    rightMax -- output value for maximum fan speed (typical: 10)
    """

    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

#Scales values from temperature to scaled values

def fanTransmission():
    """Sets desired fan speed in "InOS" (current operating values) as
    an integer value from 0 to 10.
    """

    if(InsOS.TempLower > 30 and InsOS.TempLower < 55):
        #BV If temperature is within normal operating range, provide
        # scaled output for fan speed
        InsOS.FanSpeedLower = int(math.floor(translate(InsOS.TempLower, 30, 55, 1, 10)))
    elif(InsOS.TempLower > 55 and InsOS.TempLower < 60):
        #BV If temperature is high, but not critical, run fans at
        # maximum speed
        InsOS.FanSpeedLower = 10
    elif(InsOs.TempLower < 30):
        #BV If temperature is low, turn fans off
        InsOS.FanSpeedLower = 0
    else:
        #BV Outside of acceptable range, shutdown with error code 3
        # (Low temperature zone outside of safe limits)
        desync_shutdown(3)

    if(InsOS.TempUpper > 30 and InsOS.TempUpper < 75):
        InsOS.FanSpeedUpper = int(math.floor(translate(InsOS.TempUpper, 30, 75, 1, 10)))
    elif(InsOS.TempUpper > 75 and InsOS.TempUpper < 85):
        InsOS.FanSpeedUpper = 10
    elif(InsOS.TempUpper < 30):
        InsOS.FanSpeedUpper = 0
    else:
        desync_shutdown(4)

#Sets the fan speeds based on the temperatures take, both scaled 1-10

def EndSending():
    ValueComm(0)

#Called when program is stopping


#If you're looking through this code and you need to edit the polarization curve or conditioning cycle
#I'm sorry.
#When I wrote my variable names for these sections, I did not consider that they could be considered confusing
#until i looked at them again that is.....
#For the record, CurrentCurrent refers to amperage at this time, StepStep refers to the increase in step size per iteration
#May god have mercy on you if youre editing this.
#-Nikolai, the guy who wrote the python code and was definitely sleep deprived when I wrote this
#P.S. if you're editing this in the 2019-2020 university year, message me at marianic@ualberta.ca and I'll gladly help fix/atone for my crimes


    #NOTES
    #Value 0 Stops output
    #Values 1-120 represent step sizes of 0.5A, so 0.5-60A outputs
    #121 triggers air starve cycle
    #122 prompts the ATMega to send the Pi values
    #123 is the trigger to send fan speeds to the ATMega
    #Dont attempt to send values higher that 123, as it will be taken as a higher current that 60A (if you want to fix this, look at Jaya's code)
    
    
def polarization_curve():
    GPIO.output(9, 1)
    #turns on charging relay pin
    CurrentCurrentValue = YourEcoCar.SCurrentStep
    #InsertCode for after x time
    while (CurrentCurrentValue <= YourEcoCar.ECurrentStep):
        ValueComm(CurrentCurrentValue)
        CurrentCurrentValue += YourEcoCar.CurrentStepStep
        timeWait(0.25)
        #code to wait x time
    ValueComm(YourEcoCar.ECurrentStep)
    timeWait(0.5)
    CurrentCurrentValue = YourEcoCar.ECurrentStep
    while (CurrentCurrentValue >= YourEcoCar.SCurrentStep):
        ValueComm(CurrentCurrentValue)
        CurrentCurrentValue -= YourEcoCar.CurrentStepStep
        timeWait(0.5)
    #final wait x time
    EndSending()

#Steps polarization curve values after set times

    

def air_starve():
    AirStarveTime = 6
    GPIO.output(9, 1)
    ValueComm(121)
#121 is the trigger for air stave
    timeWait(AirStarveTime)
    EndSending()
#Air starve cycle

    
def conditioning_cycle():
    ConditioningTime = 20;
    # 20 Minutes for conditioning cycle, this is what we agreed on but
    # is not some sort of mandatory value, could be made into a config
    # file value
    
    GPIO.output(9, 1)
    ValueComm(YourEcoCar.CCurrentStep)
    timeWait(ConditioningTime) 
    EndSending()
    #Constant current for conditioning cycle

def ValueReceive():
    failcounter = 0
    garbagevalues = 0
    skipdatacounter = 0
    while 1:
        try:
            with SMBusWrapper(1) as bus:
                data = bus.read_i2c_block_data(address, 122, 7)
                # prepared to receive 7 values, the first will always be
                # 122 and is omitted
                for received in data:
                    if received > 1024:
                        failcounter += 1
                        skipdatacounter = 1
                        if(failcounter > 3):
                            desync_shutdown(2)
                if skipdatacounter == 0:
                    garbagevalues = 0
                    InsOS.BatVolt = ((data[1]<<8) + (data[2]))*(0.0146)
                    # Receives 10 bit value in 2 sets, pieces them 
                    # together here, multiplies by step size.
                    InsOS.CellVolt = ((data[3]<<8) + (data[4]))*(0.0478)
                    InsOS.CellCurr = ((511-((data[5]<<8) + (data[6])))*0.168)
                    break
                skipdatacounter = 0
        except:
            failcounter += 1
            if(failcounter > 3):
                desync_shutdown(1)
        timeout = time.time() + 1
        #Safety if bad transmit, holds for 1 second between each request
        while(time.time() < timeout):
            pass
        
def ValueComm(important_value):
# OK SO HERES THE DEAL WITH HOW THIS CODE WORKS
# address is constant, its what we need to talk between the two devices
# I'm using read here instead of write because they actually do
# effectively the same thing in this case because theres 0 data to
# transmit
# This library is stupid.
# effectively, important_value which is called an offset value, is sent
# to the ATMega
# Jaya has set it up to read those offsets as commands
# Because this library is silly and its actually the most memory 
# efficient way.
# Heres a good project for anyone looking to make this code better:
# Rewrite the I2C protocols, I really didnt want to, I wouldn't
# recommend you do either because if it ain't broke dont fix it
# I'm sorry. -Nik
    
    failcounter = 0
    # if the code fails to send 3 times in a row, the entire program
    # grinds to a halt, yep.
    # if i lose control of the code through this, you need to cycle
    # power because everything is fudged.

    if(important_value == 0):
        while 1:
            with SMBusWrapper(1) as bus:
                bus.read_i2c_block_data(address, important_value, 0)
                time.sleep(0.01)
                # This case is only for sending 0, as its not going to
                # try/except, its just gonna keep doing it until it works.
                
    while 1:
        try:
            with SMBusWrapper(1) as bus:
                bus.read_i2c_block_data(address, important_value, 0)
                print('SENDING STEP VALUE {}'.format(important_value))
                #writes to terminal what you're sending
                break
        except:
            failcounter += 1
            if(failcounter > 3):
                desync_shutdown(1)
    
        # Decreasing delay may create more transmission errors.
        time.sleep(0.01)

def ValueWrite(fanValueOne, fanValueTwo):
    failcounter = 0
    while 1:
        try:
            with SMBusWrapper(1) as bus:
                bus.write_i2c_block_data(address, 123, [fanValueOne, fanValueTwo])
                #Sends 2 fan values, Jaya's code sets both to the higher one, but she didnt seem to know what she was doing so I just sent both anyways
                break
        except:
            failcounter += 1
            if(failcounter > 3):
                desync_shutdown(1)
                #Shuts down in error if the program desyncs

def SafetyCheck():
    if(InsOS.BatVolt < 11):
        #battery voltage must stay above 11 for things to work.
        desync_shutdown(5)
    #if((InsOS.CellVolt < 10) or (InsOS.CellVolt > 46)):
        #(Commented out) I realised this may trigger in the event of air starve, if you add an exception for that, this works
        #desync_shutdown(6)
    if(((YourEcoCar.method == "Air Starve") and (InsOS.CellCurr > 20)) or ((YourEcoCar.method != "Air Starve") and ((InsOS.CellCurr < (CurrentCurrentValue/2)-2) or (InsOS.CellCurr > (CurrentCurrentValue/2)+2)))):
        desync_shutdown(7)
        #Checks the cell current for safe values
    
def timeWait(timelimit):
    timeoutbig = time.time() + (60*timelimit)
    #any inputs are in the scale of minutes
    while (time.time() < timeoutbig):

        timeout = time.time() + 1
        while(time.time() < timeout):
            pass

        tempSensing()
        #fanTransmission()
        ValueWrite(InsOS.FanSpeedLower, InsOS.FanSpeedUpper)
        #do the temp sensing first each cycle
        
        #TODO temp send functions for both areas

        ValueReceive()
        #Checks the cell parameters
        #SafetyCheck()
        print("Battery Voltage: {}, Cell Voltage: {}, Cell Current: {}".format(InsOS.BatVolt, InsOS.CellVolt, InsOS.CellCurr))
        #writes to terminal.
        
        #textframe.config(font = ("Arial", 16), pady=150)
        #textframe.pack()
        #SafetyChecks()



def desync_shutdown(trigger):
    EndSending()
    #Sends 0 at the start of this function

    if trigger == 1:
        errormessage = "The device has desynced with the PWM device"
    elif trigger == 2:
        errormessage = "The device received too many garbage values in a row and has shut down"
    elif trigger == 3:
        errormessage = "The controller devices have begun overheating, and must be stopped"
    elif trigger == 4:
        errormessage = "The power devices have begun overheating, and must be stopped"
    elif trigger == 5:
        errormessage = "The battery voltage has fallen too far and the device must be stopped."
    elif trigger == 6:
        errormessage = "The cell voltage has gone too high or too low and the device must be stopped."
    elif trigger == 7:
        errormessage = "The cell current has gone too high or too low and the device must be stopped."
    else:
        errormessage = "You shouldn't be reading this, if you do, power down the system and have it exorcised."

        #error messages
        
    panic_frame = tk.Frame(root, height=380, width=600)
    panic_frame.pack_propagate(False)
    panic_frame.place(x=80, y=50)

    panic_label = tk.Label(panic_frame, text='Uh oh')
    panic_label.config(font=("Arial", 24), bg='blue')
    panic_label.pack(fill="both")

    panic_button = tk.Button(panic_frame, text="Understood", command=root.destroy())
    panic_button.config(font=("Arial", 16), bg='black', fg='white')
    panic_button.pack(side="bottom", fill="x")

    panic_textbox = tk.Text(panic_frame, width=50, height=20)
    panic_textbox.config(font=("Arial", 12))
    panic_textbox.pack(fill="both")
    panic_textbox.insert(tk.END, "%s" % (errormessage))

    #This builds tKinter boxes


#The rest of this code consists of tKinter library stuff
#I'm not going to go into detail in how it all works, but
#The documentation for this library is beautiful and i'd recommend
#reading it before touching this stuff
#I'll give notes when required, BUT its on you to read the documentation
#because this is a fairly systematic code, you could literally copy paste one block
#and make another block with it.


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
    #Insert appropriate warning text here
    

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
    #This other button is important because it will allow us to do custom inputs, but is not operational yet

def alice_select():
    
    YourEcoCar.name = "Alice"
    process_select()
    #This is done for config file stuff
    
def sofie_select():

    YourEcoCar.name = "Sofie"
    process_select()
     #This is done for config file stuff

def picked_other():

#THIS IS A PLACEHOLDER BOX, IT DOES NOTHING AND CAN BE REMOVED IF DESIRED
    
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

#Pick your cycle
    
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
    #Draws conditioning parameters for the correct vehicle based on your cycle selection
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



    #The following is all checks to make sure that nobody inserted stupid values into the config file

    #IMPORTANT FOR PROGRAMMERS:
    #I have no idea if entering text instead of numbers is detected as a stupid value in this method, test this!
    #Also, disable generating non error buttons if an error is detected (should be just inserting it in a while loop)

    if(YourEcoCar.method == "Conditioning"):
        
        if(YourEcoCar.CCurrentStep > 60):
            #This checks to ensure safe maximum opperating conditions (limits conditioning current to 30A, pol curve to 60A)
            RS_title = tk.Label(RS_baseFrame, text="Unsafe Current Parameters detected, consult operating specifications for limits")
            RS_title.config(font=("Arial", 24), pady=150)
            RS_title.pack()
            
            RS_Error_button = tk.Button(RS_baseFrame, text="Start", command=vehicle_select)
            RS_Error_button.config(font=("Arial", 16), bg='black', fg='white')
            RS_Error_button.place(width=200, height=200, x=150, y=200)
            
    if(YourEcoCar.method == "Pol Curve"):
        if(YourEcoCar.SCurrentStep > YourEcoCar.ECurrentStep):
            #Consistency Checks
            RS_title = tk.Label(RS_baseFrame, text="Error in Current Step Definitions!")
            RS_title.config(font=("Arial", 24), pady=150)
            RS_title.pack()
        
            RS_Error_button = tk.Button(RS_baseFrame, text="Start", command=vehicle_select)
            RS_Error_button.config(font=("Arial", 16), bg='black', fg='white')
            RS_Error_button.place(width=200, height=200, x=150, y=200)
        elif((YourEcoCar.SCurrentStep > 120) or (YourEcoCar.ECurrentStep > 120)):
            #This checks to ensure safe maximum opperating conditions (limits conditioning current to 30A, pol curve to 60A)
            RS_title = tk.Label(RS_baseFrame, text="Unsafe Current Parameters detected, consult operating specifications for limits")
            RS_title.config(font=("Arial", 24), pady=150)
            RS_title.pack()
        
            RS_Error_button = tk.Button(RS_baseFrame, text="Start", command=vehicle_select)
            RS_Error_button.config(font=("Arial", 16), bg='black', fg='white')
            RS_Error_button.place(width=200, height=200, x=150, y=200)

    RS_title = tk.Label(RS_baseFrame, text="Ready!")
    RS_title.config(font=("Arial", 24), pady=50)
    RS_title.pack()

    RS_start_button = tk.Button(RS_baseFrame, text="Start", command=activation_sequence)
    RS_start_button.config(font=("Arial", 16), bg='black', fg='white')
    RS_start_button.place(width=200, height=200, x=150, y=200)
        
    RS_stop_button = tk.Button(RS_baseFrame, text="Stop", command=end_run)
    RS_stop_button.config(font=("Arial", 16), bg='black', fg='white')
    RS_stop_button.place(width=200, height=200, x=450, y=200)

    #RS_emerstop_button = tk.Button(RS_baseFrame, text="Emergency Stop", command=emergencystop_run)
    #RS_emerstop_button.config(font=("Arial", 16), bg='black', fg='white')
    #RS_emerstop_button.place(width=50, height=50, x=650, y=300)

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

    EndSending()
    
    end_frame = tk.Frame(root, height=380, width=600)
    end_frame.pack_propagate(False)
    end_frame.place(x=80, y=50)

    end_label = tk.Label(end_frame, text='Ending Process')
    end_label.config(font=("Arial", 24), bg='blue')
    end_label.pack(fill="both")

    end_button = tk.Button(end_frame, text="Got It", command=vehicle_select)
    end_button.config(font=("Arial", 16), bg='black', fg='white')
    end_button.pack(side="bottom", fill="x")

    end_textbox = tk.Text(end_frame, width=50, height=20)
    end_textbox.config(font=("Arial", 12))
    end_textbox.pack(fill="both")
    end_textbox.insert(tk.END, "Shutting Down, please give the device a second to wind down.")

def emergencystop_run():
    GPIO.output(26, 0)
    root.destroy()
    #The ultimate kill switch, never called, but is available because i used it previously :/





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

subtitle1 = tk.Label(root, text="Version 1.0")
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

