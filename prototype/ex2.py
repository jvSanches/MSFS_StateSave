from SimConnect import *
# Create SimConnect link
sm = SimConnect()
# Creat a function to call the MobiFlight AS1000_MFD_SOFTKEYS_3 event.
Sk3 = Event(b'MobiFlight.TRANSPONDER_Push_OFF', sm)
# Call the Event.
Sk3()
sm.exit()