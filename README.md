# The Soupinator 510

Shenzhen, Fallout
IRL Hackathon Project

This project is an auto tracking turret featuring a laser. It uses four different servos in order to control the pitch and yaw of a 3D printed turret.

The reason this project was made is because THE WORLD IS ENDING!!!! and soup needs a way to annihilate his enemies and protect himself from the vicious beasts of an apocolyptic world. For this reason, we have created the SOUPINATOR 510, a havoc-wreaking turret that will mow down anyone in soup's path.

We built this using 3D modeled parts and by working around components not readily available. For example, we did not have a lazy susan, so we got around that by using herringbone gears with edge blocks to hold a large gear in place with two other gears, essentially making a floating gear.


<img width="2480" height="3508" alt="510 Turret Zine Final" src="https://github.com/user-attachments/assets/cbb6d690-3f55-4554-9415-def713bc1d50" />


### Disclaimer 

Although we wished to use the XIAO ESP32 Sense camera to track movement, due to a difference in available library version and the ESP32 version, we were forced to use a laptop camera

## Build Instructions

First, please make sure you have all the parts printed. They are made to look best in black.
You should have:
* Left Turret Sideplate
* Right Turret Sideplate
* Turret Head
* Base
* Central Gear
* Servo Gear (2)
* Legs (3)

Then, Please gather the following parts:
* MG90S (2)
* MG995 (2)
* Cross-shaped servo horn (2)
* Circular servo horn (2)
* XIAO ESP32 Sense (Optional)
* XIAO ESP32-C3
* Laser module
* Assorted screws, bolts, and washers (and heatset inserts if you want to be fancy!)

Take the MG90S servos and screw them in (wire first) into the rectangular cutouts on the Left and Right Turret Sideplates (The horn should be facing into the side with no lettering)

<img width="247" height="257" alt="image" src="https://github.com/user-attachments/assets/154846e6-ed9f-4894-a465-7ab21db4c6b8" />

Attach the cross shaped horn to the each side Turret head, then attach both of the Turret sides to that assembly using the servo horns.

Attach the laser to the bottom of the Turret head using zipties. Optionally attach the Sense to the extrusion on the side of the Turret head using screws.

<img width="248" height="244" alt="image" src="https://github.com/user-attachments/assets/1fde28cb-0af8-4d05-9682-ae65d74155d6" />

The top of the turret is complete.

For the bottom of the turret, attach the legs to the base using screws. Everything should line up. 

<img width="256" height="142" alt="image" src="https://github.com/user-attachments/assets/ab72f1f3-2e95-4a6c-8c33-557790b467d8" />

Then, slide the MG995 servos into the servo slots, and screw them in.

Take each smaller servo gear, and attach the circular servo horn on the underside, with side connecting to the servo on the bottom. Use screws.

Attach ONE of those small gears onto one of the MG995 servos. Then, align the Central Gear with that smaller gear, and roll it until you are able to attach the second smaller gear.

<img width="348" height="230" alt="image" src="https://github.com/user-attachments/assets/096991de-fa72-4afe-a455-b2ad912a7a8c" />

The bottom part of the turret is complete!

To attach them, screw the bottom of the Turret sidplates (there are holes) into the Central Gear. 

<img width="335" height="294" alt="image" src="https://github.com/user-attachments/assets/d4e20fac-d313-4566-ac4c-5a459bf41054" />

## Electrical

## Firmware
AI Tracking Turret

Face-tracking pan/tilt turret. Mac webcam does vision processing, XIAO ESP32-C3 drives servos + laser over USB serial.

Requirements


macOS, Windows, or Linux
Python 3.10+
Arduino IDE 2.0+
XIAO ESP32-C3
4x servo (2 pan, 2 tilt) + laser diode


1. Firmware setup (XIAO ESP32-C3)


Install Arduino IDE
Arduino IDE → Settings → Additional Boards Manager URLs:


   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json


Boards Manager → search esp32 → install latest (Espressif Systems)
Connect XIAO C3 via USB-C → select board XIAO_ESP32C3 and the matching port
Paste in the C3 firmware (c3.ino)
Verify it first, then Upload it
Open Serial Monitor at 115200 baud to confirm it's running


2. Host software setup (Python)

bashpython3 --version          # confirm Python 3.10+
pip3 install opencv-python mediapipe pyserial

Open the tracking script and set SERIAL_PORT to match your board:

macOS: /dev/cu.usbmodemXXXX
Windows: COM3 (or similar)


Get the exact value from Arduino IDE's port dropdown.

3. Running it

Confirm XIAO C3 is wired (servos/laser powered from power bank, common ground with C3 — see wiring diagram) and connected to your Mac via USB-C
Close Arduino Serial Monitor (it locks the port)
Run:

Paste in the python camera code (soupinator.py)

bash   python3 soupinator.py


A webcam window opens — step into frame, servos should track your face, laser lights up on lock


Troubleshooting


Port busy: lsof | grep usbmodem<port>, kill the PID holding it
No servo movement: confirm Serial Monitor is closed, check FRAME_W/FRAME_H in firmware match your webcam resolution
Wrong pan direction: check cv2.flip() mirroring matches your coordinate mapping
Gear strain: lower MAX_STEP in firmware to slow servo response
