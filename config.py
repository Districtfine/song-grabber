import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
