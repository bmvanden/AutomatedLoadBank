



# This is the address we setup in the Arduino Program
address = 0x08
    

    
def EndSending():
    ValueComm(0)
    
def CommProcessPolCurve():
    GPIO.output(9, 1)
    #turns on charging relay pin
    CurrentCurrentValue = YourEcoCar.SCurrentStep
    #InsertCode for after x time
    while (CurrentCurrentValue <= YourEcoCar.ECurrentStep):
        ValueComm(CurrentCurrentValue)
        CurrentCurrentValue += YourEcoCar.CurrentStepStep
        timeWait(2)
        #code to wait x time
    ValueComm(YourEcoCar.ECurrentStep)
    timeWait(2)
    CurrentCurrentValue = YourEcoCar.ECurrentStep
    while (CurrentCurrentValue >= YourEcoCar.SCurrentStep):
        ValueComm(CurrentCurrentValue)
        CurrentCurrentValue -= YourEcoCar.CurrentStepStep
        timeWait(2)
    #final wait x time
    EndSending()
    SuccessScreen()

def CommProcessAirStarve():
    GPIO.output(9, 1)
    ValueComm(121)
    timeWait(AirStarveTime)
    
def CommProcessConditioning():
    GPIO.output(9, 1)
    ValueComm(CCurrentStep)
    timeWait(ConditioningTime) #make config file spec

def ValueReceive():
    failcounter = 0
    while 1:
        try:
            with SMBusWrapper(1) as bus:
                data = bus.read_i2c_block_data(address, 122, 7)
                BatVolt = (data[1]<<8) + (data[2])
                CellVolt = (data[3]<<8) + (data[4])
                CellCurr = (data[5]<<8) + (data[6])
                break
        except:
            failcounter += 1
            if(failcounter > 3):
                desync_shutdown()
        timeout = time.time() + 1
        while(time.time() < timeout):
            pass
        
def ValueComm(important_value):
    while 1:
        try:
            with SMBusWrapper(1) as bus:
                bus.read_i2c_block_data(address, important_value, 0)
                break
        except:
            failcounter += 1
            if(failcounter > 3):
                desync_shutdown()
    
        # Decreasing delay may create more transmission errors.
        time.sleep(0.01)

#def SafetyChecks():
    #if BatVolt < BATVALPLACEHOLDER :
        ##checks for low battery
        
    
def timeWait(timelimit):
    timeout = time.time() + 60*timelimit
    while (time.time() < timeout):

        #INSERT FAN VALUE FUNCTIONS
        
        #TODO temp send functions for both areas

        ValueReceive()
        textframe = tk.Label(RS_baseFrame, text = "Battery Voltage: {}, Cell Voltage: {}, Cell Current: {}".format(BatVolt, CellVolt, CellCurr))
        textframe.config(font = ("Arial", 16), pady=150)
        textframe.pack()
        #SafetyChecks()


def desync_shutdown():
    EndSending()
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
    panic_textbox.insert(tk.END, "an issue has occurred in the communication between the interface\nand the chip, the program will now close")
