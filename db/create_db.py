import sqlite3


def create_db():
    connection = sqlite3.connect("auto_ria.db")
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Car (
            id INTEGER PRIMARY KEY,
            photo1_url TEXT,
            photo2_url TEXT,
            photo3_url TEXT,
            brand TEXT NOT NULL,
            price INTEGER NOT NULL,
            auto_ria_link TEXT NOT NULL,
            auction_photo_link TEXT,
            sold BOOLEAN NOT NULL
        )
    ''')

    connection.commit()
    connection.close()
