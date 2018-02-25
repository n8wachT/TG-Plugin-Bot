"""plugin:plugin template"""
# Docstring must be of the format """plugin:<plugin name>""" or plugin will be ignored.
from telegram import ChatAction as Ca
from telegram.ext import CommandHandler

# Load order, higher loads later. For preventing plugin conflicts. Removing this defaults load order to 0.
order = -1

# List of telegram update handlers or [handler, group] lists.
handlers = []


# May include plugins and/or logger arguments to be passed from the bot if needed.
def command(bot, update):
    update.message.chat.send_action(Ca.TYPING)
    update.message.reply_text(text="Template plugin reply.")


handlers.append(CommandHandler('template_command', command))
