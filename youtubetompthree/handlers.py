import logging

from telegram.error import BadRequest

from youtubetompthree import youtubeconverter

logger = logging.getLogger(__name__)


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
        bot.sendAudio(
            chat_id=update_type.chat_id,
            audio=file,
            title=video_info['title']
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
