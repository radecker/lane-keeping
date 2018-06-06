import time
import cv2
import math
import numpy as np
import serial
from matplotlib import pyplot as plt

ser = serial.Serial('COM4', 9600)
time.sleep(2)

STEPPER_MOTOR_STEPS = 45
MOTOR_DELAY = 0.50

LEFT = 0
RIGHT = 1

HARD_LEFT =     0
SOFT_LEFT =     1
CENTER =        2
SOFT_RIGHT =    3
HARD_RIGHT =    4

def state_control(error, dir, current_state, prev_state):
    if error < 2:
        current_state = CENTER
    elif error < 6:
        if dir == LEFT:
            current_state = SOFT_LEFT
        if dir == RIGHT:
            current_state = SOFT_RIGHT
    else:
        if dir == LEFT:
            current_state = HARD_LEFT
        if dir == RIGHT:
            current_state = HARD_RIGHT
    if prev_state != current_state:
        if prev_state == CENTER:
            if current_state == SOFT_LEFT:
                turn_wheel(1, LEFT)
            if current_state == SOFT_RIGHT:
                turn_wheel(1, RIGHT)
            if current_state == HARD_LEFT:
                turn_wheel(2, LEFT)
            if current_state == HARD_RIGHT:
                turn_wheel(2, RIGHT)
        if prev_state == SOFT_LEFT:
            if current_state == CENTER:
                turn_wheel(1, RIGHT)
            if current_state == HARD_LEFT:
                turn_wheel(1, LEFT)
        if prev_state == HARD_LEFT:
            if current_state == CENTER:
                turn_wheel(2, RIGHT)
            if current_state == SOFT_LEFT:
                turn_wheel(1, RIGHT)
        if prev_state == SOFT_RIGHT:
            if current_state == CENTER:
                turn_wheel(1, LEFT)
            if current_state == HARD_RIGHT:
                turn_wheel(1, RIGHT)
        if prev_state == HARD_RIGHT:
            if current_state == CENTER:
                turn_wheel(2, LEFT)
            if current_state == SOFT_RIGHT:
                turn_wheel(1, LEFT)
    print([current_state, prev_state])
    prev_state = current_state
    return [current_state, prev_state]


def turn_wheel(steps, dir):
    correction_steps = STEPPER_MOTOR_STEPS * steps
    correction_steps = float('%.2f'%(correction_steps))
    correction_steps = '%.0f' % (correction_steps)
    print(correction_steps)
    if dir == LEFT:
        print("L" + str(correction_steps))
        ser.write(b"L" + str(correction_steps).encode())
    if dir == RIGHT:
        print("R" + str(correction_steps))
        ser.write(b"R" + str(correction_steps).encode())

print("STARTING RUN")
state = state_control(0, LEFT, CENTER, CENTER)
time.sleep(MOTOR_DELAY)
print("Completed 1")
state = state_control(3, LEFT, state[0], state[1])
time.sleep(MOTOR_DELAY)
print("Completed 2")
state = state_control(3, LEFT, state[0], state[1])
time.sleep(MOTOR_DELAY)
print("Completed 3")
state = state_control(7, LEFT, state[0], state[1])
time.sleep(MOTOR_DELAY)
print("Completed 4")
state = state_control(0, LEFT, state[0], state[1])
time.sleep(MOTOR_DELAY)
print("Completed 5")
state = state_control(7, RIGHT, state[0], state[1])
time.sleep(MOTOR_DELAY)
print("Completed 6")
print("ENDING RUN")
