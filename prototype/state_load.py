from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from time import sleep
from SimConnect import *
import os
import sys
def bcd_to_dec(num):
    return horner_scheme(num, 0x10, 10)

def dec_to_bcd(num):
    return horner_scheme(num, 10, 0x10)

def horner_scheme(num, divider, factor):
    remainder = num % divider
    quotient = num // divider
    result = 0

    if not (quotient == 0 and remainder == 0):
        result += horner_scheme(quotient, divider, factor) * factor + remainder
        
    return result
def horner_scheme_bcd32(num):
    divider = 32
    factor = 32
    result = 0
    
    # Implementing Horner's scheme for base-32
    while num > 0:
        remainder = num % divider
        num //= divider
        result = result * factor + remainder
        
    return result


sm = SimConnectMobiFlight()
ae = AircraftEvents(sm)
vr = MobiFlightVariableRequests(sm)
vr.clear_sim_variables()

def find_highest_number():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    files = os.listdir(script_dir)
    numbers=[]
    for file in files:
        if file.startswith("M500state_") and file.split('_')[1].split('.')[0].isdigit():
            numbers.append(int(file.split('_')[1].split('.')[0]))
        else:
            numbers.append(-1)
    if max(numbers) > 0:
        return os.path.join(script_dir, files[numbers.index(max(numbers))])
    else:
        return 0



if len(sys.argv) == 2:
    file_path = sys.argv[1]
    if os.path.isfile(file_path) and file_path.lower().endswith('.txt'):
        f_name = file_path
        print("Loading user file: ")
else:
    f_name = find_highest_number()
    print("Loading most recent file: ")
print(f_name)
sleep(1)
with open(f_name, "r") as cfg_file:
    lines = cfg_file.read().splitlines()

vr.set("1 (>L:FSR_M500_BATTERY_SWITCH_ON)")
sleep(1)
# vr.set("1 (A:AVIONICS MASTER SWITCH, Bool)")
ae.find("AP_ALT_VAR_INC")(1000)
sleep(1)
    
for i in lines: 
    print(i)   
    if "PITOT" in i and float(i[:2])==1:
        ae.find("PITOT_HEAT_ON")()
    elif "PARKING" in i and float(i[:2])==0:
        ae.find("PARKING_BRAKES")()
    elif "AVIONICS" in i and float(i[:2])==1:
        ae.find("TOGGLE_AVIONICS_MASTER")()
    elif "ALTERNATOR:1" in i and float(i[:2])==1:
        ae.find("TOGGLE_ALTERNATOR1")()
    elif "ALTERNATOR:2" in i and float(i[:2])==1:
        ae.find("TOGGLE_ALTERNATOR2")()
    elif "PUMP" in i and float(i[:2])!=1:
        ae.find("FUEL_PUMP")()
    elif "RUDDER" in i:  
        vr.get("A:RUDDER TRIM, Radians")
        sleep(0.1) 
        tgt = float(i.split("(")[0])       
        for j in range(int(abs(tgt)/0.00227)):    
            if tgt > 0.001:        
                ae.find("RUDDER_TRIM_RIGHT")()
            elif tgt < -0.001:
                ae.find("RUDDER_TRIM_LEFT")()
            sleep(0.1)

    elif "KOHLSMAN" in i:  
        vr.get("(A:KOHLSMAN SETTING MB:1, Millibars)")
        sleep(0.1) 
        tgt = float(i.split("(")[0])         
        while vr.get("(A:KOHLSMAN SETTING MB:1, Millibars)") < tgt:
            ae.find("KOHLSMAN_INC")()
            sleep(0.05) 
        while vr.get("(A:KOHLSMAN SETTING MB:1, Millibars)") > tgt:
            ae.find("KOHLSMAN_DEC")()
            sleep(0.05) 

    elif "TRANSPONDER" in i:
        a = float(i.split(' ')[0])
        ae.find("XPNDR_SET")(dec_to_bcd(int(a)))

    elif "COM STANDBY FREQUENCY:1" in i:
        ae.find("COM_STBY_RADIO_SET")(horner_scheme_bcd32(int(float(i.split(' ')[0]))))
        pass
    else:
        vr.set(i)
    sleep(0.1)
    
vr.set("0 (>L:FSR_M500_BATTERY_SWITCH_ON)")
sleep(1)
sm.exit()

'''
battery on
load pannel switches
set flaps
set e trim
set r trim
set pb
'''

