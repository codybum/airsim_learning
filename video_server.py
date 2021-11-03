from flask import Flask, render_template_string, Response

import airsim
import cv2
import numpy as np
import argparse 

parser = argparse.ArgumentParser(description='AirSim Video Server')
parser.add_argument('--vid', type=str, default="NONE")
parser.add_argument('--cid', type=str, default="NONE")
parser.add_argument('--ip', type=str, default="127.0.0.1")
args = parser.parse_args()


client = airsim.MultirotorClient(args.ip)
client.confirmConnection()

CAMERA_NAME = args.cid
IMAGE_TYPE = airsim.ImageType.Scene
DECODE_EXTENSION = '.jpg'

def frame_generator():
    #request = airsim.ImageRequest("cam", airsim.ImageType.Scene, False, False) # types are in airsim/types.py
    while (True):
        #response_image = client.simGetImage(CAMERA_NAME, IMAGE_TYPE,vehicle_name=args.cid)
        response_image = client.simGetImage(CAMERA_NAME, IMAGE_TYPE)
        #response_image = client.simGetImage(request)
        np_response_image = np.asarray(bytearray(response_image), dtype="uint8")
        decoded_frame = cv2.imdecode(np_response_image, cv2.IMREAD_COLOR)
        ret, encoded_jpeg = cv2.imencode(DECODE_EXTENSION, decoded_frame)
        frame = encoded_jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(
        """
            <html>
            <head>
                <title>AirSim Streamer</title>
            </head>
            <body>
                <h1>AirSim Streamer</h1>
                <hr />
                Please use the following link: <a href="/video_feed">http://10.33.31.21:5000/video_feed</a>
            </body>
            </html>
        """
        )

@app.route('/video_feed')
def video_feed():
    return Response(
            frame_generator(),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)

