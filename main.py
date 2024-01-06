import asyncio
import time
from db.create_db import create_db
from scraper.get_car_data import make_request_and_update_database

from telegram_bot.bot import main_bot


def main():
    create_db()
    loop = asyncio.get_event_loop()
    chat_id = loop.run_until_complete(main_bot())

    while True:
        try:
            make_request_and_update_database(chat_id)
            time.sleep(3600)  # 10 minutes interval
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
