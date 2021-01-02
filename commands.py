import logging
import threading
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from dateutil import relativedelta as rdelta



def start_message(update, context):
    """Initial start/help message when calling /help or /start"""
    update.message.reply_text(
        'Hello! I\'m AcknowledgedBot.\n\nTo make announcements, add me to a group (@AcknowledgedBot) and type "/ack [your announcement here]."\n\nIf you find any bugs or suggestions, please message @ackbotsupport.'
    )


def about_message(update, context):
    """Initial start/help message when calling /help or /start"""
    update.message.reply_text(
        'AcknowledgedBot was built to reduce the clutter in large group chats. It was built in 2017, and is open source https://github.com/lowewenzel/acknowledged-bot.'
    )


def gen_user_name(from_user):
    """from_user has username or full_name"""
    if from_user.username:
        new_name = from_user.full_name + " (@" + from_user.username + ")"
    else:
        new_name = from_user.full_name

    return new_name

def new_acknowledgement(
    update,
    context,
    numbered=False,
    optional=False,
    should_be_channel=False,
    no_reply=False,
):
    """Create acknowledgement message for bot"""

    is_channel = update._effective_chat.type == "channel"

    # Add a "Acknowledge" button, add to reply markup
    keyboard = [[InlineKeyboardButton("Acknowledge", callback_data="1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if is_channel:
        channel_post = update.channel_post

        if " " not in channel_post.text:
            return

        full_text = channel_post.text.split(" ", 1)

        text_command = full_text[0].split("@")[0]
        effective_message = full_text[1]

        message = ""

        if text_command == "/ackopt":
            message = effective_message + "\n\n---------------\nAcknowledged Opt-In:\n"
        elif text_command == "/acklist":
            message = effective_message + "\n\n---------------\nAcknowledged List:\n"
        elif text_command == "/ack":
            message = effective_message + "\n\n---------------\nAcknowledged:\n"
        else:
            return

        channel_post.edit_text(message, reply_markup=reply_markup)
        return
    elif should_be_channel:
        return

    # If there is no space, return
    if " " not in update.message.text:
        return

    # Split the input message by first space
    announcement = update.message.text_markdown.split(" ", 1)[1]
    if numbered:
        final_response = (
            "\n" + announcement + "\n\n---------------\nAcknowledged List:\n"
        )
    elif optional:
        final_response = (
            "\n" + announcement + "\n\n---------------\nAcknowledged Opt-In:\n"
        )
    else:
        final_response = "\n" + announcement + "\n\n---------------\nAcknowledged:\n"

    if no_reply:
        update.effective_chat.send_message(
            final_response, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )
    else:
        # Send final message reply
        update.message.reply_text(
            final_response, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    return

def button_callback(update, context):
    """Called when user presses Acknowledge Button"""
    # Callback query containing all meta data
    query = update.callback_query
    from_user = query.from_user

    is_list = "Acknowledged List" in query.message.text
    previous_number = 0

    if is_list:
        last_line = query.message.text.split("\n")[-1]
        previous_number_str = last_line.split(".")[0]
        try:
            previous_number = int(previous_number_str)
        except ValueError:
            previous_number = 0

    # New name
    new_name = gen_user_name(from_user)

    # Add Ack button
    ackd_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Acknowledge", callback_data="2")]]
    )

    # Check if already acknowledged
    if new_name in query.message.text or (" " + new_name) in query.message.text:
        if "Opt-In" in query.message.text:
            str_text_arr = query.message.text.split("\n")
            str_text_arr.remove("- " + new_name)
            new_text = "\n".join(str_text_arr)

            # Update the message contents
            context.bot.edit_message_text(
                reply_markup=ackd_markup,
                chat_id=query.message.chat_id,
                message_id=query.message.message_id,
                text=new_text,
            )
        query.answer()
    # Add acknowledgement
    else:
        if is_list:
            new_text = (
                query.message.text + "\n" + str(previous_number + 1) + ". " + new_name
            )
        else:
            new_text = query.message.text + "\n- " + new_name

        # Update the message contents
        context.bot.edit_message_text(
            reply_markup=ackd_markup,
            chat_id=query.message.chat_id,
            message_id=query.message.message_id,
            text=new_text,
        )
        query.answer()

    return
