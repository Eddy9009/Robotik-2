# -------------------------------------------------------------------------------------------------------------------------
#
# Doku / Test Leds v1.01 [Python 2.7]
# (c) 12/2024 by n3r0 - all rights reversed.
#
# -------------------------------------------------------------------------------------------------------------------------

import threading
import sys
import math
import time

from naoqi import ALProxy

#ip_ignis = "ignis.local"
#ip_thera = "thera.local"

robotIP = "ignis.local" # robotIP
port = 9559
musik_path = "/home/nao/music"

# Initialize proxies
tts = ALProxy("ALTextToSpeech", robotIP, port)
leds = ALProxy("ALLeds", robotIP, port)
motion = ALProxy("ALMotion", robotIP, port)
memory = ALProxy("ALMemory", robotIP, port)
system = ALProxy("ALSystem", robotIP, port)
posture = ALProxy("ALRobotPosture", robotIP, port)
behavior_manager = ALProxy("ALBehaviorManager", robotIP, port)
audio_player = ALProxy("ALAudioPlayer", robotIP, port)
audio_device = ALProxy("ALAudioDevice", robotIP, port)

# -------------------------------------------------------------------------------------------------------------------------
   
def test_motors():

    # -------------------------------------------------------------------------------------------- INIT ROBOT

    #motion.rest(); quit()
    posture.goToPosture("Stand", 1.0)
    
    #motionProxy.actuator

    # 0xRRGGBB     
    leds.fadeRGB("EarLeds", 0x0000FF, 0.1) # Blue
    #leds.fadeRGB("FaceLeds", 0x00FF00, 0.1) # Green
    #leds.fadeRGB("FaceLeds", 0xFF0000, 0.1) # Red
    #leds.fadeRGB("FaceLeds", 0x0000FF, 0.1) # Blue
    leds.fadeRGB("FaceLeds", 0xFFFF00, 0.1) # Yellow
    
    c = 0 # for x in range(0, 3):

    while (not memory.getData("FrontTactilTouched")):
    
        st = 0.01
        c+=1

        if c == 10:
         leds.fadeRGB("FaceLeds", 0xFF0000, 0.1) # Red
         motion.angleInterpolation("HeadYaw", math.pi/2.0, 0.4, True)
         c = 10
        
        if c == 20:       
         leds.fadeRGB("FaceLeds", 0x0000FF, 0.1) # Blue
         motion.angleInterpolation("HeadYaw", (math.pi/2.0) *-1, 0.4, True)
         c  = 20
        
        if c == 30:
         c = 0
         leds.fadeRGB("FaceLeds", 0xFFFF00, 0.1) # Yellow
         motion.angleInterpolation("HeadYaw", 0.0, 0.4, True)

        LNames1 = ["Face/Led/Blue/Left/0Deg/Actuator/Value", "Face/Led/Blue/Left/90Deg/Actuator/Value","Face/Led/Blue/Left/180Deg/Actuator/Value","Face/Led/Blue/Left/270Deg/Actuator/Value"]
        leds.createGroup("LGroup1",LNames1)
       
        RNames1 = ["Face/Led/Blue/Right/0Deg/Actuator/Value", "Face/Led/Blue/Right/90Deg/Actuator/Value","Face/Led/Blue/Right/180Deg/Actuator/Value","Face/Led/Blue/Right/270Deg/Actuator/Value"]
        leds.createGroup("RGroup1",RNames1)
        
        LNames2 = ["Face/Led/Blue/Left/45Deg/Actuator/Value", "Face/Led/Blue/Left/135Deg/Actuator/Value","Face/Led/Blue/Left/225Deg/Actuator/Value","Face/Led/Blue/Left/315Deg/Actuator/Value"]
        leds.createGroup("LGroup2",LNames2)
       
        RNames2 = ["Face/Led/Blue/Right/45Deg/Actuator/Value", "Face/Led/Blue/Right/135Deg/Actuator/Value","Face/Led/Blue/Right/225Deg/Actuator/Value","Face/Led/Blue/Right/315Deg/Actuator/Value"]
        leds.createGroup("RGroup2",RNames2)

        time.sleep(st) 
        
        leds.on("LGroup1")
        leds.on("RGroup1")
        leds.off("LGroup2")    
        leds.off("RGroup2")
        
        time.sleep(st) 

        leds.on("LGroup2")
        leds.on("RGroup2")
        leds.off("LGroup1")    
        leds.off("RGroup1")    

    motion.angleInterpolation("HeadYaw", 0.0, 0.4, True)
    leds.fadeRGB("FaceLeds", 0x000000FF, 0.1) # Blue
    motion.rest()
    print motion.getSummary()
    leds.fadeRGB("FaceLeds", 0, 1.0) # off
    leds.fadeRGB("EarLeds", 0, 1.0) # off    
    quit()
    
    # --------------------------------------------------------------------------------------------
      
if __name__ == "__main__":
    test_motors()

# -------------------------------------------------------------------------------------------------------------------------

