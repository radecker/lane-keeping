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
import math
import numpy as np
import serial
# from matplotlib import pyplot as plt

cap = cv2.VideoCapture(1)
fourcc = cv2.VideoWriter_fourcc(*'DVIX')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
ser = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2)

STEPPER_MOTOR_STEPS = 20
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
    # print([current_state, prev_state])
    prev_state = current_state
    return [current_state, prev_state]


def turn_wheel(steps, dir):
    correction_steps = STEPPER_MOTOR_STEPS * steps
    correction_steps = float('%.2f'%(correction_steps))
    correction_steps = '%.0f' % (correction_steps)
    if dir == LEFT:
        # print("L" + str(correction_steps))
        ser.write(b"L" + str(correction_steps).encode())
    if dir == RIGHT:
        # print("R" + str(correction_steps))
        ser.write(b"R" + str(correction_steps).encode())



CAR_WIDTH_CORRECTION = 3*12         # Half width of car in inches
CORRECTION_FACTOR = 0.2522          # Constant to convert pixels to inches at 10 ft distance
TARGET_DIST_PX = 140                # Target distance ahead of vehicle in pixels
# going at 15 feet distance
TARGET_DIST_SUB = 24.0
BS_FACTOR = 1.6514
state = state_control(0, LEFT, CENTER, CENTER)

prev_dist = 0
prev_dist_2 = 0
count = 0
while(True):
    ret, frame = cap.read()
    if ret == True:

        # start_time = time.time()

        # img = cv2.resize(src, (400,400))
        # plt.imshow(img)

        img = frame
        #img = cv2.imread("road_test.jpg")
        img = img[240:440, 320:]         # Full normal size is (480,640)
        # img = img[135:320, 320:]
        # print img.shape  #(height, width, channels)
        edges = cv2.Canny(img,100,175)

        end_points = []
        point_averages = []
        lines = cv2.HoughLines(edges,1,np.pi/180,75)
        if lines is not None:
            for line in lines:
                rho, theta = line[0]
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a*rho
                y0 = b*rho
                x1 = int(x0 + 1000*(-b))
                y1 = int(y0 + 1000*(a))
                x2 = int(x0 - 1000*(-b))
                y2 = int(y0 - 1000*(a))

                rise = y2 - y1
                #print "rise " + str(rise)
                run = (x2 - x1) + 1    # +1 to handle divide by zero case
                #print "run " + str(run)
                slope = abs(float(float(rise)/run))
                if slope > .5:
                    list.append(end_points, (x1,x2,y1,y2))
                    #cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        #print end_points
        for i in range(0,4):
            temp = []
            for point_set in end_points:
                list.append(temp, point_set[i])
            if len(end_points) != 0:
                list.append(point_averages, sum(temp)/len(end_points))

        if len(end_points) != 0:
            cv2.line(img, (point_averages[0], point_averages[2]), (point_averages[1], point_averages[3]), (0, 0, 255), 2)
        dist_from_line = 0
        for i in range(0, len(img[TARGET_DIST_PX])):
            if img[TARGET_DIST_PX,i][0] == 0 and img[TARGET_DIST_PX,i][1] == 0 and img[TARGET_DIST_PX, i][2] == 255:
                dist_from_line = i*CORRECTION_FACTOR - CAR_WIDTH_CORRECTION
                break

        dist_from_line = dist_from_line * BS_FACTOR
        if count > 1:
            dist_from_line = (dist_from_line + prev_dist + prev_dist_2)/3
        prev_dist_2 = prev_dist
        prev_dist = dist_from_line
        if count < 10:
            count = count + 1

        if dist_from_line:
            # print(dist_from_line)
            if dist_from_line > 25:
                print("GO RIGHT")
                miss_dist = abs(dist_from_line - TARGET_DIST_SUB)
                state = state_control(miss_dist, RIGHT, state[0], state[1])
            elif dist_from_line < 19:
                miss_dist = abs(dist_from_line - TARGET_DIST_SUB)
                print("GO LEFT")
                state = state_control(miss_dist, LEFT, state[0], state[1])
            else:
                miss_dist = abs(dist_from_line - TARGET_DIST_SUB)
                print("YOU GOOD BOYE")
                state = state_control(miss_dist, LEFT, state[0], state[1])      # Passing left because it is ignored for center

        cv2.imwrite('hough_lines.jpg',img)
        # print time.time() - start_time, "Seconds"
        #out.write(img)

        cv2.imshow('frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # print img[140, :]
            # print len(img[140])
            ser.close()
            break
    else:
        break

cap.release()
out.release()
cv2.destroyAllWindows()
