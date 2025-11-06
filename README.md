# Robotik-2

requirements:

#######################################################################################

Visual-Studio-Code :

py27 -m pip install virtualenv

py27 -m  virtualenv Projekt

danach nicht vergessen die gitgore Datei löschen(im Projekt-Ordner), sonst pusht git keine Änderungen !!!

#######################################################################################

Powershell:

$env:PYTHONPATH += ";C:\Users\Seminar\Desktop\Robotik-2\SDK\lib"

test:

echo $env:PYTHONPATH

#######################################################################################

Check and example:

from naoqi import ALProxy

robotIP = "192.168.13.188"  # IP  NAO

port = 9559

tts = ALProxy("ALTextToSpeech", robotIP, port)

tts.say("Hallo, ich bin NAO!")

#######################################################################################

Pygame:

py27 -m pip install pygame

Check and example:

py27 -m pygame.examples.aliens








