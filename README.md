# WOTServer
A WIP server emulator for the mobile game "Futurama: Worlds of Tomorrow"

# !!This is NOT functional!!
# !!You can not play this game at this time!!

Most of this is likely going to change
There is a lot of debugging in this server code
Any help is appreciated, as you can tell I'm learning as I go!

To work on this:
(GETTING STARTED)
must begin by patching the APK with your localhost address
change ALL HTTPS requests to HTTP
rebuild, sign & install the APK
(Use Apktool)

connection values located at:
lib\armeabi-v7a\libclient.so (hexadecimal binary)

seemingly unnecessary (for this) server connection info located in
res\values\strings.xml

(TOOLS USED)
Android Device
Virtual Android (App)
Bluestacks Emulator
PCAP Droid
HTTP Toolkit
Wireshark
Android Platform Tools (ADB, Apksigner)
Unmodified Futurama APK
Unmodified Family Guy: The Quest for Stuff

You can now begin monitoring and responding to requests
