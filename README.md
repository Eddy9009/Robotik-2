# Robotik-2

requiements:

NAO SDK / Python-API :
pip install naoqi

Check and example:
from naoqi import ALProxy

robotIP = "192.168.1.10"  # IP eures NAO

port = 9559

tts = ALProxy("ALTextToSpeech", robotIP, port)

tts.say("Hallo, ich bin NAO!")

Pygame:
pip install pygame

Check and example:
python -m pygame.examples.aliens








