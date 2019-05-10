# AutomatedLoadBank
Python user interface for Raspberry Pi driven automated load bank

### Project Abstract
An automated resistive load bank was created to test and optimize hydrogen fuel cells for the University of Alberta EcoCar team. The load bank utilizes a touchscreen graphical user interface to select automated testing cycles and pulse width modulation for a variable load. The load bank handles up to 60 A of current from the 46 V fuel cell with 1000 W of power dissipation capability. Furthermore, it is battery powered, portable, and weather resistant.

### Software Overview
The automated load bank is managed primarily by a Raspberry Pi computer, and its I/O capabilities are extended using an Atmel ATMega328P. In this repository lies the software for the Raspberry Pi. The software is primarily written in Python and uses the TkInter graphics library to develop a touchscreen user interface.

### Communication With Other Modules
#### ATMega328P via I2C
**Raspberry Pi to ATMega328P**
* 0 -- Stop output
* 1-120 -- Desired load in steps. Step size is 0.5 A, so a value of 64 would correspond to a 32 A load.
* 121 -- Start an air starve cycle. Operating parameters are set in the ATMega328P.
* 122 -- Data request for all inputs read by ATMega328P. (Fuel cell voltage, fuel cell current, battery voltage)
* 123 -- Trigger to tell ATMega328P that fan speeds will be sent next.
* **WARNING:** Sending values greater than 123 will be interpreted by the ATMega328P as desired current values of greater than 60 A which is outside the design parameters for the hardware.

**ATMega328P to Raspberry Pi**


### Version History

### Pi Configurations Necessary to Run this Software
**Install Raspbian operating system using Etcher to put the latest image on an SD card**\
    [TUTORIAL](https://www.raspberrypi.org/documentation/installation/installing-images/)
    
**Set date for Wi-Fi access**\
  `sudo date -s "Dec 27 14:54"`
    
**Update software repositories & installed software**\
  [TUTORIAL](https://www.raspberrypi.org/documentation/raspbian/updating.md)\
  `sudo apt-get update`\
  `sudo apt-get dist-upgrade`
  
   
**Install "Matchbox" on-screen software keyboard**\
  `sudo apt-get install matchbox-keyboard`
    
**Install TkInter and Python image library**\
`sudo apt-get install tk`\
`sudo apt-get install python-imaging`\
`sudo apt-get install python-imaging-tk`\
`sudo apt-get install python3-pil.imagetk`

**Set Python3 as default environment**\
Edit bash file: `nano ~/.bashrc`\
Add at the end:
```
alias python='/usr/bin/python3'
alias pip=pip3
```
Run bash file: `source ~/.bashrc`\

**Enable I2C**\
`sudo raspi-config` -> **5 Interfacing Options** -> **P5 I2C** -> **yes** -> **Finish**

**Add Matplotlib dependencies**
```
sudo apt-get install libatlas3-base libffi-dev at-spi2-core python3-gi-cairo
pip install cairocffi
pip install matplotlib
```

### Handy Features/Resources
**Display brightness**\
`sudo bash -c "echo n > /sys/class/backlight/rpi_backlight/brightness"`\
where 0 < n < 255 (255 is maximum brightness)\
[*Alternate Method*](https://raspberrypi.stackexchange.com/questions/46225/adjusting-the-brightness-of-the-official-touchscreen-display)
```
>>> import rpi_backlight as bl
>>> bl.set_brightness(255)
>>> bl.set_brightness(20, smooth=True, duration=3)
>>> bl.get_max_brightness()
255
>>> bl.get_actual_brightness()
20
>>> bl.get_power()
True
>>> bl.set_power(False)
```
