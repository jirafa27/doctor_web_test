from app.extensions import db


class File(db.Model):
    hash_sum = db.Column(db.String, primary_key=True)
    username = db.Column(db.String)