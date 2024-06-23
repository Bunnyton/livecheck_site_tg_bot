#!/usr/bin/env python
import asyncio
import aiohttp
import telegram
from settings import TELEGRAM_API_KEY
from data import Website
import ssl

# Загрузка API ключа Telegram и настройка бота
bot = telegram.Bot(token=TELEGRAM_API_KEY)

# Функция для проверки статуса веб-сайтов
async def check_website(website, ssl_context):
    url = website.url

    status_code = 0
    text = str()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, ssl=ssl_context, allow_redirects=True) as response:
                status_code = response.status

                if response.history:
                    redirects = [f"{index + 1}: {resp.url}" for index, resp in enumerate(response.history)]
                    text += f"\n\nRedirects:\n" + "\n".join(redirects)

    except aiohttp.ClientError as e:
        status_code = -1
        text += '\n' + str(e)
    
    # Проверка изменения статуса и отправка сообщения в Telegram, если он изменился
    if status_code != website.last_status_code:
        website.last_status_code = status_code
        website.save()
        await bot.send_message(chat_id=website.chat_id,
                       text=f"Status code changed for {website.url}. Current is {status_code}.{text}")

# Асинхронная функция для проверки всех веб-сайтов
async def main():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    websites = Website.select()
    tasks = [check_website(website, ssl_context) for website in websites]
    await asyncio.gather(*tasks)

# Запуск основной асинхронной функции
if __name__ == "__main__":
    asyncio.run(main())