import os.path
import cv2 as cv
import numpy as np
import tensorflow as tf
import tensorflow.keras.backend as K
from flask import g

def contrastive_loss(y_true, y_pred):
    margin = 1
    square_pred = tf.math.square(y_pred)
    margin_square = tf.math.square(tf.math.maximum(margin - (y_pred), 0))
    return tf.math.reduce_mean(
        (1 - y_true) * square_pred + (y_true) * margin_square
    )

def load_model():
    if 'tensorflow_model' not in g:
        saved_model_path = os.path.join(os.getcwd(), 'saved_model/1')
        g.tensorflow_model = tf.keras.models.load_model(
            saved_model_path,
            custom_objects={"K": K, "contrastive_loss": contrastive_loss}
        )

    return g.tensorflow_model


def read_image(path):
    image = cv.imread(path, cv.COLOR_BGR2RGB)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(image_gray, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
    image_white = cv.bitwise_not(thresh)
    return np.array(image_white).reshape(1, 150, 150, 1)

def read_image_resnet(path):
    image = cv.imread(path, cv.COLOR_BGR2RGB)
    image_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    _, thresh = cv.threshold(image_gray, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
    image_white = cv.bitwise_not(thresh)
    image_white = cv.cvtColor(image_white, cv.COLOR_GRAY2RGB)
    return image_white
    # return np.repeat(image_white[..., np.newaxis], 3, -1)

def read_image_by_tensorflow(path):
    image_content = tf.io.read_file(path)
    image = tf.image.decode_png(image_content, channels=1)
    return tf.reshape(image, [1, 150, 150, 1])

def predict(images_paths):
    (image_path_1, image_path_2) = images_paths
    image1 = read_image(image_path_1)
    image2 = read_image(image_path_2)

    # image1_content = tf.io.read_file(image_path_1)
    # image1 = tf.image.decode_png(image1_content, channels=1)
    # image1 = tf.reshape(image1, [1, 150, 150, 1])

    # image2_content = tf.io.read_file(image_path_2)
    # image2 = tf.image.decode_png(image2_content, channels=1)
    # image2 = tf.reshape(image2, [1, 150, 150, 1])

    model = load_model()
    result = model.predict([image1, image2])
    return result[0][0]
