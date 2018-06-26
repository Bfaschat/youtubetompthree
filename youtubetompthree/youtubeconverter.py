import youtube_dl
import youtube_dl.utils

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '256',
    }],
    'restrictfilenames': True,
    'outtmpl': './audio/%(title)s.%(ext)s'
}


def convert_video(youtube_url, download=True):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(youtube_url, download=download)


def get_restricted_filename(youtube_title):
    return youtube_dl.utils.sanitize_filename(youtube_title, restricted=True)
