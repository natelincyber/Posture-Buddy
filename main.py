from flask import Flask
from flask import render_template
from flask import Response

import poseModule

app = Flask(__name__)

detector = poseModule.poseDetector()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/demo')
def demo():
    detector.setarmsCounter(0)
    detector.setlegsCounter(0)
    detector.setswayCounter(0)
    detector.sethandsCounter(0)
    detector.setfidgetCounter(0)
    return render_template('demo.html')


@app.route('/results')
def results():
    armscounter = int(detector.getarmsCounter())
    legscounter = int(detector.getlegsCounter())
    swaycounter = int(detector.getswayCounter())
    armsdowncounter = int(detector.gethandsCounter())
    fidgetcounter = int(detector.getfidgetCounter())
    return render_template('results.html', armscounter=armscounter, legscounter=legscounter, 
                            swaycounter=swaycounter, armsdowncounter=armsdowncounter, 
                            fidgetcounter=fidgetcounter)


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/video_feed')
def video_feed():
    return Response(poseModule.main(detector), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    # host
    app.run(host='127.0.0.1', debug=True, port=5000)
