import socket
from realSense import RealSense2
try:
    from ZED import ZEDCamera
    isZed=True
except:
    isZed=False
import numpy as np

rsCam = RealSense2()
rsCam.startStream()

if isZed:
    zedCam = ZEDCamera()
    zedCam.startStream()

def server(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    print('Ready for Connections')
    while True:
        client, addr = sock.accept()
        print('Connection', addr)
        while True:
            req = client.recv(4096)
            if not req:
                break
            # Parse command here
            command = req.decode('ascii')
            if command[:3]=='pic':
                rsAlbum = rsCam.takePicture()
                if isZed:
                    zedAlbum = zedCam.takePicture()
                fname = command[4:-1]
                np.save(fname+'_rs_depth.npy', rsAlbum.depth)
                np.save(fname+'_rs_color.npy', rsAlbum.color)
                if isZed:
                    np.save(fname+'_zed_depth.npy', zedAlbum.depth)
                    np.save(fname+'_zed_color.npy', zedAlbum.color)
            else:
                print('ERROR: improper command!')

server(('', 25000))
