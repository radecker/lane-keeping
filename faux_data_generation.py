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

import imageio

print("Processing image...\n")

filename = "DriveMap.png"

image = imageio.imread(filename)
height, width = image.shape[:2]

distances = []
for j in range(0, height):
    for i in range(0, width):
        if image[j][i][2] != 255:
            distance = (width - i)*.261
            distances.append(distance)
            break

filename = "output.csv"
file = open(filename, 'w')
for distance in distances:
    file.write(str(distance) + "\n")

print("Done writing results to output.csv")