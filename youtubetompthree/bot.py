import logging
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler
from telegram.ext import Updater
from telegram.messageentity import MessageEntity

from youtubetompthree import handlers
from youtubetompthree.filters import AlbumFilter

logger = logging.getLogger(__name__)

updater = None


def __get_updater(token):
    global updater
    if not updater:
        updater = Updater(token=token)
        return updater
    return updater


def setup_and_configure_bot(token):
    dispatcher = __get_updater(token).dispatcher

    album_handler = MessageHandler(AlbumFilter(), handlers.split_audio)
    youtube_links_handler = MessageHandler(
        Filters.entity(MessageEntity.URL),
        handlers.download_audio
    )

    dispatcher.add_handler(album_handler)
    dispatcher.add_handler(youtube_links_handler)
    dispatcher.add_handler(CallbackQueryHandler(handlers.vote_song))

    return updater
