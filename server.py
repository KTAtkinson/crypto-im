"""Chat server"""

import datetime
import json

import pytz
import jinja2
import flask
import flask_debugtoolbar
from sqlalchemy.orm.exc import NoResultFound

import model


app = flask.Flask(__name__)

# Required to user Flask sessions and the debug toolbar.
app.secret_key = 'DcYyy8kNOm9zUtl'

# Pervent Jinja from ignoring unprovided variables.
app.jinja_env.undefined = jinja2.StrictUndefined


@app.route('/<string:conversation_code>', methods=['GET'])
def get_chat_page(conversation_code):
    """Get the HTML for the chat page."""

    return flask.render_template('chat_page.html',
                                 conversation_code=conversation_code)


@app.route('/join/<string:conversation_code>', methods=['POST'])
def join_chat(conversation_code):
    """Adds a user to conversation, if the conversation doesn't exist, creates it.

    Args:
       conversation_code: <str> the human readable identifier for the chat.

    Returns:
       response: <str> json encoded, indicating if the join was successful or not.
    """

    try:
        conversation = model.Conversation.query.filter_by(
                conversation_code=conversation_code).one()
    except NoResultFound:
        conversation = model.Conversation(conversation_code=conversation_code)
        model.db.session.add(conversation)
        model.db.session.commit()

    user_query = model.User.query.filter_by(
            conversation_id=conversation.conversation_id)
    num_users = user_query.count()

    if num_users > 1:
        response = {
                'success': False,
                'error': 'There is no room in this conversation.'}
        return flask.json.jsonify(response), 400

    name = flask.request.form.get('name')
    pkey = flask.request.form.get('public_key')
    new_user = model.User(name=name, public_key=pkey,
                          conversation_id=conversation.conversation_id)
    model.db.session.add(new_user)
    model.db.session.commit()

    str_user_id = str(new_user.user_id)
    str_conv_id = str(conversation.conversation_id)
    flask.session[str_conv_id] = ':'.join([str_user_id, str_conv_id])
    rsp = {
            'success': True,
            'error': '',
            'new_user_id': new_user.user_id,
            'conversation_id': new_user.conversation_id,
            }
    response = app.make_response(flask.json.jsonify(rsp))
    response.set_cookie("chat-data-"+str_conv_id, value=str_user_id+":"+str_conv_id)
    return response


@app.route('/status/<string:conversation_id>/<int:user_id>', methods=['POST'])
def update_user_status(conversation_id, user_id):
    """Updates the users last seen time and returns new messages.

    Args:
        conversation_id: <str> the conversation code for which this user's
           status should be updated.
        user_id: <int> the user id to update.

    Returns:
        response: <str> json, containing the statues of other users in the
            conversation, and any new messages for the user.
    """
    verified = (
            VerifyCookies(flask.session,
                          flask.request.cookies['chat-data-'+conversation_id]))
    if not verified:
        return flask.json.jsonify({'success': False,
                                   'error': "Was not able to verify user."})
    pkey = flask.request.form.get('public_key')
    print "AVAILABLE FORM FIELDS:", flask.request.form.keys()
    user = model.User.query.get(user_id)
    user.public_key = pkey
    user.last_seen = datetime.datetime.now(tz=pytz.utc)
    model.db.session.add(user)

    # print 'found and updated user.
    last_msg_seen_id = flask.request.form.get('last_message_seen_id')

    print "Getting message."
    if last_msg_seen_id:
        last_message_time = model.Message.query.get(last_msg_seen_id).timestamp
    else:
        last_message_time = datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)

    # TODO: Move query to model.Message.
    query = model.db.session.query(model.Message).filter(
             model.Message.timestamp > last_message_time,
             model.User.conversation_id==conversation_id,
             model.Message.recipient_id==user_id)
    query = query.order_by(model.Message.timestamp)
    new_messages = query.all()

    # TODO: Move to model.Message.
    new_message_dict_list = []
    for message in new_messages:
        message_dict = {
                'sender_name': message.author.name,
                'message': message.message,
                'message_id': message.message_id
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


@app.route('/add_message/<string:conversation_id>/<string:user_id>',
           methods=['POST'])
def add_message(conversation_id, user_id):
    """Adds a message to the conversation as a given user.

    Args:
        conversation_id: <str> the conversation code for the conversation
            for which the message would be added..
        user_id: <str> user id for the user who is sending the message.

    Returns:
        response: <str> json verifing that the message was posted.
    """
    verified = (
            VerifyCookies(flask.session,
            flask.request.cookies['chat-data-'+conversation_id]))
    if not verified:
        return flask.json.jsonify({'success': False,
                                   'error': "Failed to verify user."})
    author = model.User.query.get(user_id)
    if author.conversation_id != int(conversation_id):
        response = {
                'success': False,
                'error': "You don't have permission to send meesages in "
                            "this chat."
                }
        return flask.json.jsonify(response), 403 

    messages = flask.json.loads(flask.request.form.get('encoded_messages'))
    for msg_index in messages:
        message = messages[msg_index]
        new_message = model.Message(author_id=user_id,
                                    recipient_id=message['user_id'],
                                    message=message['encoded_message'])
        model.db.session.add(new_message)
    model.db.session.commit()

    return flask.json.jsonify({'success': True, 'error': None})


def VerifyCookies(session_cookie, user_cookie):
    user_id, conv_id = user_cookie.split(":")
    session_cookie_data = session_cookie[conv_id]

    if session_cookie_data != user_cookie:
        return False

    return True


if __name__ == '__main__':
    # Debugger is True so the debug toolbar is present.
    app.add_debug = True

    model.connect_to_db(app)
    # Add the debug toolbar.
    flask_debugtoolbar.DebugToolbarExtension(app)

    app.run(debug=True)
