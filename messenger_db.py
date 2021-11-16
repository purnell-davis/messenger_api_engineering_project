'''
Functionality to interact with the Messenger Database.
'''

import os
import sqlite3

from contextlib import closing

MESSENGER_DB_SQLITE_FILE = os.environ.get('MESSENGER_DB_SQLITE_FILE', 'messenger_app.db')

class UserTable():
    '''
    Object representing the user table.
    Retains the user SQL commands to interact with the table.
    '''
    TABLE_NAME = 'user'

    CREATE_TABLE_SQL = f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                               user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               user_name VARCHAR(50) NOT NULL,
                               avatar VARCHAR(256),
                               created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           );'''

    INSERT_USER_BY_NAME_SQL = f'''INSERT INTO {TABLE_NAME}(user_name)
                                      VALUES (?)'''

class ChatroomTable():
    '''
    Object representing the chatroom table.
    Retains the user SQL commands to interact with the table.
    '''
    TABLE_NAME = 'chatroom'

    CREATE_TABLE_SQL = f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                               chatroom_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               chatroom_name VARCHAR(100) NOT NULL,
                               admin_user_id INTEGER,
                               created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY (admin_user_id) REFERENCES user (user_id) 
                                       ON UPDATE NO ACTION
                           );'''

    INSERT_CHATROOM_SQL = f'''INSERT INTO {TABLE_NAME}(chatroom_name, admin_user_id)
                                  VALUES (?, ?)'''

class MessageTable():
    '''
    Object representing the message table.
    Retains the user SQL commands to interact with the table.
    '''
    TABLE_NAME = 'message'

    CREATE_TABLE_SQL = f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                               message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                               chatroom_id INTEGER NOT NULL,
                               sender_user_id INTEGER NOT NULL,
                               message_str LONGTEXT NOT NULL,
                               message_media VARCHAR(256),
                               message_sent_ts TIMESTAMP NOT NULL,
                               stored_at_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY (chatroom_id) REFERENCES chatroom (chatroom_id) 
                                       ON DELETE CASCADE ON UPDATE NO ACTION,
                               FOREIGN KEY (sender_user_id) REFERENCES user (user_id)
                                       ON UPDATE NO ACTION
                           );'''

    CREATE_INDEX_SQL = f'''CREATE INDEX idx_messages_stored_at_ts
                               ON {TABLE_NAME} (stored_at_ts);'''

    INSERT_MESSAGE_KEYS = ('chatroom_id',
                           'sender_user_id',
                           'message_str',
                           'message_sent_ts')

    SELECT_MESSAGE_QUERY_KEYS = ('message_id',
                                 'chatroom_id',
                                 'sender_user_id',
                                 'message_str',
                                 'message_sent_ts',
                                 'stored_at_ts')

    INSERT_MESSAGE_SQL = f'''INSERT INTO {TABLE_NAME} (%s, %s, %s, %s)
                                 VALUES (?, ?, ?, ?)''' % (INSERT_MESSAGE_KEYS)

    ALL_MESSAGES_SQL = '''SELECT (%s, %s, %s, %s, %s, %s) FROM {TABLE_NAME}
                            WHERE message_sent_ts > datetime('now', '-30 days')
                            LIMIT 100''' % (SELECT_MESSAGE_QUERY_KEYS)

    ALL_MESSAGES_IN_CHATROOM_SQL = \
        '''SELECT (%s, %s, %s, %s, %s, %s) FROM {TABLE_NAME}
             WHERE chatroom_id=? AND
                   message_sent_ts > datetime('now', '-30 days')
             LIMIT 100''' % (SELECT_MESSAGE_QUERY_KEYS)

    ALL_MESSAGES_IN_CHATROOM_FROM_SENDER_SQL = \
        '''SELECT (%s, %s, %s, %s, %s, %s) FROM {TABLE_NAME}
             WHERE chatroom_id=? AND
                   sender_user_id=? AND
                   message_sent_ts > datetime('now', '-30 days')
             LIMIT 100''' % (SELECT_MESSAGE_QUERY_KEYS)

    ALL_MESSAGES_IN_CHATROOM_SINCE_SQL = \
        '''SELECT (%s, %s, %s, %s, %s, %s) FROM {TABLE_NAME}
             WHERE chatroom_id=? AND
                   message_sent_ts > datetime('now', '-30 days') AND
                   message_sent_ts > datetime(?)
           LIMIT 100;'''

    #@TODO: Allow DB and Table to store emojis
    #  https://stackoverflow.com/questions/39463134/how-to-store-emoji-character-in-mysql-database

class User2ChatroomTable():
    '''
    Object representing the user2chatroom table.
    Retains the user SQL commands to interact with the table.
    '''
    TABLE_NAME = 'user2chatroom'

    CREATE_TABLE_SQL = f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
                               chatroom_id INTEGER NOT NULL,
                               user_id INTEGER NOT NULL,
                               PRIMARY KEY (chatroom_id, user_id),
                               FOREIGN KEY (chatroom_id) REFERENCES chatroom (chatroom_id) 
                                       ON DELETE CASCADE ON UPDATE NO ACTION,
                               FOREIGN KEY (user_id) REFERENCES user (user_id) 
                                       ON DELETE CASCADE ON UPDATE NO ACTION
                           );'''

    INSERT_USER_TO_CHATROOM_REL_SQL = f'''INSERT INTO {TABLE_NAME}(chatroom_id, user_id)
                                              VALUES (?, ?)'''

    ALL_USERS_IN_CHATROOM = f'''SELECT user_id FROM {TABLE_NAME}
                                    WHERE chatroom_id=?'''

