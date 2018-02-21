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

def pictureLoop(client, cameras, startedQ, fig):
    req = client.recv(4096)
    if not req:
        return True
    # Parse command here
    command = req.decode('ascii')
    if command[:3]=='pic':
        fname = command[4:-1]
        for key in startedQ:
            if startedQ[key]:
                album = cameras[key].takePicture()
                np.save('{}_{}_depth.npy'.format(fname,key), album.depth)
                np.save('{}_{}_color.npy'.format(fname,key), album.color)
                fig[0 if key=='RS' else 1].imshow(album.color)#ax = fig.subplot(211 if key=='RS' else 212)
                ax.imshow(album.color)
                #plt.show()
        print('OK')
    else:
        print('ERROR: improper command!')
    return False

def main(address):
    cameras, startedQ = startCameras()

    sock = setUpSocket(address)
    print('Ready for Connections')

    try:
        plt.ion()
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        while True:
            client, addr = sock.accept()
            print('Connection', addr)
            pictureTakenQ = False
            while not pictureTakenQ:
                pictureTakenQ = pictureLoop(client, cameras, startedQ, [ax1,ax2])
    finally:
        print('Closing Cameras')
        for key in startedQ:
            cameras[key].closeStream()
    return

if __name__ == '__main__':
    main(('', 25000))
