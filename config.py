import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_SECRET_KEY')
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
