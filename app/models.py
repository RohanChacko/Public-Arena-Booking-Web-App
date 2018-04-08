from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db,login
from flask_login import UserMixin


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    venues = db.relationship('Book', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)     #A field in which a function is passed as default, will be set to the value of the called function
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.venue)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))