import logging
import os
import re

from youtubetompthree import youtubeconverter

logger = logging.getLogger(__name__)


def get_or_download_video(title, vid_url):
    """
    Return the audio location if we have already downloaded previously and download it
    if the didn't
    :param title:
    :param vid_url:
    :return:
    """
    file_location = f'audio/{title}.mp3'
    exists = os.path.isfile(file_location)
    if not exists:
        youtubeconverter.convert_video(vid_url)
    return file_location


def convert_to_milliseconds(time):
    t = time.split(':')

    seconds = int(t[-1]) * 1000
    minutes = int(t[-2]) * 60 * 1000
    milliseconds = seconds + minutes
    if len(t) > 2:
        hours = int(t[-3]) * 60 * 60 * 1000
        milliseconds += hours

    return milliseconds


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


def process_description(description):
    files_to_process = []
    lines = description.split('\n')
    expression = r'^(.*?)(\d{1,2}:\d{1,2})(.*?)$'

    for index, line in enumerate(lines):
        m = re.search(expression, line)
        if m:
            title = m.group(1) or m.group(3)
            title = title.replace('-', '').strip(' ')
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
