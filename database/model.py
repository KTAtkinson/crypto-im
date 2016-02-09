"""Database model for chat client."""

import datetime


from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """Models a chat client user."""

    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    public_key = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)


class Conversation(db.Model):
    """Model for a chat conversation."""

    __tablename__ = "conversations"
    conversation_id = db.Column(db.Integer, primary_key=True)
    conversation_code = db.Column(db.String(20))


class Message(db.Model):
    """Model for a chat message."""

    __tablename__ = "messages"
    message_id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.conversation_id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    author = db.relationship('User',
                             foreign_keys='Message.author_id',
                             backref=db.backref('sent_messages'))
    recipient = db.relationship('User',
                                foreign_keys='Message.recipient_id',
                                backref=db.backref('recieved_messages'))


# The following code was borrowed from a Hackbright skiills assessment on
# it provides an interactive python prompt for quiering and manipulating
# the databsse.
##############################################################################

def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///chat-client'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
