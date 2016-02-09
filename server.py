"""Chat server"""

import jinja2
import flask
import flask_debugtoolbar
from sqlalchemy.orm import exc

import model


app = flask.Flask(__name__)

# Required to user Flask sessions and the debug toolbar.
app.secret_key = 'DcYyy8kNOm9zUtl'

# Pervent Jinja from ignoring unprovided variables.
app.jinja_env.undefined = jinja2.StrictUndefined


@app.route('/<string:conversation_code>', methods=['GET'])
def get_chat_page(conversation_code):
    """Get the HTML for the chat page."""

    raise NotImplementedError


@app.route('/join/<string:conversation_code>', methods=['POST'])
def join_chat(conversation_code):
    """Adds a user to conversation, if the conversation doesn't exist, creates it.

    Args:
       conversation_code: <str> the human readable identifier for the chat.

    Returns:
       response: <str> json encoded, indicating if the join was successful or not.
    """

    raise NotImplementedError


@app.route('/status/<string:conversation_id>', methods=['POST'])
def update_user_status(conversation_id):
     """Updates the users last seen time and returns new messages.

     Args:
         conversation_id: <str> the conversation code for which this user's
             status should be updated.

     Returns:
         response: <str> json, containing the statues of other users in the
             conversation, and any new messages for the user.
     """

     raise NotImplementedError


@app.route('/add_message/<string:conversation_id>', methods=['POST'])
def add_message(conversation_id):
    """Adds a message to the conversation as a given user.

    Args:
        conversation_id: <str> the conversation code for the conversation
            for which the message should be added.

    Returns:
        response: <str> json verifing that the message was posted.
    """

    raise NotImplementedError


if __name__ == '__main__':
    # Debugger is True so the debug toolbar is present.
    app.add_debug = True

    model.connect_to_db(app)

    # Add the debug toolbar.
    flask_debugtoolbar.DebugToolbarExtension(app)

    app.run()
