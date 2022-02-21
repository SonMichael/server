import os.path

from flask import Flask, jsonify
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename

from models.user import User
from services.staff_service import StaffService
from services.user_service import UserService
from services.signature_service import SignatureService, save_signature_request_image
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


@app.route("/api/users", methods=['GET'])
def get_all_users():
    user_service = UserService()
    users = user_service.get_all_users()

    return jsonify([user.to_json() for user in users])


@app.route("/api/login", methods=['POST'])
def login_api():
    username = request.form['username']
    password = request.form['password']
    staff_service = StaffService()
    user = staff_service.login(username, password)
    if user is None:
        return jsonify({ "error": "Wrong username or password"}), 400

    return jsonify({
        "error": None,
        "staff": user.to_json()
    })

@app.route("/user/<id>")
def get_user_by_id(id):
    user_service = UserService()
    user = user_service.get_user_by_id(id)
    return jsonify(user.to_json())


@app.route('/signature/<user_id>', methods=['GET'])
def get_signature_by_user_id(user_id):
    signature_service = SignatureService()
    signatures = signature_service.get_by_user_id(user_id)

    return jsonify([signature.to_json() for signature in signatures])


@app.route('/signature', methods=['GET', 'POST'])
def add_signature_to_user():
    user_service = UserService()
    users = user_service.get_all_users()

    if request.method == 'GET':
        return render_template('signature.html', users=users)

    file, has_error, error_message = verify_upload_file(request)
    if has_error:
        return render_template('signature.html', users=users, has_error=True, error_message=error_message)

    file_content = file.read()
    user_id = request.form['user_id']
    signature_service = SignatureService()
    signature_service.add_signature(user_id, file_content)

    return render_template('upload_success.html')


@app.route('/api/signature', methods=['POST'])
def add_signature_to_user_by_api():
    file, has_error, error_message = verify_upload_file(request)
    if has_error:
        return jsonify({"error": error_message}), 400

    file_content = file.read()
    user_id = request.form['user_id']
    signature_service = SignatureService()
    signature_service.add_signature(user_id, file_content)

    return jsonify({"error": None}), 201


@app.route("/predict", methods=['GET', 'POST'])
def handle_predict():
    user_service = UserService()
    users = user_service.get_all_users()

    if request.method == 'GET':
        return render_template('predict.html', users=users)

    signature_file, has_error, error_message = verify_upload_file(request)
    if has_error:
        return render_template('predict.html', users=users, has_error=True, error_message=error_message)

    result = predict_signature(signature_file)
    return render_template('predict.html', users=users, show_result=True, probability=str(result))


@app.route("/api/predict", methods=['POST'])
def handle_predict_by_api():
    signature_file, has_error, error_message = verify_upload_file(request)
    if has_error:
        return jsonify({"error": error_message}), 400

    document_file, has_error, error_message = verify_upload_file(request, 'document')
    if has_error:
        return jsonify({"error": error_message}), 400

    result = predict_signature(signature_file, document_file)
    return jsonify({
        "error": None,
        "probability": str(result)
    })


@app.route("/api/signature_request", methods=['GET'])
def get_signature_requests():
    signature_service = SignatureService()
    signatures = signature_service.get_signature_requests()

    return jsonify([signature.to_json() for signature in signatures])


@app.route('/api/accept_request', methods=['POST'])
def accept_request():
    request_id = request.form['request_id']
    signature_service = SignatureService()
    signature_service.accept_request(request_id)

    return jsonify({"error": None})

if __name__ == 'app':
    app.run(host="0.0.0.0")


def predict_signature(signature_file, document_file):
    signature_test_image = save_image_in_temp(signature_file)
    document_test_image = save_image_in_temp(document_file)

    user_id = request.form['user_id']
    signature_service = SignatureService()
    signatures = signature_service.get_by_user_id(user_id)
    genuine_images = [signature.path for signature in signatures]

    result, best_fit_image_path = tensorflow_service.batch_predict(signature_test_image, genuine_images)
    result = round(result * 100, 2)

    signature_image_save_path = save_signature_request_image(user_id, signature_test_image)
    document_image_save_path = save_signature_request_image(user_id, document_test_image)
    signature_service.add_signature_request(user_id, signature_image_save_path, result, document_image_save_path, best_fit_image_path)

    return result


def save_image_in_temp(image_file):
    filename = image_file.filename
    image_file.save(f"./temp/{secure_filename(filename)}")
    return os.path.join(os.getcwd(), 'temp/' + filename)


def verify_upload_file(input_request, field='signature'):
    if field not in input_request.files:
        return None, True, "No file part"

    file = input_request.files[field]
    filename = file.filename
    if not file or filename == '':
        return file, True, "File is empty"

    if not allowed_file(file.filename):
        return file, True, "Only png and jpeg files are allowed"

    return file, False, None


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
