import socket
import numpy as np

try:
    from realSense import RealSense2
    rsCam = RealSense2()
    rsCam.takePicture()
    isRS = True
except:
    isRS = False
    print('Realsense Camera could not be opened!')

try:
    from ZED import ZEDCamera
    zedCam = ZEDCamera()
    zedCam.startStream()
    isZed=True
except:
    isZed=False
    print('ZED Camera could not be opened!')

if not isRS:
    while True:
        resp = input('The RealSense camera was not opened. Continue? (y/n)')
        if resp.lower()=='n':
            print('Exiting')
            exit()
        elif resp.lower()=='y':
            break

if not isZed:
    while True:
        resp = input('The ZED camera was not opened. Continue? (y/n)')
        if resp.lower()=='n':
            print('Exiting')
            exit()
        elif resp.lower()=='y':
            break

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
                fname = command[4:-1]
                if isRS:
                    rsAlbum = rsCam.takePicture()
                    np.save(fname+'_rs_depth.npy', rsAlbum.depth)
                    np.save(fname+'_rs_color.npy', rsAlbum.color)
                if isZed:
                    zedAlbum = zedCam.takePicture()
                    np.save(fname+'_zed_depth.npy', zedAlbum.depth)
                    np.save(fname+'_zed_color.npy', zedAlbum.color)
            else:
                print('ERROR: improper command!')

server(('', 25000))
