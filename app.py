# -*- coding: utf-8 -*-
import os
import time
import logging

import os.path
from commands import start_message, new_acknowledgement, button_callback
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Config vars
token = os.environ["TELEGRAM_TOKEN"]


def error(update, context):
    """Log Errors caused by Updates."""
    print("[ERROR]", context.error)
    raise context.error


def main():
    """
        @AcknowledgedBot commands
        /ack - create a new acknowledgement
        /start, /new, /help - Help message
    """

    def acknowledge_should_be_channel(update, context):
        return new_acknowledgement(update, context, False, False, True)

    def acknowledge(update, context):
        return new_acknowledgement(update, context)
    
    def acknowledge_numbered(update, context):
        return new_acknowledgement(update, context, True)
    
    def acknowledge_optional(update, context):
        return new_acknowledgement(update, context, False, True)
    
    def acknowledge_no_reply(update, context):
        return new_acknowledgement(update, context, False, False, False, True)
    
    def acknowledged_button_callback(update, context):
        return button_callback(update, context)

    # Initialize bot listener
    updater = Updater(token=token, use_context=True)

    # commands
    updater.dispatcher.add_handler(CommandHandler("ack", acknowledge))
    updater.dispatcher.add_handler(
        CommandHandler("acklist", acknowledge_numbered)
    )
    updater.dispatcher.add_handler(
        CommandHandler("ackopt", acknowledge_optional)
    )
    updater.dispatcher.add_handler(
        CommandHandler("ackblank", acknowledge_no_reply)
    )
    updater.dispatcher.add_handler(CommandHandler("start", start_message))
    updater.dispatcher.add_handler(CommandHandler("new", start_message))
    updater.dispatcher.add_handler(CommandHandler("help", start_message))

    updater.dispatcher.add_handler(
        MessageHandler(Filters.command, acknowledge_should_be_channel)
    )

    # Button callback
    updater.dispatcher.add_handler(CallbackQueryHandler(acknowledged_button_callback))

    # Errors
    updater.dispatcher.add_error_handler(error)

    # Start listening
    print("(start) Acknowledged Bot Started", updater.bot)
    updater.start_polling()
    updater.idle()
    

if __name__ == "__main__":
    main()
