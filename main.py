#!/usr/bin/env python
from telegram.ext import Updater, CommandHandler, Application
from asyncio import Queue
from settings import TELEGRAM_API_KEY, BOTAN_TOKEN
from data import Website
import aiohttp
from decorators import required_argument, valid_url
import ssl
# import botan


help_text = """
The bot ensures that your website was always online. In the case of status changes, the bot will tell you that you need to pay attention to the site. The website is checked for availability every 5 minutes.

Commands:

/help - Help
/list - Show yours added urls
/add <url> - Add new url for monitoring
/del <url> - Remove exist url
/test <url> - Test current status code for url right now

Url format is http[s]://host.zone/path?querystring
For example:

/test https://crusat.ru
"""
# For any issues visit: https://github.com/crusat/telegram-website-monitor/issues
# Contact author: @crusat


async def start(update, context):
    # botan.track(BOTAN_TOKEN, update.message.chat_id, update.message.to_dict(), 'start')
    await update.message.reply_text("Hello!\nThis is telegram bot to check that the site is alive.\n" + help_text)
    # bot.sendMessage(chat_id=update.message.chat_id, text="Hello!\nThis is telegram bot to check that the site is alive.\n%s" % help_text)


async def show_help(update, context):
    # botan.track(BOTAN_TOKEN, update.message.chat_id, update.message.to_dict(), 'help')
    await update.message.reply_text(help_text)
    # bot.sendMessage(chat_id=update.message.chat_id, text="%s" % help_text)


@required_argument
@valid_url
async def add(update, context):
    print('add')
    # botan.track(BOTAN_TOKEN, update.message.chat_id, update.message.to_dict(), 'add')
    print(context.args[0])
    url = context.args[0].lower()
    print(url)
    website_count = (Website.select().where((Website.chat_id == update.message.chat_id) & (Website.url == url)).count())
    print(website_count)
    if website_count == 0:
        website = Website(chat_id=update.message.chat_id, url=url)
        print('ok1')
        website.save(force_insert=True)
        print('ok2')
        await update.message.reply_text(" ".join(["Added", url]))
        # bot.sendMessage(chat_id=update.message.chat_id, text="Added %s" % url)
        print('ok3')
    else:
        await update.message.reply_text(" ".join(["Website", url,  "already exists"]))
        # bot.sendMessage(chat_id=update.message.chat_id, text="Website %s already exists" % url)
    print('end')


@required_argument
async def delete(update, context):
    # botan.track(BOTAN_TOKEN, update.message.chat_id, update.message.to_dict(), 'delete')
    url = context.args[0].lower()
    website = Website.get((Website.chat_id == update.message.chat_id) & (Website.url == url))
    if website:
        website.delete_instance()
        await update.message.reply_text(" ".join(["Deleted", url]))
        # bot.sendMessage(chat_id=update.message.chat_id, text="Deleted %s" % url)
    else:
        await update.message.reply_text(" ".join(["Website", url, "is not exists"]))
        # bot.sendMessage(chat_id=update.message.chat_id, text="Website %s is not exists" % url)


async def url_list(update, context):
    # botan.track(BOTAN_TOKEN, update.message.chat_id, update.message.to_dict(), 'list')
    websites = (Website.select().where(Website.chat_id == update.message.chat_id))
    out = ''
    for website in websites:
        out += "%s (last status code: %s)\n" % (website.url, website.last_status_code)
    if out == '':
        await update.message.reply_text(" ".join(["List empty"]))
        # bot.sendMessage(chat_id=update.message.chat_id, text="List empty")
    else:
        await update.message.reply_text(out)
        # bot.sendMessage(chat_id=update.message.chat_id, text="%s" % out)


@required_argument
@valid_url
async def test(update, context):
    # botan.track(BOTAN_TOKEN, update.message.chat_id, update.message.to_dict(), 'test')
    url = context.args[0].lower()
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession() as session:
            async with session.head(url, ssl=ssl_context, allow_redirects=True) as response:
                text = str()
                if response.status == 200:
                    text = " ".join(["Url", url, "is alive (status code 200)"])
                    # bot.sendMessage(chat_id=update.message.chat_id, text="Url %s is alive (status code 200)" % url)
                else:
                    text = " ".join(["Status code of url", url, "is", str(response.status)])

                if response.history:
                    redirects = [f"{index + 1}: {resp.url}" for index, resp in enumerate(response.history)]
                    text += f"\n\nRedirects:\n" + "\n".join(redirects)
                await update.message.reply_text(text)
                    # bot.sendMessage(chat_id=update.message.chat_id, text="Status code of url %s is %s" % (url, r.status_code))
    except Exception as e:
        await update.message.reply_text(" ".join(["Error for url", url, '-', str(e)]))
        # bot.sendMessage(chat_id=update.message.chat_id, text="Error for url %s" % url)


app = Application.builder().token(TELEGRAM_API_KEY).build()
# updater = Updater(TELEGRAM_API_KEY, update_queue)
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler("add", add))
app.add_handler(CommandHandler("del", delete))
app.add_handler(CommandHandler("list", url_list))
app.add_handler(CommandHandler("test", test))
app.add_handler(CommandHandler("help", show_help))

print('Telegram bot started')

app.run_polling()
# updater.start_polling()
# updater.idle()