class MessengerDB():
    '''
    Object representing the Messenger Database.
    Provides functionality to Read/Write data in the DB.
    '''
    def __init__(self, sqlite_db_file=MESSENGER_DB_SQLITE_FILE):
        self.sqlite_db_file = sqlite_db_file
        self.connection = self.open_db_connection()

        self.create_user_table()
        self.create_chatroom_table()
        self.create_message_table()
        self.create_user2chatroom_table()

    def open_db_connection(self):
        '''
        Create a connection to the sqlite DB.
        '''
        conn = sqlite3.connect(self.sqlite_db_file, detect_types=sqlite3.PARSE_DECLTYPES |
                                                                 sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row

        return conn

    def close_db_connection(self):
        '''
        Close connection to DB.
        '''
        self.connection.close()

    @classmethod
    def row2dict(cls, row):
        '''
        Convert row obj to dict.
        '''
        return {key: row[key] for key in row.keys()}

    def _execute_commit(self, sql_str, *args):
        '''
        Commit a command in the DB.
        '''
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute(sql_str, args)
                self.connection.commit()
        except sqlite3.Error as error:
            #@TODO: handle exception appropriately
            print("Failed to insert data into sqlite table", error)

    def _executemany_commit(self, sql_str, rows_data):
        '''
        Commit a command in the DB.
        '''
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.executemany(sql_str, rows_data)
                self.connection.commit()
        except sqlite3.Error as error:
            #@TODO: handle exception appropriately
            print("Failed to insert data into sqlite table", error)

    def _execute_insert_commit(self, sql_str, args):
        '''
        Commit an insertion command on the DB.
        Returns:
            int, inserted row id
        '''
        try:
            with closing(self.connection.cursor()) as cursor:
                cursor.execute(sql_str, args)
                self.connection.commit()
                return cursor.lastrowid
        except sqlite3.Error as error:
            #@TODO: handle exception appropriately
            print("Failed to insert data into sqlite table", error)

        return None

    def create_user_table(self):
        '''
        Create user table.
        '''
        self._execute_commit(UserTable.CREATE_TABLE_SQL)

    def create_chatroom_table(self):
        '''
        Create chatroom table.
        '''
        self._execute_commit(ChatroomTable.CREATE_TABLE_SQL)

    def create_message_table(self):
        '''
        Create message table.
        '''
        self._execute_commit(MessageTable.CREATE_TABLE_SQL)
        self._execute_commit(MessageTable.CREATE_INDEX_SQL)

    def create_user2chatroom_table(self):
        '''
        Create user2chatroom table.
        '''
        self._execute_commit(User2ChatroomTable.CREATE_TABLE_SQL)

    def insert_user_row(self, username, avatar_url=None):
        '''
        Create new user row.

        Params:
            username str: name of user
            avatar_url str: [optional] url to avatar image.
        '''
        #@TODO: add functionality for avatar
        return self._execute_insert_commit(UserTable.INSERT_USER_BY_NAME_SQL, (username,))

    def insert_chatroom_row(self, chatroom_name, admin_user_id):
        '''
        Create new chatroom row.

        Params:
            chatroom_name str: name of the chatroom
            admin_user_id int: id of user who created chatroom
        '''
        chatroom_id = self._execute_insert_commit(
            ChatroomTable.INSERT_CHATROOM_SQL, (chatroom_name, admin_user_id))

        self.add_users_to_chatroom(chatroom_id, [admin_user_id])

        return chatroom_id

    def add_users_to_chatroom(self, chatroom_id, user_ids):
        '''
        Create new chatroom row.

        Params:
            chatroom_id int: ID of chatroom to add users to
            user_ids list[int]: ids of users to add to chatroom
        '''
        chatroom_to_users = [(chatroom_id, user_id) for user_id in user_ids]

        return self._executemany_commit(
            User2ChatroomTable.INSERT_USER_TO_CHATROOM_REL_SQL, chatroom_to_users)

    def insert_message_rows(self, messages):
        '''
        Create new message row

        Params:
            messages list[{}]: list of dictionary messages
                message dict:
                    chatroom_id int, chatroom that message corresponds to
                    sender_user_id int, user id of sender of message
                    message_str str, message string content
                    message_sent_ts int[timestamp], time the message was sent from the client
                                                    perspective.
        '''
        message_ids = []
        for message in messages:
            message_vals = tuple([message[key] for key in MessageTable.INSERT_MESSAGE_KEYS])
            message_ids.append(
                self._execute_insert_commit(MessageTable.INSERT_MESSAGE_SQL, message_vals))

        return message_ids
