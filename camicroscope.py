from flask import jsonify, Flask, send_file, render_template, redirect, request
import pandas as pd
from flask_cors import CORS, cross_origin
import csv, json
from json import JSONEncoder
from pathlib import PurePath, Path
import os
import numpy as np
from PIL import Image
from cv2 import imread


app = Flask(__name__)
app.config["DEBUG"] = True
path = Path('./images')

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config["IMAGE_UPLOADS"] = path

#CORS Headers 
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def get_hello():
    return "Hello world"

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        if request.files:
            image=request.files["image"]
            image.save(str(path/image.filename))
            full_filename = os.path.join(app.config['IMAGE_UPLOADS'], image.filename)
            img = imread(full_filename)
            # get the shape of the image 
            row, col, plane = img.shape
            # create arrays of zeros with the same as the image 
            red = np.zeros((row,col,plane), np.uint8)
            green = np.zeros((row,col,plane), np.uint8)
            blue = np.zeros((row,col,plane), np.uint8)
            # extract the blue, green and red channels of the image
            blue[:,:,0]=img[:,:,0]
            green[:,:,1]=img[:,:,1]
            red[:,:,2]=img[:,:,2]
            # create dictionaries for the various channels type
            blue_channel = {'blue':blue}
            red_channel = {'red':red}
            green_channel = {'green':green}
            # construct the image from its red, green and blue channel components
            image_reconstruct = Image.fromarray(img)
            # save the reconstructed image
            image_reconstruct.save(os.path.join(app.config['IMAGE_UPLOADS'],"reconstruct.png"))
            # return json.dumps([red_channel, green_channel, blue_channel], cls=NumpyArrayEncoder)
            # return the reconstructed image to the user
            return send_file(os.path.join(app.config['IMAGE_UPLOADS'],"reconstruct.png"),mimetype='image/png')
    return render_template('upload_image.html')  

#app.run()


