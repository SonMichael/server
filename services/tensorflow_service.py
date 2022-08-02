import os.path
import cv2 as cv
import numpy as np
import tensorflow as tf
from keras import backend as K
from flask import g

from services.signature_service import preproccess_image
from services.helper import isV1
from services.Constants import  CLASSES_V2


# def contrastive_loss(y_true, y_pred):
#     margin = 1
#     square_pred = tf.math.square(y_pred)
#     margin_square = tf.math.square(tf.math.maximum(margin - (y_pred), 0))
#     return tf.math.reduce_mean(
#         (1 - y_true) * square_pred + (y_true) * margin_square
#     )

def euclidean_distance(vectors):
    # unpack the vectors into separate lists
    (x, y) = vectors
    # compute the sum of squared distances between the vectors
    sum_squared = K.sum(K.square(x - y), axis=1, keepdims=True)
    # return the euclidean distance between the vectors
    return K.sqrt(K.maximum(sum_squared, K.epsilon()))


def contrastive_loss(y, prediction, margin=1):
    # explicitly cast the true class label data type to the predicted
    # class label data type (otherwise we run the risk of having two
    # separate data types, causing TensorFlow to error out)
    y = tf.cast(y, prediction.dtype)
    # calculate the contrastive loss between the true labels and
    # the predicted labels
    squared_predictions = K.square(prediction)
    squared_margin = K.square(K.maximum(margin - prediction, 0))
    return K.mean(y * squared_predictions + (1 - y) * squared_margin)

def get_model():
    if isV1():
        saved_model_path = os.path.join(os.getcwd(), 'saved_model/4')
        tensorflow_model = tf.keras.models.load_model(
                saved_model_path,
                custom_objects={
                    "K": K,
                    "euclidean_distance": euclidean_distance,
                    "contrastive_loss": contrastive_loss
                    # "contrastive_loss": contrastive_loss
                }
            )
        return tensorflow_model
    saved_model_path = os.path.join(os.getcwd(), 'saved_model/v2')
    return tf.keras.models.load_model(saved_model_path)
    

def load_model():
    if 'tensorflow_model' not in g:
        
        g.tensorflow_model = get_model()

    return g.tensorflow_model


def read_image(path):
    if not isV1():
        return get_image_v2(path)
    image = cv.imread(path, cv.IMREAD_GRAYSCALE)
    image = preproccess_image(image)
    gray_image = cv.bitwise_not(image)
    normalized_image = gray_image / 255.0
    (height, width) = image.shape
    return np.array(normalized_image).reshape(height, width, 1)

def get_image_v2(path):
    image = cv.imread(path)
    image = (image[...,::-1].astype(np.float32)) / 255.0
    image = np.expand_dims(image,axis = 0 )
    return image

def batch_predict(test_image_path, genuine_image_paths):
    test_image = read_image(test_image_path)
    genuine_images = [read_image(image) for image in genuine_image_paths]

    genuine_images_length = len(genuine_images)
    (height, width, _) = test_image.shape
    inputs = [np.zeros((genuine_images_length, height, width, 1)) for i in range(2)]
    for i in range(genuine_images_length):
        inputs[0][i] = test_image
        inputs[1][i] = genuine_images[i]

    model = load_model()
    results = model.predict(inputs)

    max_result = -1
    max_index = -1
    for index, result in enumerate(results):
        if result.max() > max_result:
            max_result = result.max()
            max_index = index

    return max_result, genuine_image_paths[max_index]

def predict_v2(test_image_path, user_id):
    test_image = read_image(test_image_path)
    model = load_model()
    classes = model.predict(test_image)
    label = CLASSES_V2[user_id]
    return classes[0][label]

