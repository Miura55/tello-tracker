# simple example demonstrating how to control a Tello using your keyboard.
# For a more fully featured example see manual-control-pygame.py
# 
# Use W, A, S, D for moving, E, Q for rotating and R, F for going up and down.
# When starting the script the Tello will takeoff, pressing ESC makes it land
#  and the script exit.

import numpy as np
import cv2
import os
import math
import time
import socket
import subprocess
from datetime import datetime

os.makedirs('./imgs', exist_ok=True)

TELLO_IP = '192.168.10.1'
CMD_PORT = 8889
VIDEO_PORT = 11111

FRAME_WIDTH = 960
FRAME_HEIGHT = 720

class Tello:
    def __init__(self):
        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cmd_sock.bind(('', CMD_PORT))
        self.tello_addr = (TELLO_IP, CMD_PORT)

    def send(self, cmd):
        print(f'>> {cmd}')
        self.cmd_sock.sendto(cmd.encode(), self.tello_addr)


tello = Tello()

time.sleep(1)
tello.send('command')
time.sleep(1)
tello.send('streamon')

# start ffmpeg
cmd = [
    'ffmpeg',
    '-loglevel', 'quiet',
    '-i', f'udp://0.0.0.0:{VIDEO_PORT}',
    '-pix_fmt', 'bgr24',
    '-vcodec', 'rawvideo',
    '-an',
    '-sn',
    '-f', 'rawvideo',
    '-'
]

pipe = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    bufsize=10**8
)

frame_size = FRAME_WIDTH * FRAME_HEIGHT * 3


while True:
    # In reality you want to display frames in a seperate thread. Otherwise
    #  they will freeze while the drone moves.
    raw = pipe.stdout.read(frame_size)
    if len(raw) != frame_size:
        print('No img')
        continue

    img_array = np.frombuffer(raw, dtype=np.uint8)
    img = img_array.reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))
    cv2.imshow("drone", img)

    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC
        tello.send('land')
        break
    elif key == ord('p'):
        dt = datetime.now()
        file_name = "{}.png".format(dt.strftime('%Y%m%d%H%M'))
        cv2.imwrite('./imgs/{}'.format(file_name), img)
    elif key == ord('t'):
        tello.send('takeoff')
    elif key == ord('l'):
        tello.send('land')
    elif key == ord('w'):
        tello.send('forward 20')
    elif key == ord('s'):
        tello.send('back 20')
    elif key == ord('d'):
        tello.send('right 20')
    elif key == ord('a'):
        tello.send('left 20')
    elif key == ord('f'):
        tello.send('flip f')
    elif key == ord('v'):
        tello.send('flip b')
    elif key == ord('j'):
        tello.send('cw 45')
    elif key == ord('h'):
        tello.send('ccw 45')

