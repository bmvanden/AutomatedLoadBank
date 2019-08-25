import threading
import time
import smbus2

# Holds data to be received from ATMega
ATMegaData = [0, 1, 3, 50, 80, 0, 0, 5]

# Holds data to be sent to ATMega
PiData = [3, 10, 0]

readErrCounter = 0
writeErrCounter = 0


class I2CThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print("Starting " + self.name)

        # Give thread time to initialize
        time.sleep(2)

        PiStatusOptions = {0: "Boot up",
                           3: "Normal Operation",
                           4: "Load Overtemp",
                           5: "Controller Overtemp",
                           6: "Load Overcurrent",   
                           7: "Fuel Cell Voltage too High",
                           8: "Fuel Cell Voltage too Low",
                           9: "Battery Low",
                           10:"Air Starve Relay Active",
                           15:"Lost Communication"}

        while (1):
            """
            Read 7 bytes from ATMega (2 bytes FuelCellCurrent, 2 bytes 
            FuelCellVoltage, 2 bytes BatteryVoltage, 1 byte ATMega status)

            Address:    8
            Offset:     0
            of Bytes:   7
            """
            try:
                with smbus2.SMBusWrapper(1) as bus:
                    ATMegaData = bus.read_i2c_block_data(8, 0, 8)
                readErrCounter = 0
            except:
                #print("Read Error")
                readErrCounter += 1

            time.sleep(0.5)

            """
            Write 3 bytes to ATMega (1 byte FanSpeed, 1 byte Target Current,
            1 byte Pi Status)

            Address:    8
            Offset:     0
            # of bytes: 3
            """
            try:
                with smbus2.SMBusWrapper(1) as bus:
                    bus.write_i2c_block_data(8, 42, [PiData[0],PiData[1],PiData[2]])
                PiData[0] += 1
                PiData[1] += 2
                PiData[2] += 1
                if PiData[2] > 15:
                    PiData[2] = 0
                writeErrCounter = 0
            except:
                #print("Write Error")
                writeErrCounter += 1

            time.sleep(0.5)

            print("\n\nATMega Data: ")
            print(ATMegaData)
            print("Pi Data: ")
            print(PiData)
            print("Read Error Counter: % 2d  Write Error Counter: % 2d" 
                %(readErrCounter, writeErrCounter))
            print("Status: % s"
                %(PiStatusOptions.get(PiData[2], 'INVALID STATE')))
