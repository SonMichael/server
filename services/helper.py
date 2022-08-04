from services.Constants import API_VERSION_V1, CONFIGS
from services.config_service import ConfigService

def isV1():
    service = ConfigService()
    config = service.get_by(CONFIGS['API_VERSION'])
    return config.value == API_VERSION_V1
