import socket
import numpy as np
import matplotlib.pyplot as plt

def checkCamerasStarted(isRS, isZed):
    if not isRS:
        while True:
            resp = input('The RealSense camera was not opened. Continue? (y/n)')
            if resp.lower()=='n':
                print('Exiting')
                return False
            elif resp.lower()=='y':
                break

    if not isZed:
        while True:
            resp = input('The ZED camera was not opened. Continue? (y/n)')
            if resp.lower()=='n':
                print('Exiting')
                return False
            elif resp.lower()=='y':
                break
    return True

def startCameras():
    cameras = {}
    startedQ = {}
    try:
        from realSense import RealSense2
        rsCam = RealSense2()
        rsCam.takePicture()
        isRS = True
        cameras['RS'] = rsCam
        startedQ['RS'] = isRS
    except:
        isRS = False
        print('Realsense Camera could not be opened!')

    try:
        from ZED import ZEDCamera
        zedCam = ZEDCamera()
        zedCam.startStream()
        isZed=True
        cameras['ZED'] = zedCam
        startedQ['ZED'] = isZed
    except:
        isZed=False
        print('ZED Camera could not be opened!')

    if not checkCamerasStarted(isRS, isZed):
        exit()

    return cameras, startedQ

def setUpSocket(address):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    return sock

def pictureLoop(fname, client, cameras, startedQ, axes):
    for key in startedQ:
        if startedQ[key]:
            album = cameras[key].takePicture()
            np.save('{}_{}_depth.npy'.format(fname,key), album.depth)
            np.save('{}_{}_color.npy'.format(fname,key), album.color)
            if key=='RS':
                axes[0].imshow(album.color)
            elif key=='ZED':
                axes[1].imshow(album.color[:,:1280,(2,1,0)])
            plt.pause(0.05)
    print('OK')

def main(address):
    cameras, startedQ = startCameras()

    sock = setUpSocket(address)
    print('Ready for Connections')

    try:
        plt.ion()
        fig = plt.figure(figsize=(16,9))
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        while True:
            client, addr = sock.accept()
            print('Connection', addr)
            exitFlag = False
            while True:
                req = client.recv(4096)
                if not req:
                    continue
                command = req.decode('ascii').split(' ')
                verb = command[0]
                if verb=='pic':
                    fname = command[1][:-1]
                    pictureLoop(fname, client, cameras, startedQ, [ax1,ax2])
                elif verb=='off':
                    pass
                elif verb=='on':
                    pass
                else:
                    print('ERROR: {} is not a proper command'.format(verb))
    finally:
        print('Closing Cameras')
        for key in startedQ:
            cameras[key].closeStream()
    return

if __name__ == '__main__':
    main(('', 25000))
