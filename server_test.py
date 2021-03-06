"""Tests for flask server."""

import json
import unittest

from flask import json

import model
import server


class ChatClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes the test application."""
        cls.client = server.app.test_client()
        server.app.config['TESTING'] = True

        model.connect_to_db(server.app, db_name='chat_client_test')
        # Clear any data that may be in the database.
        model.db.drop_all()

    def setUp(self):
        """Setup data for tests."""
        model.db.create_all()
        (self.conversation,
         self.users,
         self.msgs) = model.seed(server.app)

    def tearDown(self):
        """Drops all tables."""
        model.db.session.close()
        model.db.drop_all()
        with self.client as c:
            with c.session_transaction() as sess:
                sess.clear()

    def test_chat_page(self):
        """Test that the chat page route returns taxt/HTML.

            Given:
                A running chat server.

            When:
                Any top-level domain is requested that is not another route.

            Then:
                The chat page HTML is returned.
        """
        c_code = 'new-chat'
        rsp = self.client.get('/{}'.format(c_code))
        html = rsp.data

        self.assertEqual(200, rsp.status_code)
        # HTML is returned.
        self.assertIn('<html>', html)
        # HTML for chat is retrieved.
        self.assertIn(c_code, html)

    def test_join_new_chat(self):
        """Tests that a user can create and join a chat.

            Given:
                A running chat server.

            When:
                '/join/<conversation_code>' route is requested.

            Then:
                A chat is created with that conversation code, and a user is
                created with the name provided and added to the chat.
        """
        rsp = self.client.post('/join/join-here', data={'name': 'bob'})
        rsp_json = json.loads(rsp.data)

        self.assertEqual(200, rsp.status_code)
        self.assertTrue(rsp_json['success'])
        self.assertEquals(rsp_json['error'], '')
        self.assertIn('new_user_id', rsp_json)
        self.assertIn('conversation_id', rsp_json)

    def test_join_existing_chat(self):
        """User can join existing chat with a single person.

            Given:
                A conversation with one other user.

            When:
                Another user joins.

          Then:
              The user is successfully added to the chat.
       """
        conv_code = 'new-chat'
        conv = model.Conversation(conversation_code=conv_code)
        model.db.session.add(conv)
        model.db.session.commit()

        user1 = model.User(name='bob', conversation_id=conv.conversation_id,
                           public_key='')
        model.db.session.add(user1)
        model.db.session.commit()

        rsp = self.client.post('/join/{}'.format(conv_code),
                               data={'name': 'alice'})

        self.assertEqual(200, rsp.status_code)

    def test_invites_added(self):
        """Invites are created for each user in the conversation."""
        rsp = self.client.post('/join/join-here', data={'name': 'bob'})
        rsp_json = json.loads(rsp.data)

        invites = model.Invitation.query.filter_by(
                joining_user_id=rsp_json['new_user_id']).count()
        self.assertNotEqual(int(invites), 0)

    def test_status(self):
        """Test that /status route returns JSON response.

            Given:
                Users and a conversation.

            When:
                A users updates their status.

            Then:
                The response contains new messages and the status of other users
                in the conversation.
        """
        conversation_id = self.conversation.conversation_id
        user_id = self.users[0].user_id
        self.setup_invites()

        uri = '/status/{}/{}'.format(conversation_id, user_id)
        self.set_session_cookie(user_id, conversation_id)
        self.set_user_cookie(user_id, conversation_id)

        rsp = self.client.post(uri, data={'public_key': '',
                                          'last_message_seen_id': None})
        rsp_json = json.loads(rsp.data)

        self.assertEqual(200, rsp.status_code)
        self.assertTrue(rsp_json['success'])
        self.assertIn('users', rsp_json)
        self.assertIn('new_messages', rsp_json)
        self.assertIn('invitations', rsp_json)
        # All messages are in the response because no last_message_seen_id
        # is specified.
        self.assertEqual(3, len(rsp_json['new_messages']))

    def test_status_new_messages(self):
        """User receives new messages when they update their status.

             Given:
                 A conversation with users and messages.

             When:
                 A user updates their status with a last_message_seen_id.

             Then:
                 They recieve all messages back that where sent after the
                message_id provided by the client.
        """
        conversation_id = self.conversation.conversation_id
        self.setup_invites()
        user_id = self.users[0].user_id
        message_id = self.msgs[1].message_id
        uri = '/status/{}/{}'.format(conversation_id, user_id)
        self.set_session_cookie(user_id, conversation_id)
        self.set_user_cookie(user_id, conversation_id)
        rsp = self.client.post(uri,
                               data={'public_key': '',
                                     'last_message_seen_id': message_id})
        rsp_json = json.loads(rsp.data)

        self.assertEqual(200, rsp.status_code)
        self.assertTrue(rsp_json['success'])
        self.assertIn('users', rsp_json)
        self.assertIn('new_messages', rsp_json)
        # All messages are in the response because no last_message_seen_id
        # i specified.
        self.assertEqual(2, len(rsp_json['new_messages']))

    def test_new_invitation(self):
        """User recieves an invitation when there is one outstanding."""
        (approval_user_id,
         joining_user_id,
         conversation_id,
         _) = self.setup_invites()
        uri = '/status/{}/{}'.format(conversation_id, approval_user_id)
        self.set_user_cookie(approval_user_id, conversation_id)
        self.set_session_cookie(approval_user_id, conversation_id)
        resp = self.client.post(
                uri, data={'public_key':'', 'last_message_seen_id': None})
        resp_json = json.loads(resp.data)

        invitations = resp_json['invitations']
        self.assertEqual(len(invitations), 1)
        self.assertEqual(invitations[0]['user_id'], joining_user_id)

    def test_no_new_messages(self):
        """User receives no new messages when there are no new messages.

            Given:
                Users in a conversation, with messages.

            When:
                A user requests messages, but there are no new messages.

            Then:
            The users should not recieve any new messages
        """
        conversation_id = self.conversation.conversation_id
        self.setup_invites()
        user_id = self.users[0].user_id
        message_id = self.msgs[-1].message_id
        uri = '/status/{}/{}'.format(conversation_id, user_id)
        self.set_session_cookie(user_id, conversation_id)
        self.set_user_cookie(user_id, conversation_id)
        rsp = self.client.post(uri,
                               data={'public_key': '',
                                     'last_message_seen_id': message_id})
        rsp_json = json.loads(rsp.data)

        self.assertEqual(0, len(rsp_json['new_messages']))

    def test_not_approved_user(self):
        """Not approved user recieves and error when updating status."""
        (_,
         joining_user_id,
         conversation_id,
         _) = self.setup_invites(is_approved=None)
        self.set_session_cookie(joining_user_id, conversation_id)
        self.set_user_cookie(joining_user_id, conversation_id)
        uri = '/status/{}/{}'.format(conversation_id, joining_user_id)
        rsp = self.client.post(uri,
                               data={'public_key': '',
                                     'last_message_seen_id': 0})

        rsp_json = json.loads(rsp.data)
        self.assertFalse(rsp_json['success'])

    def test_not_approved_user(self):
        """Not approved user recieves and error when updating status."""
        (_,
         joining_user_id,
         conversation_id,
         _) = self.setup_invites(is_approved=False)
        self.set_session_cookie(joining_user_id, conversation_id)
        self.set_user_cookie(joining_user_id, conversation_id)
        uri = '/status/{}/{}'.format(conversation_id, joining_user_id)
        rsp = self.client.post(uri,
                               data={'public_key': '',
                                     'last_message_seen_id': 0})

        rsp_json = json.loads(rsp.data)
        self.assertFalse(rsp_json['success'])

    def test_ack_invitation(self):
        """Test acknowledging an invitation."""
        (approver_user_id,
         joining_user_id,
         _,
         invite_id) = self.setup_invites()
        uri = '/invite_ack/{}/{}'.format(approver_user_id, joining_user_id)
        rsp = self.client.post(uri, data={'approves': True})
        rsp_json = json.loads(rsp.data)

        invite = model.Invitation.query.get(invite_id)
        self.assertEqual(rsp_json['success'], True)
        self.assertEqual(rsp.status_code, 200)
        self.assertEqual(invite.invite_id, invite_id)


    def test_send_message(self):
        """User can send message through '/add_message' route.

            Given:
                Users and a conversation.

            When:
                A user in the conversation adds a message.

            Then:
                Status code 200 should be returned.
        """
        sender = self.users[1].user_id
        reciever = self.users[0].user_id
        conversation_id = self.conversation.conversation_id

        uri = '/add_message/{}/{}'.format(conversation_id, sender)
        self.set_session_cookie(sender, conversation_id)
        self.set_user_cookie(sender, conversation_id)
        msg_text = 'howdy!'
        msgs = {0: {'user_id': reciever, 'encoded_message': msg_text},
                1: {'user_id': sender, 'encoded_message': msg_text}}

        rsp = {'encoded_messages': json.dumps(msgs)}
        rsp = self.client.post(uri, data=rsp)
        rsp_json = json.loads(rsp.data)

        self.assertTrue(rsp_json['success'])
        self.assertIsNone(rsp_json['error'])


    def set_user_cookie(self, user_id, conversation_id):
        self.client.set_cookie('localhost',
                               '-'.join(['chat', 'data', str(conversation_id)]),
                               ':'.join([str(user_id), str(conversation_id)]))

    def set_session_cookie(self, user_id, conversation_id):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[str(conversation_id)] = (
                        ":".join([str(user_id), str(conversation_id)]))

    def setup_invites(self, is_approved=False):
        approver = self.users[0]
        conversation_id = self.conversation.conversation_id
        invite = model.Invitation(joining_user_id=approver.user_id,
                                  approver_user_id=approver.user_id,
                                  is_approved=True)
        model.db.session.add(invite)
        joiner = model.User(conversation_id=conversation_id,
                           name='bob', public_key='')
        model.db.session.add(joiner)
        model.db.session.commit()
        joiner_user_id = joiner.user_id 

        invite = model.Invitation(joining_user_id=joiner_user_id,
                                  approver_user_id=approver.user_id,
                                  is_approved=is_approved)
        model.db.session.add(invite)
        model.db.session.commit()
        return (approver.user_id, joiner_user_id, conversation_id,
                invite.invite_id)


if __name__ == '__main__':
    unittest.main()
