from telegram.ext import BaseFilter


class AlbumFilter(BaseFilter):
    def filter(self, message):
        return message.text.startswith('album ')
