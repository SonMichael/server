import os.path

from flask import Flask, jsonify
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename

from models.user import User
from services.user_service import UserService
from services.signature_service import SignatureService
from services import tensorflow_service

app = Flask(__name__)


@app.route('/')
def hello_world():
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


@app.route('/signature', methods=['GET', 'POST'])
def add_signature_to_user():
    user_service = UserService()
    users = user_service.get_all_users()

    if request.method == 'GET':
        return render_template('signature.html', users=users)

    file = request.files['file_upload']
    filename = file.filename
    if filename is None:
        return render_template('signature.html', users=users, has_error=True, error_message="File is empty")

    file_content = file.read()
    user_id = request.form['user_select']
    signature_service = SignatureService()
    signature_service.add_signature(user_id, file_content)

    return render_template('upload_success.html')

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    user_service = UserService()
    users = user_service.get_all_users()

    if request.method == 'GET':
        return render_template('predict.html', users=users)

    file = request.files['file_upload']
    filename = file.filename
    if filename is None:
        return render_template('predict.html', users=users, has_error=True, error_message="File is empty")

    file.save(f"./temp/{secure_filename(filename)}")
    test_image = os.path.join(os.getcwd(), 'temp/' + filename)

    user_id = request.form['user_select']
    signature_service = SignatureService()
    signatures = signature_service.get_by_user_id(user_id)
    genuine_images = [signature.path for signature in signatures]

    result = tensorflow_service.batch_predict(test_image, genuine_images)
    return render_template('predict.html', users=users, show_result=True, probability=str(round(result * 100, 2)))

if __name__ == 'app':
    app.run()
