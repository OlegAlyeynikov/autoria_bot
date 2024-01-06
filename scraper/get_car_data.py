import asyncio
import requests
import sqlite3
from telegram_bot.bot import send_message_each_10_minutes

search_url = ('https://auto.ria.com/api/search/auto?indexName=auto%2Corder_auto%2Cnewauto_search&category_id=1'
              '&marka_id[0]=79&model_id[0]=2104&abroad=2&custom=1&page=1&countpage=60&with_feedback_form=1'
              '&withOrderAutoInformer=1&with_last_id=1')
ria_url = 'https://auto.ria.com'


def get_missing_car_data(ids_list, cursor, connection, chat_id):
    cursor.execute('''SELECT id FROM Car''')
    all_unique_ids = [row[0] for row in cursor.fetchall()]
    first_set = set(map(str, ids_list))
    result_ids = [str(id) for id in all_unique_ids if str(id) not in first_set]
    if result_ids:
        for id_ in result_ids:
            cursor.execute('''
                    SELECT photo1_url, photo2_url, photo3_url, brand, price, auto_ria_link, auction_photo_link
                    FROM Car
                    WHERE id = ?
                ''', (id_,))

            car_data = cursor.fetchone()
            text = "This car was purchased and is no longer available on the AutoRia site!"
            if car_data:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(send_message_each_10_minutes(
                    chat_id, car_data[0], car_data[1], car_data[2], car_data[3], car_data[4], car_data[5], text, car_data[6]
                ))
            cursor.execute('''
                    UPDATE Car
                    SET sold = 1
                    WHERE id = ?
                ''', (id_,))

            connection.commit()


def check_if_price_was_changed(chat_id, cursor, shop_ids, connection):
    cursor.execute('''
            SELECT id, price
            FROM Car
        ''')
    db_prices = cursor.fetchall()
    for db_id, db_price in db_prices:

        if str(db_id) in shop_ids:
            car_url = f"https://auto.ria.com/uk/bu/blocks/json/3537/353679/{db_id}?lang_id=4"
            resp = requests.get(car_url)
            if resp.status_code == 200:
                car_data = resp.json()
                price = car_data["USD"]
                if db_price != price:
                    cursor.execute('''
                                        SELECT photo1_url, photo2_url, photo3_url, brand, price, auto_ria_link, auction_photo_link
                                        FROM Car
                                        WHERE id = ?
                                    ''', (db_id,))

                    car_data = cursor.fetchone()
                    text = "Please note the price for this car has been changed!"
                    loop = asyncio.get_event_loop()
                    loop.run_until_complete(send_message_each_10_minutes(chat_id, car_data[0], car_data[1], car_data[2], car_data[3], price, car_data[5], text, car_data[6]))
                    cursor.execute('''
                                        UPDATE Car
                                        SET price = ?
                                        WHERE id = ?
                                    ''', (price, db_id,))

                    connection.commit()
            else:
                # Handle the error
                print(f"Request failed with status code: {resp.status_code}")


def make_request_and_update_database(chat_id):
    connection = sqlite3.connect("auto_ria.db")
    cursor = connection.cursor()
    response = requests.get(search_url)

    if response.status_code == 200:
        cars_data = response.json()
        ids_list = cars_data["result"]["search_result"]["ids"]
        get_missing_car_data(ids_list, cursor, connection, chat_id)
        check_if_price_was_changed(chat_id, cursor, ids_list, connection)
        for id_ in ids_list:
            cursor.execute('''
                SELECT id FROM Car
                WHERE id = ?
            ''', (id_,))
            result = cursor.fetchone()
            if result is None:
                car_url = f"https://auto.ria.com/uk/bu/blocks/json/3537/353679/{id_}?lang_id=4"
                resp = requests.get(car_url)
                if resp.status_code == 200:
                    car_data = resp.json()
                    car_name = car_data["title"]
                    price = car_data["USD"]
                    car_url = ria_url + car_data["linkToView"]
                    mark_name = car_data["markNameEng"]
                    model_name = car_data["modelNameEng"]
                    photo_data = car_data["photoData"]["all"]
                    photo_url1 = f"https://cdn3.riastatic.com/photosnew/auto/photo/{mark_name}_{model_name}__{photo_data[0]}m.jpg"
                    photo_url2 = f"https://cdn3.riastatic.com/photosnew/auto/photo/{mark_name}_{model_name}__{photo_data[1]}m.jpg"
                    photo_url3 = f"https://cdn3.riastatic.com/photosnew/auto/photo/{mark_name}_{model_name}__{photo_data[2]}m.jpg"

                    loop = asyncio.get_event_loop()
                    text = "Please consider this car for purchase:"
                    loop.run_until_complete(send_message_each_10_minutes(
                        chat_id, photo_url1, photo_url2, photo_url3, car_name, price, car_url, text))

                    cursor.execute("INSERT INTO Car ("
                                   "id, photo1_url, photo2_url, photo3_url, brand, price, auto_ria_link, sold"
                                   ") VALUES (?, ?, ?, ?, ?, ?, ?, ?"
                                   ")", (id_, photo_url1, photo_url2, photo_url3, car_name, price, car_url, False,))
                    connection.commit()
                    connection.close()
                    return
                else:
                    # Handle the error
                    print(f"Request failed with status code: {resp.status_code}")
        connection.close()
        return
    else:
        # Handle the error
        print(f"Request failed with status code: {response.status_code}")
