from flask import Flask

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    from .extensions import db
    with app.app_context():
        db.init_app(app)
        db.create_all()
    return app


app = create_app()
