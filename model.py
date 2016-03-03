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

    def add_invites(self):
        users = User.query.filter(
                User.conversation_id==self.conversation_id,
                User.user_id!=self.user_id).all()
        approver_ids = []

        # If there are no other users create approved invite in which the joining
        # user is both the joiner and the approver.
        if not users:
            invitation = Invitation(joining_user_id=self.user_id,
                                    approver_user_id=self.user_id,
                                    is_approved=True)
            db.session.add(invitation)

        for user in users:
            if not Invitation.query.filter_by(joining_user_id=user.user_id,
                                           is_approved=False).all():
                approver_ids.append(user.user_id)

        for user_id in approver_ids:
             invitation = Invitation(joining_user_id=self.user_id,
                                     approver_user_id=user_id)
             db.session.add(invitation)

        db.session.commit()

    def is_approved(self):
        """Returns True if the user is approved to join their conversation."""
        invites = Invitation.query.filter(
                Invitation.joining_user_id==self.user_id)
        for i in invites:
            if i.is_approved is False:
                return False

        return True



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


class Invitation(db.Model):
    """Model for chat invitations."""
    __tablename__ = "invitations"
    invite_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    joining_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                                nullable=False)
    approver_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'),
                                 nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    sent_timestamp = db.Column(db.DateTime)


    joinee = db.relationship('User',
                             foreign_keys='Invitation.joining_user_id',
                             backref=db.backref('approvals'))



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
    db.session.add(user1)
    user2 = User(name='bob', conversation_id=conversation.conversation_id,
                 public_key='')
    db.session.add(user2)
    db.session.commit()

    # Add messages between these users.
    msg1a = Message(author_id=user1.user_id, recipient_id=user2.user_id,
                   message='Hello')
    msg1b = Message(author_id=user1.user_id, recipient_id=user1.user_id,
                   message='Hello')
    db.session.add(msg1a)
    db.session.add(msg1b)

    msg2a = Message(author_id=user1.user_id, recipient_id=user2.user_id,
                   message='Hello!?')
    msg2b = Message(author_id=user1.user_id, recipient_id=user1.user_id,
                   message='Hello!?')
    db.session.add(msg2a)
    db.session.add(msg2b)

    msg3a = Message(author_id=user1.user_id, recipient_id=user2.user_id,
                   message='You there??')
    msg3b = Message(author_id=user1.user_id, recipient_id=user1.user_id,
                   message='You there??')
    db.session.add(msg3a)
    db.session.add(msg3b)
    db.session.commit()

    return (conversation, (user1, user2),
            (msg1a, msg1b, msg2a, msg2b, msg3a, msg3b))


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print "Connected to DB."
