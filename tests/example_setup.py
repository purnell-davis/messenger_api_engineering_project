#!/usr/local/bin/python3

import sqlite3
import datetime
import messenger_db

from contextlib import closing

TEST_DB_FILE = 'example.db'

def drop_tables():
    '''
    Start Fresh, drop all tables.
    '''
    TEST_CONN = sqlite3.connect(TEST_DB_FILE)
    with closing(TEST_CONN.cursor()) as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS {messenger_db.User2ChatroomTable.TABLE_NAME}')
        cursor.execute('DROP INDEX IF EXISTS idx_messages_stored_at_ts')
        cursor.execute(f'DROP TABLE IF EXISTS {messenger_db.MessageTable.TABLE_NAME}')
        cursor.execute(f'DROP TABLE IF EXISTS {messenger_db.UserTable.TABLE_NAME}')
        cursor.execute(f'DROP TABLE IF EXISTS {messenger_db.ChatroomTable.TABLE_NAME}')

        TEST_CONN.commit()
    
    TEST_CONN.close()

def main():
    '''
    Entry point function.
    '''
    drop_tables()

    msg_db = messenger_db.MessengerDB(sqlite_db_file=TEST_DB_FILE)

    user_ids = []
    user_ids.append(msg_db.insert_user_row('aaron'))
    user_ids.append(msg_db.insert_user_row('betty'))
    user_ids.append(msg_db.insert_user_row('carol'))

    admin_user_id = user_ids[0]

    chatroom_id = msg_db.insert_chatroom_row('my chatroom', admin_user_id)

    msg_db.add_users_to_chatroom(chatroom_id, user_ids[1:])

    messages = [
                 {'chatroom_id': 1,
                  'sender_user_id': 1,
                  'message_str': 'hello',
                  'message_sent_ts': datetime.datetime(2021, 1, 10, 13, 1, 10),
                 },
                 {'chatroom_id': 1,
                  'sender_user_id': 2,
                  'message_str': 'hi. how are you?',
                  'message_sent_ts': datetime.datetime(2021, 1, 10, 13, 1, 10),
                 },
                 {'chatroom_id': 1,
                  'sender_user_id': 1,
                  'message_str': 'im well',
                  'message_sent_ts': datetime.datetime(2021, 1, 10, 13, 1, 10),
                 },
                 {'chatroom_id': 1,
                  'sender_user_id': 1,
                  'message_str': 'how r u?',
                  'message_sent_ts': datetime.datetime(2021, 1, 10, 13, 1, 10),
                 },
                 {'chatroom_id': 1,
                  'sender_user_id': 2,
                  'message_str': 'great!',
                  'message_sent_ts': datetime.datetime(2021, 1, 10, 13, 1, 10),
                 },
               ]

    msg_db.insert_message_rows(messages)

if __name__ == '__main__':
    main()
