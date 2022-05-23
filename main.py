# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


import re
import sqlalchemy
from pprint import pprint
import psycopg2
from yandex_music import Client

def set_tables(connection, token):
    #Заполним БД из Яндекс Музыка
    client = Client(token).init()
    CHART_ID = 'world'
    chart = client.chart(CHART_ID).chart

    i = 0
    for playlist in chart.similar_playlists:
        i += 1

        print(playlist.title, playlist.playlist_uuid, playlist.created[0:4])
        if not connection.execute(f"SELECT id FROM collection WHERE id = {i};").fetchall():
            sql = f"INSERT INTO collection VALUES({i},'{nm(playlist.title)}','{playlist.created[0:4]}');"
            connection.execute(sql)

    for track_short in chart.tracks:
        track, chart = track_short.track, track_short.chart

        if track.artists:
            album = track.albums[0]
            for artist in track.artists:

                if not connection.execute(f"SELECT id FROM singer WHERE id = {artist.id};").fetchall():
                    sql = f"INSERT INTO singer VALUES({artist.id},'{nm(artist.name)}','{nm(artist.name)}');"
                    connection.execute(sql)

                if not connection.execute(f"SELECT id FROM albom WHERE id = {album.id};").fetchall():
                    sql = f"INSERT INTO albom VALUES({album.id},'{nm(album.title)}','{album.year}');"
                    connection.execute(sql)

                if not connection.execute(f"SELECT id FROM track WHERE id = {track.id};").fetchall():
                    sql = f"INSERT INTO track VALUES({track.id},'{ nm(track.title)}','{artist.id}', {album.id}, {track.duration_ms});"
                    connection.execute(sql)
                    print(track.id, track.title, track.duration_ms)

                if not connection.execute(f"SELECT * FROM singers_alboms WHERE singer_id = {artist.id} AND albom_id = {album.id};").fetchall():
                    sql = f"INSERT INTO  singers_alboms VALUES({artist.id},{album.id});"
                    connection.execute(sql)

def nm(name):
    return re.sub("[$']", "", name)

def query(connection):

    ########### Запросы #######
    print('название и год выхода альбомов, вышедших в 2018 году:')
    sql = f"SELECT name, year FROM albom WHERE year = '{2018}' ;"
    pprint(connection.execute(sql).fetchall())

    print('название и продолжительность самого длительного трека:')
    sql = f"SELECT name, duration_ms FROM track WHERE duration_ms =(select max(duration_ms) FROM track );"
    pprint(connection.execute(sql).fetchall())

    print('название треков, продолжительность которых не менее 3,5 минуты:')
    sql = f"SELECT name, duration_ms FROM track WHERE duration_ms > {3.5*60*1000} LIMIT 20;"
    pprint(connection.execute(sql).fetchall())

    print('названия сборников, вышедших в период с 2018 по 2020 год включительно:')
    sql = f"SELECT name FROM collection WHERE year >= 2018 and year <= 2020;"
    pprint(connection.execute(sql).fetchall())

    print('исполнители, чье имя состоит из 1 слова')
    sql = f"SELECT full_name FROM singer WHERE NOT full_name LIKE '%% %%' LIMIT 10;"
    pprint(connection.execute(sql).fetchall())

    print('название треков, которые содержат слово "мой"/"my".')
    sql = f"SELECT name FROM track WHERE name LIKE '%%мой%%' OR name LIKE '%%my%%' LIMIT 10;"
    pprint(connection.execute(sql).fetchall())

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    db = 'postgresql://postgres:password@localhost:5432/netology_db2'
    engine = sqlalchemy.create_engine(db)
    connection = engine.connect()
    token = 'token'
    # Задание 1
    set_tables(connection, token)
    # Задание 2
    query(connection)
