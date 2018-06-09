#
#
#      _______________________________________________________________
#     |         ___                   ___          __                 |
#     |        / _ \__ _____ ____    / _ \___ ____/ /_____ ____       |
#     |       / , _/ // / _ `/ _ \  / // / -_) __/  '_/ -_) __/       |
#     |      /_/|_|\_, /\_,_/_//_/ /____/\__/\__/_/\_\\__/_/          |
#     |           /___/                                               |
#     |_______________________________________________________________|
#
#
#

import time
import cv2
import csv
import math
import numpy as np
import serial
# from matplotlib import pyplot as plt

STEPPER_MOTOR_STEPS = 20
MOTOR_DELAY = 0.50

LEFT = 0
RIGHT = 1

HARD_LEFT =     0
SOFT_LEFT =     1
CENTER =        2
SOFT_RIGHT =    3
HARD_RIGHT =    4

def state_control(error, dir, current_state, prev_state, file):
    if error < 3:
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
    # print([current_state, prev_state])
    file.write(str(current_state*10) + ',' + str(prev_state*10) + "\n")
    prev_state = current_state
    return [current_state, prev_state]


def turn_wheel(steps, dir):
    correction_steps = STEPPER_MOTOR_STEPS * steps
    correction_steps = float('%.2f'%(correction_steps))
    correction_steps = '%.0f' % (correction_steps)
    if dir == LEFT:
        print("L" + str(correction_steps))
        # ser.write(b"L" + str(correction_steps).encode())
    if dir == RIGHT:
        print("R" + str(correction_steps))
        # ser.write(b"R" + str(correction_steps).encode())


CAR_WIDTH_CORRECTION = 3*12         # Half width of car in inches
CORRECTION_FACTOR = 0.2522          # Constant to convert pixels to inches at 10 ft distance
TARGET_DIST_PX = 140                # Target distance ahead of vehicle in pixels
# going at 15 feet distance
TARGET_DIST_SUB = 22.0
BS_FACTOR = 1.6514

filename = "faux_data.csv"
file = open(filename, 'r')
distances = file.readlines()
file.close()

filename = "output.csv"
file = open(filename, 'w')

state = state_control(0, LEFT, CENTER, CENTER, file)
for distance in distances:
    dist_from_line = float(distance[:len(distance) - 2])
    if dist_from_line:
        # print(dist_from_line)
        if dist_from_line > 25:
            print("GO RIGHT")
            miss_dist = abs(dist_from_line - TARGET_DIST_SUB)
            state = state_control(miss_dist, RIGHT, state[0], state[1], file)
        elif dist_from_line < 19:
            miss_dist = abs(dist_from_line - TARGET_DIST_SUB)
            print("GO LEFT")
            state = state_control(miss_dist, LEFT, state[0], state[1], file)
        else:
            miss_dist = abs(dist_from_line - TARGET_DIST_SUB)
            print("YOU GOOD BOYE")
            state = state_control(miss_dist, RIGHT, state[0], state[1], file)

file.close()