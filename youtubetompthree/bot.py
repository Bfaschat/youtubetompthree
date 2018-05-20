import logging
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler, CommandHandler
from telegram.ext import Updater
from telegram.messageentity import MessageEntity

from youtubetompthree import handlers

logger = logging.getLogger(__name__)

updater = None


def __get_updater(token):
    global updater
    if not updater:
        updater = Updater(token=token)
        return updater
    return updater


def setup_bot(token):
    return __get_updater(token)


def setup_and_configure_bot(token):
    dispatcher = __get_updater(token).dispatcher

    youtube_links_handler = MessageHandler(
        Filters.entity(MessageEntity.URL),
        handlers.youtube_links
    )
    dispatcher.add_handler(CommandHandler('album', handlers.split_audio))
    dispatcher.add_handler(youtube_links_handler)
    dispatcher.add_handler(CallbackQueryHandler(handlers.vote_song))

    return updater
