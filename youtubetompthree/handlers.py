import logging
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest

from youtubetompthree import youtubeconverter

logger = logging.getLogger(__name__)

SONGS = {}


def vote_song(bot, update):
    query = update.callback_query
    message_id = query.message.message_id
    user_voting = query.from_user.id

    if message_id not in SONGS:
        SONGS[message_id] = {
            "thumbs_up": 0,
            "thumbs_down": 0,
            "have_voted": []
        }

    if user_voting not in SONGS[message_id]["have_voted"]:
        if query.data == 'thumbs_up':
            SONGS[message_id]['thumbs_up'] += 1
        elif query.data == 'thumbs_down':
            SONGS[message_id]['thumbs_down'] += 1
        SONGS[message_id]['have_voted'].append(user_voting)

        votes_up = SONGS[message_id]['thumbs_up']
        votes_down = SONGS[message_id]['thumbs_down']

        keyboard = [
            [
                InlineKeyboardButton(f"👍 {votes_up if votes_up else ''}", callback_data='thumbs_up'),
                InlineKeyboardButton(f"👎 {votes_down if votes_down else ''}", callback_data='thumbs_down')
            ]
        ]
        query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        query.answer()


def youtube_links(bot, update):
    update_type = update.message or update.channel_post

    video_info = youtubeconverter.extract_info(update_type.text)
    restricted_title = youtubeconverter.get_restricted_filename(video_info['title'])

    try:
        file = open(f'audio/{restricted_title}.mp3', 'rb')
    except FileNotFoundError:
        video_info = youtubeconverter.convert_video(update_type.text)
        file = open(f'audio/{restricted_title}.mp3', 'rb')
    finally:
        keyboard = [
            [
                InlineKeyboardButton("👍", callback_data='thumbs_up'),
                InlineKeyboardButton("👎", callback_data='thumbs_down')
            ]
        ]
        bot.sendAudio(
            chat_id=update_type.chat_id,
            audio=file,
            title=video_info['title'],
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        file.close()

    try:
        bot.deleteMessage(
            chat_id=update_type.chat_id,
            message_id=update_type.message_id
        )
    except BadRequest:
        # Probably message that can not be deleted
        pass
