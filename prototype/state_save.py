from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from time import sleep
import datetime
import os
 

sm = SimConnectMobiFlight()
vr = MobiFlightVariableRequests(sm)
vr.clear_sim_variables()

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "fsr500_config.txt")
with open(file_path, "r") as cfg_file:
    lines = cfg_file.read().splitlines()

def find_highest_number():
    files = os.listdir(script_dir)
    numbers = [int(file.split('_')[1].split('.')[0]) for file in files if file.startswith("M500state_") and file.split('_')[1].split('.')[0].isdigit()]
    if numbers:
        return max(numbers)
    else:
        return 0

f_name = os.path.join(script_dir,"M500state_" + str(find_highest_number()+1) + ".txt")
print("Saving to file: ")
print(f_name)
sleep(1)

f = open(f_name, "w")
f.write("Saved Config at ")
f.write(str(datetime.datetime.now()))
f.write("\r\n")


vr.set("1 (>L:FSR_M500_BATTERY_SWITCH_ON)")
sleep(1)

for i in(lines):   
    if i and i[0] != "#":
        vr.get(i)
        sleep(0.1)
        value = vr.get(i)
        string = str(value) + " (>"+ i[1:] + "\r\n" 
        print(string)
        f.write(string)

f.close()
vr.set("0 (>L:FSR_M500_BATTERY_SWITCH_ON)")
sleep(1)
sm.exit()