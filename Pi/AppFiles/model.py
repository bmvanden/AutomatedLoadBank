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
    
