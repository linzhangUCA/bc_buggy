import sys
import os
from datetime import datetime
import numpy as np
import pygame
from pygame.locals import *
from pygame import event, display, joystick
from adafruit_servokit import ServoKit
from gpiozero import PhaseEnableMotor
import cv2 as cv
import csv

from time import time


# SETUP
# init engine and steering wheel
engine = PhaseEnableMotor(phase=19, enable=26)
kit = ServoKit(channels=16, address=0x40)
steer = kit.servo[0]
MAX_THROTTLE = 0.32
STEER_CENTER = 95.5
MAX_STEER = 60

engine.stop()
steer.angle = STEER_CENTER
# init jotstick controller
display.init()
joystick.init()
print(f"{joystick.get_count()} joystick connected")
js = joystick.Joystick(0)
# init camera
cv.startWindowThread()
cam = cv.VideoCapture(0)
cam.set(cv.CAP_PROP_FPS, 20)
for i in reversed(range(60)):  # warm up camera
    if not (i+1) % 20:
        print(int((i + 1) / 20))
    ret, frame = cam.read()
# create data storage
image_dir = os.path.join(sys.path[0], 'data/', datetime.now().strftime("%Y%m%d%H%M"), 'images/')
if not os.path.exists(image_dir):
    try:
        os.makedirs(image_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
label_path = os.path.join(os.path.dirname(os.path.dirname(image_dir)), 'labels.csv')
# init vars
vel, ang = 0., 0.
action = []
frame_count = 0
is_recording = False


# MAIN
try:
    while True:
        ret, frame = cam.read()
        if ret:  # check camera
            frame_count += 1
        else:
            print("No image received!")
            engine.stop()
            engine.close()
            cv.destroyAllWindows()
            pygame.quit()
            sys.exit()
        for e in event.get():
            if e.type == QUIT:
                print("QUIT detected, terminating...")
                engine.stop()
                engine.close()
                cv.destroyAllWindows()
                pygame.quit()
                sys.exit()
            if e.type == JOYAXISMOTION:
                ax0_val = js.get_axis(0)
                ax4_val = js.get_axis(4)
                vel = -np.clip(ax4_val, -MAX_THROTTLE, MAX_THROTTLE)
                if vel > 0:  # drive motor
                    engine.forward(vel)
                elif vel < 0:
                    engine.backward(-vel)
                else:
                    engine.stop()
                ang = STEER_CENTER - MAX_STEER * ax0_val
                steer.angle = ang  # drive servo
                action = [ax0_val, ax4_val]  # steer, throttle
                print(f"engine speed: {vel}, steering angle: {ang}")
            elif e.type == JOYBUTTONDOWN:
                if js.get_button(0):
                    is_recording = not is_recording
                    print(f"is recording? {is_recording}")
        if is_recording:
            image = cv.resize(frame, (120, 160))
            cv.imwrite(image_dir + str(frame_count)+'.jpg', image)  # save image
            label = [str(frame_count)+'.jpg'] + action
            with open(label_path, 'a+', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(label)  # save labels
        if cv.waitKey(1) == ord('q'):
            engine.stop()
            engine.close()
            cv.destroyAllWindows()
            pygame.quit()
            sys.exit()

except KeyboardInterrupt:
    engine.stop()
    engine.close()
    cv.destroyAllWindows()
    pygame.quit()
    sys.exit()
