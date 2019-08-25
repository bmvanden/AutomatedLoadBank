import configuration as cfg

class EcoCarModel:
    def __init__(self):
        # Get vehicle specifications from configuration file
        name = cfg.name
        conditioningCurrent = cfg.conditioningCurrent
        conditioningTime = cfg.conditioningTime
        minCurrent = cfg.minCurrent
        maxCurrent = cfg.maxCurrent
        currentStepSize = cfg.currentStepSize
        currentStepDuration = cfg.currentStepDuration
        airStarveTime = cfg.airStarveTime
        
        # Current operating parameters for load bank
        PiStatus = 0            // See I2CThread.py for explanation of states
        desiredEnclTemp = 35    // degrees C - fan speed adjusts to target this setpoint
        actualLoadTemp = 0      // measured above load resistors
        actualContrTemp = 0     // measured above controller board
        targetLoadCurrent = 0   // amps - desired load on fuel cell
        
        ATMegaStatus = 0
        actualLoadCurrent = 0   // amps - actual load on fuel cell
        actualLoadVoltage = 0   // volts - fuel cell voltage
        batteryVoltage = 0      // volts - 12V internal battery voltage
        
    def refreshData(target):
        if target.dataOk:
            # Update data to send to ATMega over I2C. I2C interface only supports integers
            # from 0-255, so real values are doubled and converted to int to reduce step size.
            target.PiData = [PiStatus, int(desiredEnclTemp * 2), int(actualLoadTemp * 2),
                             int(actualContrTemp * 2), int(targetLoadCurrent * 2)]
            
            # Update data received from ATMega over I2C.
            ATMegaStatus = ATMegaData[0]
            actualLoadCurrent
            actualLoadVoltage
            batteryVoltage
