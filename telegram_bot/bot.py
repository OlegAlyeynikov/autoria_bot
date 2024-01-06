import asyncio
from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode

telegram_token = '6659226520:AAFeY5Hh2RfWnWzEAW-5eM4MX-HL8RihI7o'


async def main_bot():
    bot = Bot(telegram_token)
    async with bot:
        updates = (await bot.get_updates())[0]
        message = updates.message  # Assuming there is a message in updates
        chat_id = message.chat.id
        return chat_id


async def send_message(chat_id, message):
    bot = Bot(telegram_token)
    async with bot:
        await bot.send_message(text=message, chat_id=chat_id)


async def send_message_each_10_minutes(
        chat_id, photo_url1, photo_url2, photo_url3, car_name, price, car_url, text, auction_url=None):
    bot = Bot(telegram_token)
    photo_urls = [photo_url1, photo_url2, photo_url3]
    async with bot:
        media = [
            InputMediaPhoto(
                media=photo_url
            ) for photo_url in photo_urls
        ]

        caption = f"{text}\n{car_name}\nPrice: {price}\nCar URL: {car_url}"
        if auction_url:
            caption = caption + f"\nAuction URL: {auction_url}"

        await bot.send_media_group(chat_id, media, caption=caption, parse_mode=ParseMode.HTML)
