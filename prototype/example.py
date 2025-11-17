from simconnect_mobiflight import SimConnectMobiFlight
from mobiflight_variable_requests import MobiFlightVariableRequests
from time import sleep
from SimConnect import *
# print("Esperando")
# sleep(60*25)


# MAIN
sm = SimConnectMobiFlight()
ae = AircraftEvents(sm)
vr = MobiFlightVariableRequests(sm)
vr.clear_sim_variables()



# # sleep(1)
# req = "(A:NAV OBS:1, Degrees)"
# vr.get(req)
# sleep(0.1)
# value = vr.get(req)
# print(value)
# ae.find("KOHLSMAN_INC")()
# sleep(0.1)
# value = vr.get(req)
# print(value)
# # COM_RADIO_SWAP
'''
weights = [0,10*80,40*80,320*85,4000,4000,2000]

for i in range(1,7):
    vr.set(f"{float(weights[i])/0.453592} (>A:PAYLOAD STATION WEIGHT:{i}, Pounds)")
    sleep(0.1) 

vr.get("(A:CG PERCENT, Percent Over 100)")
sleep(0.1) 
cg = (vr.get("(A:CG PERCENT, Percent Over 100)")*100 + 9.714)
sleep(0.1) 

zfw = 168600
for i in weights:
    zfw += i
print(f'ZFW: {zfw:.1f} | CG: {cg:.1f} ')
'''

var = "(A:EXTERNAL POWER AVAILABLE:1, Bool)"

vr.get(var)
sleep(0.1) 
print(vr.get(var))

# # vr.set("0 1 3 4 4 (A:TRANSPONDER STATE:1, Number) case (>A:TRANSPONDER STATE:1, Number)")
# for i in range(50,-5,-5):
#     print(i)
#     vr.set(f"{float(i)} (>L:var_RNAV_VOLUME, Number)")


sleep(1)
# sleep(1)
# a = horner_scheme_bcd32(124850000)
# print(a)
# ae.find("KEY_PARKING_BRAKES")()
# ae.find("COM2_RADIO_SET")(9029)
# ae.find("COM_RADIO_SET")(9029)
# ae.find("COM2_RADIO_SET")(9029)
# vr.set("(>K:TOGGLE_EXTERNAL_POWER)")
# vr.set("3 1013 16 * (>K:2:KOHLSMAN_SET)")

# sleep(0.1)
# Event(b'MobiFlight.TRANSPONDER_Push_OFF', sm)()