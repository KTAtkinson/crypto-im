"""Chat server"""

import datetime

import pytz
import jinja2
import flask
import flask_debugtoolbar

import model


app = flask.Flask(__name__)

# Required to user Flask sessions and the debug toolbar.
app.secret_key = 'DcYyy8kNOm9zUtl'

# Pervent Jinja from ignoring unprovided variables.
app.jinja_env.undefined = jinja2.StrictUndefined


@app.route('/<string:conversation_code>', methods=['GET'])
def get_chat_page(conversation_code):
    """Get the HTML for the chat page."""

    return flask.render_template('chat_page.html')


@app.route('/join/<string:conversation_code>', methods=['POST'])
def join_chat(conversation_code):
    """Adds a user to conversation, if the conversation doesn't exist, creates it.

    Args:
       conversation_code: <str> the human readable identifier for the chat.

    Returns:
       response: <str> json encoded, indicating if the join was successful or not.
    """

    raise NotImplementedError


@app.route('/status/<string:conversation_id>/<int:user_id>', methods=['POST'])
def update_user_status(conversation_id, user_id):
    """Updates the users last seen time and returns new messages.

    Args:
        conversation_id: <str> the conversation code for which this user's
           status should be www.
        user_id: <int> the user id to update.

    Returns:
        response: <str> json, containing the statues of other users in the
            conversation, and any new messages for the user.
    """
    pkey = flask.request.form.get('public_key')
    user = model.User.query.get(user_id)
    user.public_key = pkey
    user.last_seen = datetime.datetime.now(tz=pytz.utc)
    model.db.session.add(user)

    # print 'found and updated user.'
    last_msg_seen_id = flask.request.form.get('last_message_seen_id')

    print "Getting message."
    last_message = model.Message.query.get(last_msg_seen_id)

    # TODO: Move query to model.Message.
    query = model.db.session.query(model.Message).filter(
             model.Message.timestamp > last_message.timestamp,
             model.User.conversation_id==conversation_id,
             model.Message.recipient_id==user_id)
    query = query.order_by(model.Message.timestamp)
    new_messages = query.all()

    # TODO: Move to model.Message.
    new_message_dict_list = []
    for message in new_messages:
        message_dict = {
                'sender_name': message.author.name,
                'message': message.message
                }
        new_message_dict_list.append(message_dict)

    conversation_users = model.User.query.filter(
            model.User.conversation_id == conversation_id,
            model.User.user_id != user_id).all()
    print conversation_users

    # TODO: Move to model.Users
    conversation_users_dict_list = []
    for user in conversation_users:
        time_inactive = datetime.datetime.now(tz=pytz.utc) - user.last_seen
        user_dict = {
                'user_id': user.user_id,
                'public_key': user.public_key,
                'inactive_secs': time_inactive.total_seconds()
                }
        conversation_users_dict_list.append(user_dict)

    response = {
            'success': True,
            'users': conversation_users_dict_list,
            'new_messages': new_message_dict_list
            }
    model.db.session.commit()
    return flask.json.jsonify(response)


@app.route('/add_message/<string:conversation_id>', methods=['POST'])
def add_message(conversation_id):
    """Adds a message to the conversation as a given user.

    Args:
        conversation_id: <str> the conversation code for the conversation
            for which the message wwhould be added.

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

    app.run(debug=True)
