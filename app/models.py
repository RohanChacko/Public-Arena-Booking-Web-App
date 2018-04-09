from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db,login
from flask_login import UserMixin


class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    events = db.relationship('Events', backref='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Events(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(500))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    start_time = db.Column(db.Integer)
    end_time = db.Column(db.Integer)
    type = db.Column(db.Integer)

class Venues(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(500))
    capacity = db.Column(db.Integer)
    type = db.Column(db.String(64))
    events = db.relationship('Events', backref='venues')

class Invites(db.Model):
    __tablename__ = 'invites'
    id = db.Column(db.Integer, primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
    status = db.Column(db.Integer)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
