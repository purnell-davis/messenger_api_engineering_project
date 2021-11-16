#!/usr/bin/python
'''
Functional test, testing the functionality of messenger_db.py:MessengerDB.
'''

import os
import sqlite3
import tempfile
import unittest

from contextlib import closing

import messenger_db

class BaseDBTestClass(unittest.TestCase):
    '''
    Base TestCase Class for the MessengerDB tests.
    Establishes a shared setUp/tearDown sequence.
        - Test MessengerDB object
        - Test connection to the sqlite DB

        - Close connections to DB.
        - Delete test sqlite file.
    '''

    def setUp(self):
        self.test_db_file = tempfile.mkstemp(prefix='test', suffix='.db')[1]
        self.test_messenger_db = messenger_db.MessengerDB(self.test_db_file)

        self.test_conn = sqlite3.connect(self.test_db_file)

    def tearDown(self):
        self.test_messenger_db.close_db_connection()
        self.test_conn.close()

        os.remove(self.test_db_file)

class Test_create_user_table(BaseDBTestClass):
    '''
    Test the create user table functionality.
    '''

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_table_exists(self):
        '''
        Assert:
            table exists
        '''
        self.test_messenger_db.create_user_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'''SELECT name FROM sqlite_master 
                                 WHERE type='table' AND 
                                       name='{messenger_db.UserTable.TABLE_NAME}';''')
            assert cursor.fetchone() == ('user',)

    def test_table_columns_correct(self):
        '''
        Assert:
            table columns are correct
        '''
        self.test_messenger_db.create_user_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'PRAGMA table_info({messenger_db.UserTable.TABLE_NAME});')
            '''
            PRAGMA table_info(tablename)
                output format:
                   0|col1|TYPE|1||1
                   1|col2|TYPE|1||0
                   2|col3|TYPE|1||0 
            '''
            output = cursor.fetchall()

        expected_output = {'user_id': 'INTEGER',
                           'user_name': 'VARCHAR(50)',
                           'avatar': 'VARCHAR(256)',
                           'created_ts': 'TIMESTAMP'}

        assert {i[1]:i[2] for i in output} == expected_output

class Test_create_chatroom_table(BaseDBTestClass):
    '''
    Test the create chatroom table functionality.
    '''

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_table_exists(self):
        '''
        Assert:
            table exists
        '''
        self.test_messenger_db.create_chatroom_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'''SELECT name FROM sqlite_master 
                                 WHERE type='table' AND 
                                       name='{messenger_db.ChatroomTable.TABLE_NAME}';''')
            assert cursor.fetchone() == ('chatroom',)

    def test_table_columns_correct(self):
        '''
        Assert:
            table columns are correct
        '''
        self.test_messenger_db.create_chatroom_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'PRAGMA table_info({messenger_db.ChatroomTable.TABLE_NAME});')
            '''
            PRAGMA table_info(tablename)
                output format:
                   0|col1|TYPE|1||1
                   1|col2|TYPE|1||0
                   2|col3|TYPE|1||0 
            '''
            output = cursor.fetchall()

        expected_output = {'chatroom_id': 'INTEGER',
                           'chatroom_name': 'VARCHAR(100)',
                           'admin_user_id': 'INTEGER',
                           'created_ts': 'TIMESTAMP'}

        assert {i[1]:i[2] for i in output} == expected_output

class Test_create_message_table(BaseDBTestClass):
    '''
    Test the create message table functionality.
    '''

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_table_exists(self):
        '''
        Assert:
            table exists
        '''
        self.test_messenger_db.create_message_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'''SELECT name FROM sqlite_master 
                                 WHERE type='table' AND 
                                       name='{messenger_db.MessageTable.TABLE_NAME}';''')
            assert cursor.fetchone() == ('message',)

    def test_table_columns_correct(self):
        '''
        Assert:
            table columns are correct
        '''
        self.test_messenger_db.create_message_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'PRAGMA table_info({messenger_db.MessageTable.TABLE_NAME});')
            '''
            PRAGMA table_info(tablename)
                output format:
                   0|col1|TYPE|1||1
                   1|col2|TYPE|1||0
                   2|col3|TYPE|1||0 
            '''
            output = cursor.fetchall()

        expected_output = {'message_id': 'INTEGER',
                           'chatroom_id': 'INTEGER',
                           'sender_user_id': 'INTEGER',
                           'message_str': 'LONGTEXT',
                           'message_media': 'VARCHAR(256)',
                           'message_sent_ts': 'TIMESTAMP',
                           'stored_at_ts': 'TIMESTAMP'}

        assert {i[1]:i[2] for i in output} == expected_output

    def test_table_indices_correct(self):
        '''
        Assert:
            table indices are correct
        '''
        self.test_messenger_db.create_message_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'PRAGMA index_list({messenger_db.MessageTable.TABLE_NAME});')
            '''
            PRAGMA index_list(tablename)
                output format:
                   0|index|0|c|0
            '''
            output = cursor.fetchall()

        expected_output = ['idx_messages_stored_at_ts']
        assert [i[1] for i in output] == expected_output

class Test_create_user2chatroom_table(BaseDBTestClass):
    '''
    Test the create user2chatroom table functionality.
    '''

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_table_exists(self):
        '''
        Assert:
            table exists
        '''
        self.test_messenger_db.create_user2chatroom_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'''SELECT name FROM sqlite_master 
                                 WHERE type='table' AND 
                                       name='{messenger_db.User2ChatroomTable.TABLE_NAME}';''')
            assert cursor.fetchone() == ('user2chatroom',)

    def test_table_columns_correct(self):
        '''
        Assert:
            table columns are correct
        '''
        self.test_messenger_db.create_user2chatroom_table()

        with closing(self.test_conn.cursor()) as cursor:
            cursor.execute(f'PRAGMA table_info({messenger_db.User2ChatroomTable.TABLE_NAME});')
            '''
            PRAGMA table_info(tablename)
                output format:
                   0|col1|TYPE|1||1
                   1|col2|TYPE|1||0
                   2|col3|TYPE|1||0 
            '''
            output = cursor.fetchall()

        expected_output = {'chatroom_id': 'INTEGER',
                           'user_id': 'INTEGER'}

        assert {i[1]:i[2] for i in output} == expected_output

if __name__ == '__main__':
    unittest.main()
