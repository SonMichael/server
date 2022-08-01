from services.Constants import API_VERSION_V1
import os

def isV1():
    return os.environ['FLASK_API_VERSION'] == API_VERSION_V1
