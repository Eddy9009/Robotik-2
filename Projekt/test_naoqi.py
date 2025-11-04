from naoqi import ALProxy

ip = "192.168.13.188"  # IP deines NAO oder Pepper
port = 9559

tts = ALProxy("ALTextToSpeech", ip, port)
tts.say("Hallo, ich bin NAO! Darf ich bitte eure Aufmerksamkeit haben")