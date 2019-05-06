import os


from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from urls import register_urls


app = Flask(__name__)

app.config["SECRET_KEY"] = "stXruuKhdbG2-g"

CORS(app)

DB_USER = "root"
DB_PASSWORD = "admin123"
DB_HOST = "localhost"
DB_PORT = "3306"
DB_NAME = "target_db"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{0}:{1}@{2}/{3}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

register_urls(app)