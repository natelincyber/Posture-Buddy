from flask import Flask
from flask import render_template
from flask import Response

import cv2
import time
import mediapipe as mp


class poseDetector():

    def __init__(self, mode=False, upBody=False, smooth=True, detectionConf=0.5, trackConf=0.5):
        self.mode = mode
        self.upBody = upBody
        self.smooth = smooth
        self.detectionConf = detectionConf
        self.trackConf = trackConf

        self.mpDraw = mp.solutions.drawing_utils
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(
            self.mode, self.upBody, self.smooth, self.detectionConf, self.trackConf)

        self.armscounter = 0
        self.legscounter = 0
        self.swaycounter = 0
        self.armsDownCounter = 0

    # finds pose and draws over it
    def findPose(self, frame, draw=True):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(imgRGB)

        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(
                frame, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return frame

    def getPosition(self, frame, draw=True):

        lmList = []

        if self.results.pose_landmarks:

            for id, landmark in enumerate(self.results.pose_landmarks.landmark):

                h, w, c = frame.shape

                cx, cy = int(landmark.x * w), int(landmark.y * h)
                lmList.append([id, cx, cy])

                if draw:
                    cv2.circle(frame, (cx, cy), 3, (255, 0, 0), cv2.FILLED)
                    cv2.putText(frame, str(id), (cx, cy),
                                cv2.FONT_HERSHEY_PLAIN, 1, (155, 50, 23), 1)
        return lmList

    def refPos():
        pass

    def getarmsCounter(self):
        return self.armscounter/30

    def setarmsCounter(self, val):
        self.armscounter = val

    def getlegsCounter(self):
        return self.legsCounter/30

    def setlegsCounter(self, val):
        self.legsCounter = val

    def getswayCounter(self):
        return self.swaycounter/30

    def setswayCounter(self, val):
        self.swaycounter = val
    
    def gethandsCounter(self):
        return self.armsDownCounter/30

    def sethandsCounter(self, val):
        self.armsDownCounter = val

    def detectCrossedArms(self, lmlist):
        #left_wrist = 15
        #right_wrist = 16
        '''
            1. if left on right AND right on left
            2. counter ++
            3. return counter
        '''
        try:

            left_wristx = lmlist[15][1]
            # left_wristy = lmlist[15][2]

            right_wristx = lmlist[16][1]
            # right_wristy = lmlist[16][2]

            centerBodyLine = (
                (lmlist[11][1] - lmlist[12][1])/2) + lmlist[12][1]

        except IndexError:

            return

        if left_wristx < centerBodyLine and right_wristx > centerBodyLine:
            self.armscounter += 1

        return self.armscounter

    def detectCrossedLegs(self, lmlist):
        try:

            left_anklex = lmlist[27][1]
            right_anklex = lmlist[28][1]

        except IndexError:
            return

        if left_anklex < right_anklex or right_anklex > left_anklex:
            self.legsCounter += 1

        return self.legsCounter

    def detectSway(self, lmlist, lhold, rhold):

        left_shoulderx = lmlist[11][1]
        right_shoulderx = lmlist[12][1]

        rhold = right_shoulderx
        lhold = left_shoulderx
    
    def detectArmsDown(self, lmlist):

        left_index = lmlist[19][2]
        right_index = lmlist[20][2]

        hip_line = lmlist[24][2]

        if left_index > hip_line and right_index > hip_line:
            self.armsDownCounter += 1

        


def main(detector):

    cap = cv2.VideoCapture(1)
    previousTime = 0

    while True:

        _, frame = cap.read()

        frame = detector.findPose(frame)
        lmList = detector.getPosition(frame)
        detector.detectCrossedArms(lmList)
        detector.detectCrossedLegs(lmList)
        detector.detectArmsDown(lmList)

        # calculate FPS
        currentTime = time.time()
        fps = 1/(currentTime - previousTime)
        previousTime = currentTime
        cv2.putText(frame, str(int(fps)), (20, 40),
                    cv2.FONT_HERSHEY_PLAIN, 2, (155, 50, 23), 1)

        if _:
            frame = cv2.imencode('.jpg', frame)[1].tobytes()
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


app = Flask(__name__)

detector = poseDetector()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/demo')
def tryitout():
    detector.setarmsCounter(0)
    detector.setlegsCounter(0)
    detector.setswayCounter(0)
    detector.sethandsCounter(0)
    return render_template('demo.html')


@app.route('/results')
def results():
    armscounter = int(detector.getarmsCounter())
    legscounter = int(detector.getlegsCounter())
    swaycounter = int(detector.getswayCounter())
    armsdowncounter = int(detector.gethandsCounter())



    return render_template('results.html', armscounter=armscounter, legscounter=legscounter, swaycounter=swaycounter, armsdowncounter=armsdowncounter)


@app.route('/video_feed')
def video_feed():
    return Response(main(detector), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5000)
