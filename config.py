import os

UPLOAD_FOLDER = './static/store'
SECRET_KEY = 'e567f408fa4c480b8712f34c142ef3ab'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = \
    'sqlite:///' + os.path.join(basedir, 'database.database')