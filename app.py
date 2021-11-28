import os.path

import numpy as np
from flask import Flask, jsonify
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename

from models.user import User
from models.signature import Signature
from services.user_service import UserService
from services.signature_service import SignatureService
from services import tensorflow_service

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/hello/', methods=['GET'])
@app.route('/hello/<name>', methods=['GET'])
def login(name):
    return render_template('hello.html', name=name)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file_upload']
        file.save(f"./temp/{secure_filename(file.filename)}")
        return render_template('upload_success.html')
    else:
        return render_template('upload.html')


@app.route("/me")
def me_api():
    return {
        "username": "dinh-tran",
        "age": 31,
    }


@app.route("/me2")
def me_api_2():
    user = User(name="dinh-tran", age=31)
    return jsonify(user.to_json())


@app.route("/user/<id>")
def get_user_by_id(id):
    user_service = UserService()
    user = user_service.get_user_by_id(id)
    return jsonify(user.to_json())

@app.route('/signature/<user_id>', methods=['GET'])
def get_signature_by_user_id(user_id):
    signature_service = SignatureService()
    signatures = signature_service.get_by_user_id(user_id)

    return jsonify([ signature.to_json() for signature in signatures ])

@app.route("/predict/<user_id>", methods=['GET', 'POST'])
def predict(user_id):
    if request.method == 'GET':
        return render_template('predict.html')

    file = request.files['file_upload']
    filename = file.filename
    if filename is None:
        return render_template('predict.html', has_error=True, error_message="File is empty")

    file.save(f"./temp/{secure_filename(filename)}")

    test_image = os.path.join(os.getcwd(), 'temp/' + filename)

    signature_service = SignatureService()
    signatures = signature_service.get_by_user_id(user_id)
    store_images = [signature.path for signature in signatures]

    result = []
    for stored_image in store_images:
        probability = tensorflow_service.predict((test_image, stored_image))
        result.append(probability)
    result = np.max(result)

    return render_template('predict.html', show_result=True, probability=str(round(result * 100, 2)))

if __name__ == 'app':
    app.run()
