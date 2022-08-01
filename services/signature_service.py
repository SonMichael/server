import cv2 as cv
import numpy as np
from datetime import datetime
from database import database
from models.signature import Signature
from models.signature_request import SignatureRequest
from services.Constants import IMAGE_WIDTH, IMAGE_HEIGHT, IMAGE_WIDTH_V2, IMAGE_HEIGHT_v2
from services.helper import isV1


class SignatureService:
    def __init__(self):
        self.connection = database.open()

    def get_by_user_id(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, path FROM signature WHERE user_id = " + str(user_id))

        signatures = []
        for row in cursor.fetchall():
            signature = Signature(id=row[0], path=row[1], user_id=user_id)
            signatures.append(signature)

        return signatures

    def add_signature(self, user_id, file_content):
        saved_file_path = save_signature_image(user_id, file_content)
        self.create_signature_record(user_id, saved_file_path)

    def create_signature_record(self, user_id, image_path):
        sql_query = "INSERT INTO signature(path, user_id) VALUES('{}', {});".format(image_path, user_id)
        cursor = self.connection.cursor()
        cursor.execute(sql_query)
        self.connection.commit()

    def add_signature_request(self, user_id, image_path, similarity, document_path, best_fit_image_path):
        sql_query = """
        INSERT INTO signature_request(path, user_id, similarity, document_path, most_genuine_signature)
        VALUES('{}', {}, {}, '{}', '{}');
        """.format(image_path, user_id, similarity, document_path, best_fit_image_path)
        cursor = self.connection.cursor()
        cursor.execute(sql_query)
        self.connection.commit()

    def get_signature_requests(self):
        cursor = self.connection.cursor()
        cursor.execute("""
        SELECT r.id, r.path, r.user_id, r.similarity,
         STRFTIME('%Y-%m-%d %H:%M:%S', r.created_date),
         r.is_accepted, u.username, r.document_path, r.most_genuine_signature
        FROM signature_request r LEFT JOIN user u on u.id = r.user_id
        ORDER BY r.id DESC;
        """)

        signatures = []
        for row in cursor.fetchall():
            signature = SignatureRequest(
                id=row[0],
                path=row[1],
                document_path=row[7],
                user_id=row[2],
                username=row[6],
                similarity=row[3],
                created_date=row[4],
                is_accepted=row[5],
                most_genuine_signature=row[8]
            )
            signatures.append(signature)

        return signatures

    def accept_request(self, request_id):
        sql_query = """
        UPDATE signature_request SET is_accepted = 1
        WHERE id = {};
        """.format(request_id)
        cursor = self.connection.cursor()
        cursor.execute(sql_query)
        self.connection.commit()


def save_image(user_id, image):
    return _save_image(user_id, image, 'static/saved_images')


def save_signature_request_image(user_id, image_path):
    image = cv.imread(image_path, cv.IMREAD_UNCHANGED)
    return _save_image(user_id, image, 'static/signature_request')


def _save_image(user_id, image, save_folder):
    now = datetime.now()
    date_time_formatted = now.strftime("%Y_%m_%d_%H_%M_%S")
    saved_file_path = "./{0}/{1}_{2}.png".format(save_folder, user_id, date_time_formatted)
    cv.imwrite(saved_file_path, image)
    return saved_file_path


def preproccess_image(image):
    # TODO: Fix this
    # image = extract_signature(image)
    if isV1():
        return resize_image(image)
    return preprocess_image_v2(image)

def convert_to_gray(img):
    if(len(img.shape) == 2):
        return img
    return cv.cvtColor(img, cv.COLOR_BGR2GRAY)

def preprocess_image_v2(img):
    gray = convert_to_gray(img)
    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv.dilate(gray, kernel, iterations=1)
    img = cv.erode(gray, kernel, iterations=1)

    imgResize = cv.resize(img,(IMAGE_WIDTH_V2, IMAGE_HEIGHT_v2))
    adaptive_threshold = cv.adaptiveThreshold(imgResize, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY,85,11)
    return adaptive_threshold


def extract_signature(image):
    original_image = image.copy()
    width, height = image.shape

    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    ret, thresh = cv.threshold(gray, 0, 127, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)

    rect_kernel = cv.getStructuringElement(cv.MORPH_RECT, (10, 10))
    dilation = cv.dilate(thresh, rect_kernel, iterations=1)

    contours, hierarchy = cv.findContours(dilation, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return original_image

    contours = sorted(contours, key=cv.contourArea, reverse=True)
    x_start = width
    y_start = height
    x_end = 0
    y_end = 0
    for contour in contours:
        x, y, w, h = cv.boundingRect(contour)
        if x < x_start:
            x_start = x

        if y < y_start:
            y_start = y

        if (x + w) > x_end:
            x_end = (x + w)

        if (y + h) > y_end:
            y_end = (y + h)

    crop_image = original_image[y_start:y_end, x_start:x_end]
    return crop_image


def resize_image(image):
    return cv.resize(image, (IMAGE_WIDTH, IMAGE_HEIGHT), interpolation=cv.INTER_LINEAR)


def save_signature_image(user_id, file_content):
    image = cv.imdecode(np.fromstring(file_content, np.uint8), cv.IMREAD_UNCHANGED)
    processed_image = preproccess_image(image)
    saved_file_path = save_image(user_id, processed_image)

    return saved_file_path
