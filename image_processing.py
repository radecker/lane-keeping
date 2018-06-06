import time
import cv2
import math
import numpy as np
import serial
from matplotlib import pyplot as plt

cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'DVIX')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
ser = serial.Serial('COM8', 9600)
time.sleep(2)


#turn_left(18)


# def turn_right(dist_from_line):
#     miss_dist = abs(dist_from_line - 24.0)
#     miss_deg = math.degrees(math.atan(miss_dist / 120.0))
#     correction_steps = (miss_deg / 20.0)
#     correction_steps = float('%.2f'%(correction_steps))
#     correction_steps *= 100
#     correction_steps = '%.0f' % (correction_steps)
#     ser.write(b"R" + str(correction_steps))

MAGNITUDE = 0
DIRECTION = 1
MAG_0 = 0
MAG_1 = 1
MAG_2 = 2
MAG_3 = 3
MAG_4 = 4
LEFT = 0
RIGHT = 1
current_state = [MAG_0, CENTER]
prev_state = current_state

def state_machine(error, dir):
    if error < 2:
        prev_state = current_state
        current_state = [MAG_0, dir]
    if error >= 2 and error < 6:
        prev_state = current_state
        current_state = [MAG_1, dir]
    if error >= 6:
        prev_state = current_state
        current_state = [MAG_2, dir]

    if current_state != prev_state:
        turn_amount = abs(current_state[MAGNITUDE] - prev_state[MAGNITUDE])
        turn_dir = abs(current_state[DIRECTION] - prev_state[DIRECTION])


def turn_wheel(steps, dir):
    miss_dist = abs(dist_from_line - 22.0)
    miss_deg = math.degrees(math.atan(miss_dist / 120.0))
    correction_steps = (miss_deg / 20.0)
    correction_steps = float('%.2f'%(correction_steps))
    correction_steps *= 100
    correction_steps = '%.0f' % (correction_steps)
    if dir == LEFT:
        ser.write(b"L" + str(correction_steps))
    if dir == RIGHT:
        ser.write(b"R" + str(correction_steps))



CAR_WIDTH_CORRECTION = 3*12         # Half width of car in inches
CORRECTION_FACTOR = 0.2897          # Constant to convert pixels to inches at 10 ft distance
TARGET_DIST_PX = 140                # Target distance ahead of vehicle in pixels

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

        if dist_from_line:
            if dist_from_line > 24:
                print "GO RIGHT"
                turn_right(dist_from_line)
            elif dist_from_line < 20:
                print "GO LEFT"
                turn_left(dist_from_line)
            else:
                print "YOU GOOD BOYE"

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
