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

        model.connect_to_db(app, db_name='chat_client_test')

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

    def testAddInviteToNewChat(self):
        """Tests adding an invite for new chat."""
        conv = model.Conversation(conversation_code='testing')
        model.db.session.add(conv)
        model.db.session.commit()

        user = model.User(name='alice', public_key='',
                          conversation_id=conv.conversation_id)
        model.db.session.add(user)
        model.db.session.commit()

        user.add_invites()
        invites = model.Invitation.query.filter_by(
                joining_user_id=user.user_id).all()

        self.assertEqual(len(invites), 1)
        self.assertEqual(user.user_id, invites[0].approver_user_id)

    def testIsApproved(self):
        """Tests is approved returns True when the user is approved."""
        self.assertTrue(self.user.is_approved())

    def testIsNotApproved(self):
        """Tests is approved returns False when a user is not approved."""
        user = model.User(conversation_id=self.conversation.conversation_id,
                          name='bob', public_key='')
        model.db.session.add(user)
        model.db.session.commit()

        invite = model.Invitation(joining_user_id=user.user_id,
                                  approver_user_id=self.user.user_id)

        model.db.session.add(invite)
        model.db.session.commit()

        self.assertFalse(user.is_approved())

    def testIsNotRejected(self):
        """Tests is_rejected method."""
        self.assertFalse(self.user.is_rejected())

    def testIsRejected(self):
        """Tests a user that is rejected."""
        u = model.User(name='bob', public_key='',
                    conversation_id=self.conversation.conversation_id)
        model.db.session.add(u)
        model.db.session.commit()
        user = u

        invite = model.Invitation(joining_user_id=user.user_id,
                                  approver_user_id=self.user.user_id,
                                  is_approved=False)
        model.db.session.add(invite)
        model.db.session.commit()

        self.assertTrue(u.is_rejected())

    def testIsNotRejectedIsRejectedNone(self):  
        """is_rejected returns False when invitation.is_approved is None."""
        u = model.User(name='bob', public_key='',
                    conversation_id=self.conversation.conversation_id)
        model.db.session.add(u)
        model.db.session.commit()
        user = u

        invite = model.Invitation(joining_user_id=user.user_id,
                                  approver_user_id=self.user.user_id)
        model.db.session.add(invite)
        model.db.session.commit()

        self.assertFalse(user.is_rejected())


class InvitationModelTest(unittest.TestCase):
    """Test for the invitation data model."""

    @classmethod
    def setUpClass(cls):
        """Initializes the database."""
        app = flask.Flask(__name__)
        app.config['TESTING'] = True

        model.connect_to_db(app, db_name='chat_client_test')

        model.db.drop_all()

    def setUp(self):
        """Setup database tables."""
        model.db.create_all()

        self.conversation = model.Conversation(conversation_code='foo')
        model.db.session.add(self.conversation)
        model.db.session.commit()

        user = model.User(
                conversation_id=self.conversation.conversation_id,
                name='alice', public_key='')
        model.db.session.add(user)
        model.db.session.commit()
        self.user = user

        invitation = model.Invitation(joining_user_id=user.user_id,
                                      approver_user_id=user.user_id)
        model.db.session.add(invitation)
        model.db.session.commit()
        self.invite = invitation

    def tearDown(self):
        """Closes database session and drops all tables."""
        model.db.session.close()
        model.db.drop_all()

    def testByApproverAndJoiner(self):
        retrieved = model.Invitation.by_approver_and_joiner(self.user.user_id,
                                                            self.user.user_id)
        self.assertEqual(retrieved.invite_id, self.invite.invite_id)


if __name__ == '__main__':
    unittest.main()

