from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from time import sleep
import datetime
import os
import re
 

sm = SimConnectMobiFlight()
vr = MobiFlightVariableRequests(sm)
vr.clear_sim_variables()

script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "tbm_config.txt")
saves_dir = script_dir+"\\saves\\"
with open(file_path, "r") as cfg_file:
    lines = cfg_file.read().splitlines()

def find_highest_number():
    files = os.listdir(saves_dir)
    numbers = [int(file.split('_')[1].split('.')[0]) for file in files if file.startswith("tbmstate_") and file.split('_')[1].split('.')[0].isdigit()]
    if numbers:
        return max(numbers)
    else:
        return 0

f_name = os.path.join(saves_dir,"tbmstate_" + str(find_highest_number()+1) + ".txt")
print("Saving to file: ")
print(f_name)
sleep(1)

f = open(f_name, "w")
f.write("# Saved Config at ")
f.write(str(datetime.datetime.now()))
f.write("\r\n")
sleep(1)

for i in(lines):       
    if i=='' or i[0] == '#': #Skips comments
        continue

    # Get function
    match = re.findall(r'value_get=\[(.*?)\]', i)
    if match != []:
        get_command = match[0]
    else:
        get_command = False   
    if get_command:    
        vr.get(get_command)
        sleep(0.1)
        value = vr.get(get_command) 
        if "BCD16" in get_command and value <0:
            value=int(value) + 2**16

        string = f'value=[{value}] ' + i + '\r\n'
    else:
        string = i + '\r\n'
    
    print(string)
    f.write(string)
        

f.close()
print("Done")
sm.exit()