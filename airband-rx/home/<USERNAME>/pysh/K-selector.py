#!/bin/python


##################################################################
## Airband_receiver
## Copyright (C) 2017  Loxia labs
## 
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
## See the GNU General Public License for more details:
## <http://www.gnu.org/licenses/>.
###################################################################


import RPi.GPIO as GPIO
import subprocess, os, signal
from time import sleep
from gpiozero import Buzzer


### Using bcm-style pin numbers ----------------------------------------
GPIO.setmode(GPIO.BCM)


### Pick and pull-up input pins ----------------------------------------
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_UP) # The <ENTER> pin
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)  # The <SHTDWN> pin 

for bitpin in range(22, 26):                    # 22, 23, 24, 25 (the nibble array)
    GPIO.setup(bitpin, GPIO.IN, pull_up_down = GPIO.PUD_UP)

bz = Buzzer(15)                                 # GPIO 15. (The gpiozero library defaults to bcm numbering)
bz.on()

### Global variables ---------------------------------------------------
is_entered = False                              # Flag for the <ENTER> signal state

present_Kproc = subprocess.Popen("/home/<USERNAME>/pysh/sh/K11.sh")   # The running process' default rx channel


### Function definitions -----------------------------------------------
def no_mercy():
    global present_Kproc
    present_Kproc.terminate()                   # G'bye
    sleep(1)
    
# Annoyingly, the daughters now refuse to do the right thing and prudently accompany their deceased parent... 
# Conveniently, we only need to stab one of them (e.g. rtl_fm), and then the sister (play) soon croaks too!:
    pid_rtl_fm = map(int, subprocess.check_output(["pidof", "rtl_fm"]).split())    # Find the pid
    pidint = int(pid_rtl_fm[0])                 # Output is list-formatted, so needs casting to int first
    os.kill(pidint, signal.SIGTERM)             # die PID, die
    sleep(1)


def decimalize():                               # Mapping GPIO's to the selected nibble:
    b1 = GPIO.input(22)                         # 22 >> LSB (1)
    b2 = GPIO.input(23)                         # 23 >> 2nd (2)
    b3 = GPIO.input(24)                         # 24 >> 3rd (4)
    b4 = GPIO.input(25)                         # 25 >> 4th (8)
    num = b1 + (b2 * 2) + (b3 * 4) + (b4 * 8)   # num: hexadecimal, zero-based, inverted logic
    numnum = 1 + (15 - num)                     # numnum: decimal, 1-based, "reverted" logic (much better!)
    
    return numnum


def tune_in(kanal):
    global is_entered
    is_entered = False                          # We mustn't start more than one rx channel per ENTER signal
    
    kanyl = str(kanal)                          # This time we need to convert ints to a string
    if kanal < 10:                              # If its a single digit ...
        kanyl = "0"+kanyl                       # ... add a leading zero for neatness
    pKp = subprocess.Popen("/home/<USERNAME>/pysh/sh/K"+kanyl+".sh") # Relaunch the updated "present_Kproc" object
    print("*** Switching to channel "+kanyl)

    return pKp


def fade_out():                                 # "Stalling rattle" boogie!
    bz.beep(on_time=0.018,  off_time=0.1,   n=8, background=False)
    bz.beep(on_time=0.025,  off_time=0.13,  n=5, background=False)
    bz.beep(on_time=0.035,  off_time=0.18,  n=3, background=False)
    bz.beep(on_time=0.05,   off_time=0.25,  n=2, background=False)
    bz.beep(on_time=0.07,   off_time=0.35,  n=2, background=False)


def shuddup():
    fade_out()			                # First we emit the expressive piezo routine
    print("=== GOING DOWN NOW ===")             # Fair warning (if you're watching a screen...)
    os.system("sudo shutdown -h now")           # Now we die in peace


print("Here we go... Press Ctrl+C to exit")
################################################################################################

try:
    while 1:
        if GPIO.input(18) == 0:             # <ENTER> pin was shorted to GND
            is_entered = True               # ... and don't forget it
            print("\n ENTER key was pressed")
            no_mercy()                      # Commence by killing all running rx related processes           

        if is_entered:
            present_Kproc = tune_in(decimalize())   # Serve up the selected rx channel and save new PID
        
	if GPIO.input(4) == 0:              # <SHTDWN> pin was shorted to GND. This is not fun anymore.
       	    print("\n=== SHTDWN was triggered!")
	    shuddup()
	
except KeyboardInterrupt:
    GPIO.cleanup()                          # Back-out of script nicely



