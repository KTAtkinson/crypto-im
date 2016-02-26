"""Database model for chat client."""

import datetime


from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """Models a chat client user."""

    __tablename__ = "users"
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(25))
    public_key = db.Column(db.Text())
    last_seen = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now)
    conversation_id = db.Column(
            db.Integer,
            db.ForeignKey('conversations.conversation_id'),
            nullable=False)


class Conversation(db.Model):
    """Model for a chat conversation."""

    __tablename__ = "conversations"
    conversation_id = db.Column(db.Integer, autoincrement=True,
                                primary_key=True)
    conversation_code = db.Column(db.String(20))


class Message(db.Model):
    """Model for a chat message."""

    __tablename__ = "messages"
    message_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.datetime.now)

    author = db.relationship('User',
                             foreign_keys='Message.author_id',
                             backref=db.backref('sent_messages'))
    recipient = db.relationship('User',
                                foreign_keys='Message.recipient_id',
                                backref=db.backref('recieved_messages'))

    @classmethod
    def get_by_message_id(cls, message_id):
        return cls.query.get(message_id)


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


def connect_to_db(app, db_name='chat-client'):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///{}'.format(db_name)
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


def seed(app):
    # Create conversation.
    conversation = Conversation(conversation_code='great-conv')
    db.session.add(conversation)
    db.session.commit()

    # Create two users in the conversation.
    user1 = User(name='alice', conversation_id=conversation.conversation_id,
                 public_key='')
    user2 = User(name='bob', conversation_id=conversation.conversation_id,
                 public_key='')
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()

    # Add messages between these users.
    msg1 = Message(author_id=user1.user_id, recipient_id=user2.user_id,
                   message='Hello')
    db.session.add(msg1)
    db.session.commit()

    msg2 = Message(author_id=user1.user_id, recipient_id=user2.user_id,
                   message='Hello!?')
    db.session.add(msg2)
    db.session.commit()

    msg3 = Message(author_id=user1.user_id, recipient_id=user2.user_id,
                   message='You there??')
    db.session.add(msg2)
    db.session.commit()

    return (conversation, (user1, user2), (msg1, msg2, msg3))


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
