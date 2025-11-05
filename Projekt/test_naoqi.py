from naoqi import ALProxy

ip = "192.168.13.188"  # IP deines NAO oder Pepper
port = 9559


tts = ALProxy("ALTextToSpeech", ip, port)
audio_player = ALProxy("ALAudioPlayer", ip, port)
audio_device = ALProxy("ALAudioDevice", ip, port)
audio_device.setOutputVolume(100)
tts.say("Hallo, ich bin NAO! Darf ich bitte eure Aufmerksamkeit haben")