import logging

from youtubetompthree import config
from youtubetompthree.bot import setup_and_configure_bot

logger = logging.getLogger(__name__)


# TODO: Config logging properly
def setup_logging():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )


def run_webhook():
    setup_logging()
    updater = setup_and_configure_bot(config.TOKEN)
    logger.info('Webhook started!')

    updater.bot.set_webhook(f'{config.WEBHOOK_URL}/{config.TOKEN}')
    updater.start_webhook(
        listen=config.HOST,
        port=config.PORT,
        url_path=config.TOKEN
    )


def run_polling():
    setup_logging()
    updater = setup_and_configure_bot(config.TOKEN)
    logger.info('Polling started!')

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    run_polling()
