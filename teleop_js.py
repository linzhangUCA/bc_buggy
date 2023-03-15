import sys
import numpy as np
import pygame
from pygame.locals import *
from pygame import event, display, joystick
from adafruit_servokit import ServoKit
from gpiozero import PhaseEnableMotor
import cv2 as cv


# SETUP
# init engine and steering wheel
engine = PhaseEnableMotor(phase=19, enable=26)
kit = ServoKit(channels=16, address=0x40)
steer = kit.servo[0]
THROTTLE = 0.25
STEER_CENTER = 87
MAX_STEER = 60
engine.stop()
steer.angle = STEER_CENTER
ang = STEER_CENTER  # init value
# init jotstick controller
display.init()
joystick.init()
print(f"{joystick.get_count()} joystick connected")
js = joystick.Joystick(0)
# init camera
cv.startWindowThread()
cam = cv.VideoCapture(0)
cam.set(cv.CAP_PROP_FPS, 20)


# MAIN
try:
    while True:
        ret, frame = cam.read()
        if not ret:  # check camera
            print("No image received!")
            engine.stop()
            engine.close()
            cv.destroyAllWindows()
            pygame.quit()
            sys.exit()
        # throttle
        engine.forward(THROTTLE)
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
                # steer
                ang = STEER_CENTER - MAX_STEER * ax0_val
                steer.angle = ang  # drive servo
                action = (ax0_val)  # steer, throttle
                print(f"steering axis: {ax0_val}")
        print(f"engine speed: {THROTTLE}, steering angle: {ang}")
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
