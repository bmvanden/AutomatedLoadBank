"""
Threading example from: https://www.tutorialspoint.com/python/python_multithreading.htm
"""

#!/usr/bin/python

from AppFiles import I2CThread
from AppFiles import GUIThread

# Create new threads
thread1 = I2CThread.I2CThread(1, "Thread-1", 1)    # Send and receive data from ATMega
thread2 = GUIThread.GUIThread(2, "Thread-2", 2)    # Run the user interface

# Start new Threads
thread1.start()
thread2.start()

print("Exiting Main Thread")
