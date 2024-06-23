#!/usr/bin/env python
import validators
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

bad_url_text = "Bad url. Please use next format: http://example.com"

# Функция-декоратор для проверки наличия аргументов
def required_argument(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not context.args:
            await update.message.reply_text("This command requires an argument.")
            return
        await func(update, context, *args, **kwargs)
    return wrapper

# Функция-декоратор для проверки, является ли аргумент допустимым URL
def valid_url(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if len(context.args) == 0 or not context.args[0].startswith('http'):
            await update.message.reply_text("Please provide a valid URL.")
            return
        await func(update, context, *args, **kwargs)
    return wrapper

# def required_argument(fn):
#     def wrapper(bot, update, args):
#         if int(len(args)) == 0:
#             bot.sendMessage(chat_id=update.message.chat_id, text=bad_url_text)
#             return False
#         return fn(bot, update, args)
#     return wrapper
# 
# 
# def valid_url(fn):
#     def wrapper(bot, update, args):
#         if not validators.url(args[0], public=True):
#             bot.sendMessage(chat_id=update.message.chat_id, text=bad_url_text)
#             return False
#         return fn(bot, update, args)
#     return wrapper
