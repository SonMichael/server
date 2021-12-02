import cv2 as cv
import numpy as np
from datetime import datetime
from database import database
from models.signature import Signature


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


def save_image(user_id, image):
    now = datetime.now()
    date_time_formatted = now.strftime("_%Y_%m_%d_%H_%M_%S")
    saved_file_path = f"./saved_images/" + str(user_id) + date_time_formatted + ".png"
    cv.imwrite(saved_file_path, image)
    return saved_file_path


def preproccess_image(image):
    image = extract_signature(image)
    image = make_square_image(image)
    image = resize_image(image, 150)
    return image


def extract_signature(image):
    original_image = image.copy()
    width, height, channels = image.shape

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


def make_square_image(image):
    height, width, channels = image.shape

    # Create a black image
    x = height if height > width else width
    y = height if height > width else width
    max_dimension = max(x, y)
    white_square_background = np.full((max_dimension, max_dimension, channels), 255, np.uint8)

    white_square_background[int((y - height) / 2):int(y - (y - height) / 2),
    int((x - width) / 2):int(x - (x - width) / 2)] = image

    return white_square_background


def resize_image(image, size):
    return cv.resize(image, (size, size), interpolation=cv.INTER_AREA)


def save_signature_image(user_id, file_content):
    image = cv.imdecode(np.fromstring(file_content, np.uint8), cv.IMREAD_UNCHANGED)
    processed_image = preproccess_image(image)
    saved_file_path = save_image(user_id, processed_image)

    return saved_file_path
