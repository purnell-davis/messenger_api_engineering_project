'''
Entry point function controller for messenger REST API app.
'''
import os
from flask import Flask, request, jsonify

import messenger_db

APP = Flask(__name__)

_MESSENGER_DB = None
def _messenger_db():
    '''
    Factory method to control when DB is initialized.
    '''
    global _MESSENGER_DB

    if _MESSENGER_DB is None:
        _MESSENGER_DB = messenger_db.MessengerDB()

    return _MESSENGER_DB

@APP.route("/chatrooms/<chatroom_id>/messages", methods=['POST'])
def store_messages(chatroom_id):
    '''
    Store messages on given chatroom.

    JSON Input Payload:
        {
            message_str: string
            message_sent_ts: int(timestamp)
            sender_user_id: int
        }
    '''
    APP.logger.debug(f'chatroom_id: {chatroom_id}')

    input_json_payload = request.get_json()
    APP.logger.debug(f'JSON Payload: {input_json_payload}')

    try:
        messages = input_json_payload['data']
    except TypeError:
        APP.logger.error("Expected JSON input Payload")
        return jsonify({'errors': ['No JSON Input Provided.']}), 400
    except KeyError:
        APP.logger.error("Expected 'data' key in input JSON payload.")
        return jsonify({'errors': ['Bad Input. Malformed JSON Input.']}), 400

    #@TODO: input sanitation/validation
    #@TODO: convert ts to datetime()

    for msg in messages:
        msg['chatroom_id'] = chatroom_id

    APP.logger.debug(messages)

    message_ids = _messenger_db().insert_message_rows(messages)

    return jsonify({'data': [{'message_id': message_id} for message_id in message_ids]}), 200


# all for particular chatroom
# @APP.route("/chatrooms/<chatroom_id>/messages", methods=['GET'])

# all messages from a particular SENDER in a particular chatroom
# @APP.route("/chatrooms/<chatroom_id>/messages/<sender_user_id>", methods=['GET'])

#@TODO: would like to implement pagination
#       https://phauer.com/2015/restful-api-design-best-practices/#keyset-based-pagination-aka-continuation-token-cursor

if __name__ == "__main__":
    APP.run()
