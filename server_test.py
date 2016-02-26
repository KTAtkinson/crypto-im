"""Tests for flask server."""

import unittest

import model
import seed
import server


class ChatClientTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initializes the test application."""
        pass

    def setUp(self):
        """Setup data for tests."""
        pass

    def tearDown(self):
        """Drops all tables."""
        pass

    def test_chat_page(self):
        """Test that the chat page route returns taxt/HTML.

            Given:
                A running chat server.

            When:
                Any top-level domain is requested that is not another route.

            Then:
                The chat page HTML is returned.
        """
        pass

    def test_join_new_chat(self):
        """Tests that a user can create and join a chat.

            Given:
                A running chat server.

            When:
                '/join/<conversation_id>' route is requested.

            Then:
                A chat is created with that conversation code, and a user is
                created with the name provided and added to the chat.
        """
        pass

    def test_join_existing_chat(self):
        """User can join existing chat with a single person.

            Given:
                A conversation with one other user.

            When:
                Another user joins.

           Then:
                The user is successfully added to the chat.
        """
        pass

    def test_full_conversation(self):
        """User receives an error when joining a conversation with two users.

        Given:
            A conversation that already has two users.

        When:
            Another user tries to join.

        Then:
            The server returns an error.
        """
        pass

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
        pass

    def test_status_all_messages(self):
        """All messages are returned when no last_message_seen_id is provided.

            Given:
                A converstaion with two users and some messages.

            When:
                A user requests status with no last_messsage_seen id.

            Then:
                They should recieve all outstanding messages in return.
        """
        pass

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
        pass

    def test_no_new_messages(self):
        """User receives no new messages when there are no new messages.

            Given:
                Users in a conversation, with messages.

            When:
                A user requests messages, but there are no new messages.

            Then:
            The users should not recieve any new messages
        """
        pass

    def test_send_message(self):
        """User can send message through '/add_message' route.

            Given:
                Users and a conversation.

            When:
                A user in the conversation adds a message.

            Then:
                Status code 200 should be returned.
        """
        pass
