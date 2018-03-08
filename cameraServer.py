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

def pictureLoop(command, cameras, startedQ, axes, fig):
    verb = command[0]
    for key in startedQ:
        if startedQ[key]:
            if verb=='pic':
                picVerb(command[1], cameras, axes, key)
            elif verb=='on':
                onVerb(cameras, axes, key, fig)
            elif verb=='off':
                offVerb(command[1], cameras, axes, key, fig)
            else:
                print('ERROR: {} is not a proper command'.format(verb))
    plt.pause(0.05)

def offVerb(fname, cameras, axes, key, fig):
    if key=='RS':
        takePicture(cameras[key], fname, key, axes[0], emptyBuffer=False)
        cameras[key].closeStream()
    elif key=='ZED':
        takePicture(cameras[key], fname, key, axes[1], emptyBuffer=False)
    # GO
    fig.texts[0].set_visible(True)
    fig.texts[1].set_visible(False)
    return

def onVerb(cameras, axes, key, fig):
    if key=='RS':
        cameras[key].startStream()
    elif key=='ZED':
        pass
    # STOP
    fig.texts[0].set_visible(False)
    fig.texts[1].set_visible(True)
    return

def picVerb(fname, cameras, axes, key):
    if key=='RS':
        takePicture(cameras[key], fname, key, axes[0], emptyBuffer=True)
    elif key=='ZED':
        takePicture(cameras[key], fname, key, axes[1], emptyBuffer=True)
    return

def takePicture(camera, fname, cameraName, axes, emptyBuffer=False):
    album = camera.takePicture(emptyBuffer)
    np.save('{}_{}_depth.npy'.format(fname,cameraName), album.depth)
    np.save('{}_{}_color.npy'.format(fname,cameraName), album.color)
    img = album.color if cameraName=='RS' else album.color[:,:1280,(2,1,0)]
    axes.imshow(img)

def main(address):
    cameras, startedQ = startCameras()

    sock = setUpSocket(address)
    print('Ready for Connections')

    try:
        plt.ion()
        fig = plt.figure(figsize=(16,9))
        fig.text(0.7, 0.6, ' GO ', color='green', fontsize=120)
        fig.text(0.7, 0.6, 'STOP', color='red', fontsize=120)
        axes = [fig.add_subplot(211), fig.add_subplot(212)]
        while True:
            client, addr = sock.accept()
            print('Connection', addr)
            exitFlag = False
            while True:
                req = client.recv(4096)
                if not req:
                    continue
                command = req.decode('ascii')[:-1].split(' ')
                pictureLoop(command, cameras, startedQ, axes, fig)
    finally:
        print('Closing Cameras')
        for key in startedQ:
            cameras[key].closeStream()
    return

if __name__ == '__main__':
    main(('', 25000))
