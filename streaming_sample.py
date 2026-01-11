import socket
import subprocess
import numpy as np
import cv2
import threading
import time

TELLO_IP = '192.168.10.1'
CMD_PORT = 8889
VIDEO_PORT = 11111

FRAME_WIDTH = 960
FRAME_HEIGHT = 720

# --- Tello command sender ---
class Tello:
    def __init__(self):
        self.cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.cmd_sock.bind(('', CMD_PORT))
        self.tello_addr = (TELLO_IP, CMD_PORT)

    def send(self, cmd):
        print(f'>> {cmd}')
        self.cmd_sock.sendto(cmd.encode(), self.tello_addr)

# --- ffmpeg video reader ---
def video_stream():
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
        raw = pipe.stdout.read(frame_size)
        if len(raw) != frame_size:
            continue

        frame = np.frombuffer(raw, dtype=np.uint8)
        frame = frame.reshape((FRAME_HEIGHT, FRAME_WIDTH, 3))

        cv2.imshow('Tello Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    pipe.terminate()
    cv2.destroyAllWindows()

# --- main ---
if __name__ == '__main__':
    tello = Tello()

    time.sleep(1)
    tello.send('command')
    time.sleep(1)
    tello.send('streamon')

    video_stream()

