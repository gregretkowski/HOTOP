import logging
import time
import yaml

import cv2
import numpy as np

#import pywin32
#print(cv2.__version__)

from win32gui import FindWindow, GetWindowRect

import win32api, win32con

config = {}
with open("config.yml", 'r') as stream:
    try:
        config=yaml.safe_load(stream)
        #print(parsed_yaml)
    except yaml.YAMLError as exc:
        print(exc)

if config['debug']:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

WRITE=False
READ=False
index = 0
arr = []
#window_name='frame'
#window_name='DCS'
'''
while True:
    cap = cv2.VideoCapture(index)
    try:
        if cap.getBackendName()=="MSMF":
            arr.append(index)
    except:
        break
    cap.release()
    index += 1

print(arr)
'''
if config['read_file']:
    vid = cv2.VideoCapture('debugging.mp4')

    #width = 1920
    #height = 1080
    #vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    #vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
else:
    vid = cv2.VideoCapture(1)
    frame_width = int(vid.get(3))
    frame_height = int(vid.get(4))

mywindow = None

if config['write_file'] and not config['read_file']:
    out = cv2.VideoWriter('debugging.mp4', cv2.VideoWriter_fourcc(*'XVID'), 24, (frame_width,frame_height))

framecounter = 0
lastframes=[0,0,0,0,0,0,0]
skips=0
leftclick_down = False
rightclick_down = False
while(True):

    # Capture the video frame
    # by frame

    if mywindow is None:

        window_handle = FindWindow(None, config['target_window'])
        if window_handle:
            mywindow = GetWindowRect(window_handle)
            logging.info('window found!!')

    def getxy(vidframe,circles,mywindow):
        # TODO: add config options here!
        percent_x = 1.0 * circles[0][0][0]  / vidframe.shape[1]
        percent_y = 1.0 * circles[0][0][1] / vidframe.shape[0]
        win_x_span = mywindow[2]-mywindow[0]
        win_y_span = mywindow[3]-mywindow[1]
        x = int(win_x_span*percent_x)+mywindow[0]
        y = int(win_y_span*percent_y)+mywindow[1]
        return x, y


    ret, frame = vid.read()

        # Display the resulting frame
    if config['write_file'] and not config['read_file']:
        out.write(frame)

    if config['camera_inverted']:
        frame = cv2.rotate(frame, cv2.ROTATE_180)


    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if config['binary_threshold']:
        _, grayFrame = cv2.threshold(grayFrame,127,255,cv2.THRESH_BINARY)
    #grayFrame = cv2.adaptiveThreshold(grayFrame,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
    #        cv2.THRESH_BINARY,11,2)

    '''

    image	8-bit, single-channel, grayscale input image.
    circles	Output vector of found circles. Each vector is encoded as 3 or 4 element floating-point vector (x,y,radius) or (x,y,radius,votes) .
    method	Detection method, see HoughModes. The available methods are HOUGH_GRADIENT and HOUGH_GRADIENT_ALT.
    dp	Inverse ratio of the accumulator resolution to the image resolution. For example, if dp=1 , the accumulator has the same resolution as the input image. If dp=2 , the accumulator has half as big width and height. For HOUGH_GRADIENT_ALT the recommended value is dp=1.5, unless some small very circles need to be detected.
    minDist	Minimum distance between the centers of the detected circles. If the parameter is too small, multiple neighbor circles may be falsely detected in addition to a true one. If it is too large, some circles may be missed.
    param1	First method-specific parameter. In case of HOUGH_GRADIENT and HOUGH_GRADIENT_ALT, it is the higher threshold of the two passed to the Canny edge detector (the lower one is twice smaller). Note that HOUGH_GRADIENT_ALT uses Scharr algorithm to compute image derivatives, so the threshold value shough normally be higher, such as 300 or normally exposed and contrasty images.
    param2	Second method-specific parameter. In case of HOUGH_GRADIENT, it is the accumulator threshold for the circle centers at the detection stage. The smaller it is, the more false circles may be detected. Circles, corresponding to the larger accumulator values, will be returned first. In the case of HOUGH_GRADIENT_ALT algorithm, this is the circle "perfectness" measure. The closer it to 1, the better shaped circles algorithm selects. In most cases 0.9 should be fine. If you want get better detection of small circles, you may decrease it to 0.85, 0.8 or even less. But then also try to limit the search range [minRadius, maxRadius] to avoid many false circles.
    minRadius	Minimum circle radius.
    maxRadius	Maximum circle radius. If <= 0, uses the maximum image dimension. If < 0, HOUGH_GRADIENT returns centers without finding the radius. HOUGH_GRADIENT_ALT always computes circle radiuses.
    '''
    #circles = cv2.HoughCircles(grayFrame, cv2.HOUGH_GRADIENT, 1, 100, param2=150, minRadius=3)
    #circles = cv2.HoughCircles(grayFrame, cv2.HOUGH_GRADIENT, 3, grayFrame.shape[0] / 5.)

    # PRETTY GOOD RESULTS HERE:
    #circles = cv2.HoughCircles(grayFrame,cv2.HOUGH_GRADIENT,dp=1,minDist=20,
    #                        param1=50,param2=30,minRadius=2,maxRadius=int(grayFrame.shape[0] / 20.))

    circles = cv2.HoughCircles(grayFrame,cv2.HOUGH_GRADIENT,
                                dp=config['hc_dp'],
                                minDist=config['hc_minDist'],
                                param1=config['hc_param1'],
                                param2=config['hc_param2'],
                                minRadius=config['hc_minRadius'],
                                maxRadius=int(grayFrame.shape[0] / config['hc_maxRadius_divisor'])
                            )


    # Contours.

    contours, _, = cv2.findContours(grayFrame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    for contour in contours:
        (x,y,w,h) = cv2.boundingRect(contour)
        if cv2.contourArea(contour) <300:
            continue
        detections.append([x,y,w,h])

    #dot_count = len(xcnts)
    if circles is None:
        dot_count = 0
    else:
        dot_count = len(circles[0,:])
    #dot_count = len(circles)
    lastframes.pop(0)
    lastframes.append(dot_count)
    if dot_count in [1,2,3]:
        #print(f"Dots X: {x} Y: {y} Count: {dot_count} Circles: {len(circles[0,:])} Skips: {skips}")
        #print(np.shape(circles))
        #print(f"Count - {dot_count}")
        logging.debug(f"Count - {dot_count} - First Circle Data - X:{1.0*circles[0][0][0]/grayFrame.shape[1]: .2f} Y:{1.0*circles[0][0][1]/grayFrame.shape[0]: .2f} Sz:{circles[0][0][2]}")
        avgframesfloat = sum(lastframes) / float(len(lastframes))
        avgframes = round(sum(lastframes) / float(len(lastframes)))
        logging.debug(f"Lastframes is {avgframesfloat} {avgframes}")
        logging.debug(f"Detections {len(detections)}")
        if avgframes == 1:
            #if framecounter % 10:
            if leftclick_down:
                leftclick_down = False
                logging.info("LEFTCLICK")
                if mywindow is not None and config['send_mouse_events']:
                    x, y = getxy(grayFrame,circles,mywindow)
                    win32api.SetCursorPos((x,y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

                    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE | win32con.MOUSEEVENTF_ABSOLUTE, int(x/SCREEN_WIDTH*65535.0), int(y/SCREEN_HEIGHT*65535.0))
            elif rightclick_down:
                rightclick_down = False
                logging.info("RIGHTCLICK")
                if mywindow is not None and config['send_mouse_events']:
                    x, y = getxy(grayFrame,circles,mywindow)
                    win32api.SetCursorPos((x,y))
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
                    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
            if framecounter % 100 == 0 or config['debug'] == True:
                logging.info(f"MOVE X:{1.0*circles[0][0][0]/grayFrame.shape[1]: .2f} Y:{1.0*circles[0][0][1]/grayFrame.shape[0]: .2f}")
            if mywindow is not None and config['send_mouse_events']:
                x, y = getxy(grayFrame,circles,mywindow)
                win32api.SetCursorPos((x,y))
        elif avgframes == 2 or avgframes == 3:
            if avgframes == 2:
                leftclick_down = True
                #logging.info("LEFTCLICK")
            elif avgframes == 3:
                rightclick_down = True
                leftclick_down = False
                #logging.info("RIGHTCLICK")

        skips=0
    else:
        skips += 1

    framecounter+=1
    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    #output = grayFrame.copy()
    output = cv2.cvtColor(grayFrame,cv2.COLOR_GRAY2RGB)
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        mycircles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in mycircles:
            # draw the circle in the output image, then draw a rectangle
            # corresponding to the center of the circle
            cv2.circle(output, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)


    cv2.imshow('frame', output)
    # OK we can findwindow!!







    # note hit 'q' over the video window!!!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if config['read_file'] and circles is not None:
        time.sleep(0.1)


# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
