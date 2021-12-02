import os.path
import cv2 as cv
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from flask import g

from services.signature_service import preproccess_image


def contrastive_loss(y_true, y_pred):
    margin = 1
    square_pred = tf.math.square(y_pred)
    margin_square = tf.math.square(tf.math.maximum(margin - (y_pred), 0))
    return tf.math.reduce_mean(
        (1 - y_true) * square_pred + (y_true) * margin_square
    )


def load_model():
    if 'tensorflow_model' not in g:
        saved_model_path = os.path.join(os.getcwd(), 'saved_model/1_1')
        g.tensorflow_model = tf.keras.models.load_model(
            saved_model_path,
            custom_objects={"K": K, "contrastive_loss": contrastive_loss}
        )

    return g.tensorflow_model


def read_image(path):
    image = cv.imread(path, cv.IMREAD_UNCHANGED)
    # image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # _, thresh = cv.threshold(image_gray, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
    # image_white = cv.bitwise_not(thresh)

    image = preproccess_image(image)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    width, height = image_gray.shape
    return np.array(image_gray).reshape(1, width, height, 1)


def read_image_by_tensorflow(path):
    image_content = tf.io.read_file(path)
    image = tf.image.decode_png(image_content, channels=1)
    return tf.reshape(image, [1, 150, 150, 1])


def predict(images_paths):
    (image_path_1, image_path_2) = images_paths
    image1 = read_image(image_path_1)
    image2 = read_image(image_path_2)

    model = load_model()
    result = model.handle_predict([image1, image2])
    return result[0][0]


def batch_predict(test_image_path, genuine_image_paths):
    test_image = read_image(test_image_path)
    genuine_images = [read_image(image) for image in genuine_image_paths]

    genuine_images_length = len(genuine_images)
    inputs = [np.zeros((genuine_images_length, 150, 150, 1)) for i in range(2)]
    for i in range(genuine_images_length):
        inputs[0][i, :, :, :] = genuine_images[i]
        inputs[1][i, :, :, :] = test_image

    model = load_model()
    result = model.predict(inputs)
    return result.max()
