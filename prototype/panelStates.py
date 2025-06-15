import os
import sys
from time import sleep
import datetime
import os
import re
from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from SimConnect import *
 
def stateSave(file_path):
    sm = SimConnectMobiFlight()
    vr = MobiFlightVariableRequests(sm)
    vr.clear_sim_variables()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    saves_dir = os.path.abspath(os.path.join(script_dir, os.pardir)) +"\\saves\\"
    cfg_title = os.path.basename(file_path).split('.')[0]
    print("Config title:",cfg_title)
    with open(file_path, "r") as cfg_file:
        lines = cfg_file.read().splitlines()
    f_name = os.path.join(saves_dir, cfg_title + datetime.datetime.now().strftime("_%m%d-%H%M") + ".sav")
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
            string = f'value=[{value}] ' + i + '\r\n'
        else:
            string = i + '\r\n'
        
        print(string)
        f.write(string)

    f.close()
    print("Done")
    sm.exit()

def stateLoad(file_path):
    
    sm = SimConnectMobiFlight()
    ae = AircraftEvents(sm)
    vr = MobiFlightVariableRequests(sm)
    vr.clear_sim_variables()
       
    def getFromSim(command):   
            
        vr.get(command)
        sleep(0.1)
        return vr.get(command)

    def sendToSim(command):
        vr.set(command)
        sleep(0.1)
        
    def simEvent(event, value = False):
        ev = ae.find(event)
        if ev:
            if value:
                ev(value)
            else:
                ev()
        else:
            print("Could not find the event" , event)
        # sleep(0.1)

    
    with open(file_path, "r") as sav_file:
        lines = sav_file.read().splitlines()

        
    for i in lines: 
        if i=='' or i[0] == '#': #Skips comments
            continue
        print(i)
        # Value
        match = re.findall(r'value=\[(.*?)\]', i)
        if match != []:
            value = float(match[0])
        else:
            value = False    

        # Get function
        match = re.findall(r'value_get=\[(.*?)\]', i)
        if match != []:
            get_command = match[0]
        else:
            get_command = False    

        # Identifies if there is a set function and if it is global or value dependant 
        # Global set function
        match = re.findall(r'value_set=\[(.*?)\]', i)
        if match != []:
            set_value_command = match[0].split(';')
        else:
            set_value_command = False

        match = re.findall(r'value_inc=\[(.*?)\]', i)
        if match != []:
            inc_value_command = match[0]
        else:
            inc_value_command = False

        match = re.findall(r'value_dec=\[(.*?)\]', i)
        if match != []:
            dec_value_command = match[0]
        else:
            dec_value_command = False
        match = re.findall(r'value_toggle=\[(.*?)\]', i)
        if match != []:
            toggle_value_command = match[0]
        else:
            toggle_value_command = False

        match = re.findall(r'event_toggle=\[(.*?)\]', i)
        if match != []:
            toggle_event_command = match[0]
        else:
            toggle_event_command = False

            
        match = re.findall(r'value_dec_event=\[(.*?)\]', i)
        if match != []:
            dec_event_command = match[0]
        else:
            dec_event_command = False
        match = re.findall(r'value_inc_event=\[(.*?)\]', i)
        if match != []:
            inc_event_command = match[0]
        else:
            inc_event_command = False
        
        match = re.findall(r'value_set_event=\[(.*?)\]', i)
        if match != []:
            set_value_event = match[0]
        else:
            set_value_event = False
        

        # Set value
        if get_command and set_value_command:
            sim_value = getFromSim(get_command) 
            if sim_value != value:
                print('Command = ',get_command)
                print("Adjusting", sim_value," to ",value)
                if len(set_value_command)>1:
                    sendToSim(set_value_command[int(value)])
                else:
                    sendToSim(set_value_command[0].replace('$',str(value)))
            else:
                pass
        # Toggle Value
        elif get_command and toggle_value_command:
            sim_value = getFromSim(get_command) 
            if sim_value != value:
                print('Command = ',get_command)
                print("Adjusting", sim_value," to ",value)
                sendToSim(toggle_value_command)
        # Toggle event
        elif toggle_event_command and get_command:
            sim_value = getFromSim(get_command) 
            if sim_value != value:
                print('Command = ',get_command)
                print("Adjusting", sim_value," to ",value)
                simEvent(dec_event_command)
        # Increase/Decrease Value
        elif inc_value_command and dec_value_command:
            sim_value = getFromSim(get_command) 
            if sim_value > value:
                print('Command = ',get_command)
                print("Adjusting", sim_value," to ",value)
                while (getFromSim(get_command)) > value:
                    sendToSim(dec_value_command)                
            elif sim_value < value:
                print('Command = ',get_command)
                print("Adjusting", sim_value," to ",value)
                while (getFromSim(get_command)) < value:
                    sendToSim(inc_value_command)  
                    sleep(0.1)
        # Increase/Decrease event
        elif inc_event_command and dec_event_command:
            sim_value = getFromSim(get_command) 
            if sim_value > value:
                print('Command = ',get_command)
                print("Reducing", sim_value," to ",value)
                while (getFromSim(get_command)) > value:
                    simEvent(dec_event_command)
            elif sim_value < value:
                print('Command = ',get_command)
                print("Increasing", sim_value," to ",value)
                while (getFromSim(get_command)) < value:
                    simEvent(inc_event_command)   

        elif set_value_event and get_command:
            sim_value = getFromSim(get_command) 
            if sim_value != value:
                simEvent(set_value_event, int(value))

        elif set_value_command:
            sendToSim(set_value_command[0])

        elif toggle_event_command:
            sendToSim(toggle_value_command)
    # sm.exit()
    print("Done")


ascii_art = """
 _____                 _    _____ _        _            
 |  __ \\               | |  / ____| |      | |           
 | |__) |_ _ _ __   ___| | | (___ | |_ __ _| |_ ___  ___ 
 |  ___/ _` | '_ \\ / _ \\ |  \\___ \\| __/ _` | __/ _ \\/ __|
 | |  | (_| | | | |  __/ |  ____) | || (_| | ||  __/\\__ \\
 |_|   \\__,_|_| |_|\\___|_| |_____/ \\__\\__,_|\\__\\___||___/
"""

print(ascii_art)

if len(sys.argv) == 2:
    file_path = sys.argv[1]
    if os.path.isfile(file_path) and file_path.lower().endswith('.cfg'):
        f_name = file_path
        print("Config file loaded:",file_path)
        stateSave(f_name)
    elif os.path.isfile(file_path) and file_path.lower().endswith('.sav'):
        f_name = file_path
        print("Save file loaded:",file_path)
        stateLoad(f_name)
else:
    print("Incorrect File")

sleep(1)
