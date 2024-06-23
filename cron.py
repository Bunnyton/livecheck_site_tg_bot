#!/usr/bin/env python
import asyncio
import aiohttp
import telegram
from settings import TELEGRAM_API_KEY
from data import Website
import ssl
import time

# Загрузка API ключа Telegram и настройка бота
bot = telegram.Bot(token=TELEGRAM_API_KEY)


async def is_internet_available():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.google.com', timeout=3):
                return True
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False


async def check_website(website):
    url = website.url

    status_code = 0
    text = str()
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession() as session:
            async with session.head(url, ssl=ssl_context, allow_redirects=True) as response:
                status_code = response.status

                if response.history:
                    redirects = [f"{index + 1}: {resp.url}" for index, resp in enumerate(response.history)]
                    text += f"\n\nRedirects:\n" + "\n".join(redirects)

    except aiohttp.ClientError as e:
        if is_internet_available():
            status_code = -1
            text += '\n' + str(e)
        else:
            return
    except Exception as e:
        print(str(e))
        return
    
    if status_code != website.last_status_code:
        website.last_status_code = status_code
        website.save()
        try:
            if website.message_thread_id != 0:
                await bot.send_message(chat_id=website.chat_id, message_thread_id=website.message_thread_id,
                               text=f"Status code changed for {website.url}. Current is {status_code}.{text}")
            else:
                await bot.send_message(chat_id=website.chat_id,
                               text=f"Status code changed for {website.url}. Current is {status_code}.{text}")
        except Exception as e:
            print("Send message ERROR")


async def main():
    websites = Website.select()
    tasks = [check_website(website) for website in websites]
    await asyncio.gather(*tasks)

# Запуск основной асинхронной функции
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(main())
        time.sleep(10)
