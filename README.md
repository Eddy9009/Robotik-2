# Robotik-2

#######################################################

##Chris hast du den Kuchen schon wieder vergESSEN????##

#######################################################

requirements:

NAO SDK / Python-API :

Visual-Studio-Code :

py27 -m pip install virtualenv

py27 -m  virtualenv Projekt

Powershell:

$env:PYTHONPATH += ";C:\Users\Seminar\Desktop\Robotik-2\SDK\lib"

test:

echo $env:PYTHONPATH


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








