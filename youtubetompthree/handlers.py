import time

import logging
import telegram
import youtube_dl
from pydub import AudioSegment
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest

from youtubetompthree import youtubeconverter
from youtubetompthree.db import user_has_voted, get_song_votes, get_or_create_song, \
    add_vote_to_song
from youtubetompthree.utils import get_or_download_video, process_description, \
    cut_audio_and_save

logger = logging.getLogger(__name__)


def download_audio(bot, update):
    update_type = update.message or update.channel_post

    video_info = youtubeconverter.convert_video(update_type.text, download=False)
    restricted_title = youtubeconverter.get_restricted_filename(video_info['title'])

    file_location = get_or_download_video(restricted_title, update_type.text)

    try:
        with open(file_location, 'rb') as fd:
            bot.sendAudio(
                chat_id=update_type.chat_id,
                audio=fd,
                title=video_info['title'],
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton("👍", callback_data='like'),
                        InlineKeyboardButton("👎", callback_data='dislike')
                    ]
                ])
            )
    except telegram.error.TimedOut:
        logger.info('Telegram is taking too long..raised an TimedOut exception. Catched.')

    try:
        bot.deleteMessage(
            chat_id=update_type.chat_id,
            message_id=update_type.message_id
        )
    except BadRequest:
        # Probably a message that can not be deleted
        pass


def vote_song(bot, update):
    query = update.callback_query
    message_id = query.message.message_id
    chat_id = query.chat_id
    user_id = query.from_user.id

    song = get_or_create_song(chat_id, message_id)
    if user_has_voted(user_id, song):
        query.answer()
        return

    add_vote_to_song(song, user_id, query.data)

    likes, dislikes = get_song_votes(song)

    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"👍 {likes}", callback_data='like'),
            InlineKeyboardButton(f"👎 {dislikes}", callback_data='dislike')
        ]
    ]))


# TODO: Timeouts. Disorder of messages
# TODO: Refactor code
def split_audio(bot, update):
    update_type = update.message or update.channel_post
    command, vid_url = update_type.text.split('album ')
    message_id = update_type.message_id
    try:
        video_info = youtubeconverter.convert_video(vid_url, download=False)
        restricted_title = youtubeconverter.get_restricted_filename(video_info['title'])
        bot
        files_to_process = process_description(video_info['description'])
        files_to_process = list(filter(lambda el: bool(el), files_to_process))
        logger.info(files_to_process)
        if files_to_process:
            audio_file = get_or_download_video(restricted_title, vid_url)
            audio = AudioSegment.from_mp3(audio_file)
            files_to_send = []
            for file in files_to_process:
                filename = cut_audio_and_save(
                    audio,
                    restricted_title,
                    file['start'],
                    file['end'],
                    file['title']
                )
                files_to_send.append(filename)

            keyboard = [
                [
                    InlineKeyboardButton("👍", callback_data='thumbs_up'),
                    InlineKeyboardButton("👎", callback_data='thumbs_down')
                ]
            ]
            bot.sendMessage(
                chat_id=update_type.chat_id,
                text=f"*{video_info['title']}*",
                parse_mode='Markdown'
            )
            for index, file in enumerate(files_to_send):
                try:
                    with open(file['file'], 'rb') as f:
                        bot.sendAudio(
                            chat_id=update_type.chat_id,
                            audio=f,
                            title=f"{index} - {file['title']}",
                            reply_markup=InlineKeyboardMarkup(keyboard)
                        )
                except telegram.error.TimedOut:
                    time.sleep(1)

            bot.sendMessage(
                chat_id=update_type.chat_id,
                text=f"END *{video_info['title']}*",
                parse_mode='Markdown'
            )

    except youtube_dl.utils.DownloadError:
        pass
