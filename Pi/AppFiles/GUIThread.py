import threading
import tkinter as tk
from AppFiles import I2CThread
import time

class GUIThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print("Starting " + self.name)
        # Create the main window
        root = tk.Tk()
        root.title("EcoCar GUI")         
        # Set window size to match 7" SparkFun LCD (800 x 480)
        root.resizable(False, False)
        root.geometry("800x480")

        #Data for live update of GUI
        PiData0 = tk.IntVar()
        PiData1 = tk.IntVar()
        PiData2 = tk.IntVar()

        #Display Variable Values for Pi and ATMega
        PiDataTitle = tk.Label(root, text="Pi Data")
        PiDataTitle.pack()

        PiDataLabel1 = tk.Label(root, textvariable=PiData0)
        PiDataLabel1.pack()
        PiDataLabel2 = tk.Label(root, textvariable=PiData1)
        PiDataLabel2.pack()
        PiDataLabel3 = tk.Label(root, textvariable=PiData2)
        PiDataLabel3.pack()
        #PiDataUpdateButton = tk.Button(root, text="Increment Values", command=)
        #PiDataUpdateButton.pack()
        
        while 1:
            root.update()
            PiData0.set(I2CThread.PiData[0])
            PiData1.set(I2CThread.PiData[1])
            PiData2.set(I2CThread.PiData[2])
            time.sleep(0.1)
            
        



