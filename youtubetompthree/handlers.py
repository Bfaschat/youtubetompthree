import time

import logging
import os
import re
import telegram
import youtube_dl
from pydub import AudioSegment
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


def get_or_download_video(title, vid_url):
    try:
        return open(f'audio/{title}.mp3', 'rb')
    except FileNotFoundError:
        youtubeconverter.convert_video(vid_url)
        return open(f'audio/{title}.mp3', 'rb')


def youtube_links(bot, update):
    update_type = update.message or update.channel_post

    video_info = youtubeconverter.extract_info(update_type.text)
    restricted_title = youtubeconverter.get_restricted_filename(video_info['title'])

    file = get_or_download_video(restricted_title, update_type.text)

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


def convert_to_milliseconds(time):
    t = time.split(':')

    seconds = int(t[-1]) * 1000
    minutes = int(t[-2]) * 60 * 1000
    milliseconds = seconds + minutes
    if len(t) > 2:
        hours = int(t[-3]) * 60 * 60 * 1000
        milliseconds += hours

    return milliseconds


# TODO: Storage of voting per chat_id and persistent
# TODO: Timeouts. Disorder of messages
# TODO: Refactor code
def process_description(description):
    files_to_process = []
    lines = description.split('\n')
    expression = r'^(\D*)(\d{1,2}:\d{1,2})[ \- ]*(\D*)$'
    for index, line in enumerate(lines):
        m = re.search(expression, line)
        if m:
            title = m.group(1) or m.group(3)
            logger.info(f"{title} {m.group(2)}")
            start_position = convert_to_milliseconds(m.group(2))

            files_to_process.append({
                "title": title.strip(),
                "start": start_position,
                "end": None
            })

            if start_position != 0:
                files_to_process[index - 1]['end'] = start_position
        else:
            files_to_process.append({})

    return files_to_process


def cut_audio_and_save(audio, album_title, from_, to_, title):
    album_folder = f'audio/albums/{album_title}'
    if not os.path.exists(album_folder):
        os.mkdir(album_folder)

    logger.info(f'{title} | {from_}:{to_}')
    filename = os.path.join(album_folder, f'{title}.mp3')
    if not os.path.exists(filename):
        new_audio = audio[from_:to_]
        new_audio.export(filename, format="mp3")
    return {'title': title, 'file': filename}


def split_audio(bot, update):
    update_type = update.message or update.channel_post
    command, vid_url = update_type.text.split('album ')
    message_id = update_type.message_id
    try:
        video_info = youtubeconverter.extract_info(vid_url)
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
