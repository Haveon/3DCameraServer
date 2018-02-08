import socket
from realSense import RealSense2
import numpy as np

rsCam = RealSense2()
rsCam.startStream()

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
                album = rsCam.takePicture()
                fname = command[4:-1]
                np.save(fname+'_depth.npy', album.depth)
                np.save(fname+'_color.npy', album.color)
            else:
                print('ERROR: improper command!')

server(('', 25000))
