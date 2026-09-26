import psycopg2
from psycopg2 import extras

connection = psycopg2.connect(dbname='films')

try:
    with connection:
        with connection.cursor(cursor_factory=extras.DictCursor) as cursor:
            cursor.execute("""
            SELECT genre, COUNT(id)
            FROM films
            WHERE duration < 100
            GROUP BY genre
            """)
            films = cursor.fetchall()
finally:
    connection.close()

for row in films:
    print(f'There is {row['count']} movie in the {row['genre']} genre')



# for row in rows:
#     print(row['title'])
