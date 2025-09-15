#!/usr/bin/env python3
import cv2
import os
import numpy as np
import serial
import time
import mediapipe as mp

# -----------------------------
# Setup
# -----------------------------
URL = "http://10.14.25.228:8080/video"  # Replace with your phone IP
cap = cv2.VideoCapture(URL, cv2.CAP_FFMPEG)

# Face Cascade
cascade_path = "./haarcascade_frontalface_default.xml"
if not os.path.exists(cascade_path):
    import urllib.request
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    urllib.request.urlretrieve(url, cascade_path)

face_cascade = cv2.CascadeClassifier(cascade_path)

# Serial setup (Arduino)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)  # allow Arduino reset

# Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

# -----------------------------
# Helpers: Hand gesture detector
# -----------------------------
def get_gesture(hand_landmarks):
    """
    Returns:
        1 -> one finger (index up)
        2 -> two fingers (index + middle up)
        0 -> none
    """
    finger_states = []

    # Landmarks (tip and pip positions)
    tips = [8, 12]  # index, middle finger tips
    pips = [6, 10]  # index, middle finger pip joints

    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            finger_states.append(1)  # finger up
        else:
            finger_states.append(0)  # finger down

    total_up = sum(finger_states)
    return total_up  # 0, 1, or 2

# -----------------------------
# Real-time loop
# -----------------------------
print("🔹 Starting Face + Hand Control...")
while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)  # mirror
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect face
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:  # if face present
        cv2.putText(frame, "Face detected!", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # Process hand
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = get_gesture(hand_landmarks)

                if gesture == 1:
                    ser.write(b'F')  # Forward
                    cv2.putText(frame, "Gesture: 1 (Forward)", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

                elif gesture == 2:
                    ser.write(b'B')  # Backward
                    cv2.putText(frame, "Gesture: 2 (Backward)", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                else:
                    ser.write(b'S')  # Stop
                    cv2.putText(frame, "Gesture: None (Stop)", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
        else:
            ser.write(b'S')  # No hand
            cv2.putText(frame, "No hand detected (Stop)", (10, 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255), 2)
    else:
        ser.write(b'S')  # No face
        cv2.putText(frame, "No face detected (Stop)", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

    # Show video
    cv2.imshow("Face + Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
