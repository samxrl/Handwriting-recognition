from GCForest import gcForest
from keras.datasets import mnist
from sklearn.metrics import accuracy_score
from sklearn.externals import joblib
import numpy as np
import datetime

import urllib.request
from flask_cors import CORS
from flask import Flask, jsonify, render_template, request, render_template

print("加载模型...")
gcf = joblib.load('/mod/model.sav')
print("\n===========加载完成=============")


app = Flask(__name__, static_folder='./templates/static', template_folder="./templates")

@app.route('/', methods=['get'])
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['get', 'post'])
def anaylse():
    if request.method == 'POST':
        X_tests = request.form
        X_array = []
        for val in X_tests.values():
            test = val.split(',')
            X_array.append(test)

        pred_X = gcf.predict(X_array)

        return jsonify(data=pred_X.tolist())
    else:
        return 'GET'

@app.route('/bd', methods=['get', 'post'])
def bd():
    if request.method == 'POST':
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/handwriting?access_token=24.46fc0ccc8acd02979328312c87dfcf9b.2592000.1571703660.282335-17301475"
        data = {
            'image': request.form.get("image", ""),
            'words_type': 'number'
        }

        data = urllib.parse.urlencode(data).encode(encoding='UTF8')

        headers = {'content-type': 'application/x-www-form-urlencoded'}
        req = urllib.request.Request(url, data, headers)
        resp = urllib.request.urlopen(req)
        data = resp.read()
        print(data)

        return data
    else:
        return 'GET'

if __name__ == '__main__':
    app.debug = True
    CORS(app, supports_credentials=True)
    app.run(host='0.0.0.0', port=8000, use_reloader=False)
