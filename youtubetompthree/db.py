import sqlite3

conn = None


def __get_connection():
    global conn
    if not conn:
        conn = sqlite3.connect('example.db')
    return conn


def drop_tables():
    c = __get_connection().cursor()
    c.execute("""
        DROP TABLE `users`
    """)
    c.execute("""
        DROP TABLE `songs`
        """)
    c.execute("""
        DROP TABLE `songs_users`
        """)


def create_table_if_does_not_exists():
    c = __get_connection().cursor()
    c.execute("""
CREATE TABLE IF NOT EXISTS `users` (
    `id`    INTEGER UNIQUE
);
""")
    c.execute(
        """
CREATE TABLE IF NOT EXISTS `songs` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    `chat_id`    INTEGER,
    `message_id`    INTEGER,
    `likes` INTEGER,
    `dislikes` INTEGER,
    UNIQUE (chat_id, message_id) ON CONFLICT REPLACE
);
        """
    )
    c.execute(
        """
CREATE TABLE IF NOT EXISTS `songs_users` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
    `user`    INTEGER,
    `song`    INTEGER,
    UNIQUE (user, song) ON CONFLICT REPLACE
);
        """
    )
    __get_connection().commit()


def get_or_create_song(chat_id, message_id):
    t = (chat_id, message_id)
    c = __get_connection().cursor()
    c.execute('SELECT * FROM songs WHERE chat_id=? AND message_id=?', t)
    results = c.fetchall()
    if not results:
        c.execute("""
            INSERT INTO songs(chat_id, message_id, likes, dislikes) VALUES (?,?,0,0)
        """, t)
        c.execute('SELECT * FROM songs WHERE chat_id=? AND message_id=?', t)
        results = c.fetchall()
    __get_connection().commit()
    return results[0]


def user_has_voted(user_id, song_id):
    t = (song_id, user_id)
    c = __get_connection().cursor()
    c.execute('SELECT * FROM songs_users WHERE song=? AND user=?', t)
    if c.fetchone():
        return True
    return False


def add_vote_to_song(song_id, user_id, vote):
    likes, dislikes = get_song_votes(song_id)
    if vote == 'like':
        likes += 1
    elif vote == 'dislike':
        dislikes += 1
    c = __get_connection().cursor()
    t = (likes, dislikes, song_id)
    c.execute('UPDATE songs SET likes = ?, dislikes = ? WHERE id=?', t)
    u = (user_id, song_id)
    c.execute('INSERT INTO songs_users(user, song) VALUES (?, ?)', u)
    __get_connection().commit()


def get_song_votes(song_id):
    t = (song_id,)
    c = __get_connection().cursor()
    c.execute('SELECT likes, dislikes FROM songs WHERE id=?', t)
    return c.fetchone()
