#!/usr/bin/python
'''
Functional test, testing the functionality of messenger_app.py.
'''

import os
import json
import sqlite3
import tempfile
import unittest

from contextlib import closing

import messenger_db
import messenger_app

class Test_store_messages(unittest.TestCase):

    def setUp(self):
        self.test_db_file = tempfile.mkstemp(prefix='test', suffix='.db')[1]
        messenger_app._MESSENGER_DB = messenger_db.MessengerDB(self.test_db_file)
        self.test_conn = sqlite3.connect(self.test_db_file)
        self.test_conn.row_factory = sqlite3.Row

    def tearDown(self):
        self.test_conn.close()

        os.remove(self.test_db_file)

    def test_no_payload_error_response(self):
        '''
        Assert:
            400 Response
            No JSON Input Error Message
        '''
        with messenger_app.APP.test_client() as test_client:
            response = test_client.post('/chatrooms/5/messages')
            self.assertEqual(response.status_code, 400)
            self.assertEqual("No JSON Input Provided.", response.get_json()['errors'][0])

    def test_bad_payload_error_response(self):
        '''
        Assert:
            400 Response
            No JSON Input Error Message
        '''
        with messenger_app.APP.test_client() as test_client:
            response = test_client.post('/chatrooms/5/messages',
                                        data=json.dumps({}),
                                        content_type='application/json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual('Bad Input. Malformed JSON Input.', response.get_json()['errors'][0])

    def test_messages_stored(self):
        '''
        Assert:
            Message stored correctly
        '''
        test_messages_input = [
                                {
                                    'message_str': 'hello world!',
                                    'message_sent_ts': 1637029263,
                                    'sender_user_id': 10
                                },
                                {
                                    'message_str': 'goodnight earth!',
                                    'message_sent_ts': 1637029963,
                                    'sender_user_id': 4
                                },
                              ]

        test_chatroom_id = 5
        with messenger_app.APP.test_client() as test_client:
            response = test_client.post(f'/chatrooms/{test_chatroom_id}/messages',
                                        data=json.dumps({'data': test_messages_input}),
                                        content_type='application/json')

        self.assertEqual(response.status_code, 200)
    
        self.assertEqual([{'message_id': 1}, {'message_id': 2}], response.get_json()['data'])

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'SELECT * FROM {messenger_db.MessageTable.TABLE_NAME}')
            rows = cursor.fetchall()

        for index, row in enumerate(rows):
            row_dict = messenger_db.MessengerDB.row2dict(row)
            test_message = test_messages_input[index]
            self.assertEqual(row_dict['chatroom_id'], test_chatroom_id)
            self.assertEqual(row_dict['message_str'], test_message['message_str'])
            self.assertEqual(row_dict['message_sent_ts'], test_message['message_sent_ts'])
            self.assertEqual(row_dict['sender_user_id'], test_message['sender_user_id'])

if __name__ == '__main__':
    unittest.main()
