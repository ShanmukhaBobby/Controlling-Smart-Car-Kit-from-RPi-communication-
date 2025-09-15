# 🚗 Smart Car Controlled by Raspberry Pi

Smart Car project using **Raspberry Pi + Arduino**. The Pi handles **face detection** and **hand gesture recognition** with OpenCV + Mediapipe, then sends commands over Serial to Arduino. Arduino controls the motors via L298N driver.

## Features
- Face detection → Only runs when face is detected  
- Hand gestures:  
  - 1 finger → Forward  
  - 2 fingers → Backward  
  - None/fist → Stop  
- Serial commands (`F`, `B`, `L`, `R`, `S`)  
- Arduino controls motors accordingly  

## Hardware
- Raspberry Pi  
- Arduino Uno/Nano  
- Motor driver (L298N / L293D)  
- Smart car chassis with DC motors  
- Camera (PiCam / IP cam)  

## Usage
1. Upload `sketch_sep15a.ino` to Arduino.  
2. Run `control.py` on Raspberry Pi:  
   ```bash
   python3 control.py
