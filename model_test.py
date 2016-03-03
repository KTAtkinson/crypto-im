"""Tests for database model methods."""
import unittest

import flask

import model


class UserModelTest(unittest.TestCase):
    """Tests for the user model."""

    @classmethod
    def setUpClass(cls):
        """Initializes the database."""
        app = flask.Flask(__name__)
        app.config['TESTING'] = True

        model.connect_to_db(app, db_name='chat-client-test')

        model.db.drop_all()

    def setUp(self):
        """Setup database tables."""
        model.db.create_all()

        self.conversation = model.Conversation(conversation_code='foo')
        model.db.session.add(self.conversation)
        model.db.session.commit()

        self.user = model.User(
                conversation_id=self.conversation.conversation_id,
                name='alice', public_key='')
        model.db.session.add(self.user)
        model.db.session.commit()

        self.user.add_invites()

    def tearDown(self):
        """Closes database session and drops all tables."""
        model.db.session.close()
        model.db.drop_all()


    def testAddInvite(self):
        """Tests that invite is created for user."""
        invites = model.Invitation.query.filter_by(
                joining_user_id=self.user.user_id).all()

        self.assertEqual(len(invites), 1)
        self.assertTrue(invites[0].is_approved)

    def testAddInviteExistingChat(self):
        """Tests adding a user to an existing chat."""
        user = model.User(name='bob', public_key='',
                    conversation_id=self.conversation.conversation_id)
        model.db.session.add(user)
        model.db.session.commit()
        user.add_invites()
        invites = model.Invitation.query.filter_by(
                joining_user_id=user.user_id).all()

        self.assertEqual(len(invites), 1)
        self.assertFalse(invites[0].is_approved)


if __name__ == '__main__':
    unittest.main()

