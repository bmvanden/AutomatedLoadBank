# Vehicle name
name = "Sofie"

# Current to draw during conditioning cycle and duration to condition for
conditioningCurrent   = 15    # Amps
conditioningTime      = 20    # Minutes

# Minimum and maximum currents to draw during polarization curve
minCurrent            = 0     # Amps
maxCurrent            = 40    # Amps

# Step size and duration to use when changing current during polarization
# curve cycle. During a polarization curve, the load bank will hold the 
# "minCurrent" for the "currentStepDuration", then increase the load
# by "currentStepSize" and wait for "currentStepDuration" again. It will
# continue to step up until reaching "maxCurrent". Then, it will step back
# down to "minCurrent" again.
currentStepSize       = 5     # Amps
currentStepDuration   = 60    # Seconds

# Duration to run air starve cycle for. Air starve cycle will ramp up the
# PWM load to maximum, then apply an additional discrete load for the 
# duration specified.
airStarveTime         = 20    # Minutes
