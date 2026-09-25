import psycopg2

connection = psycopg2.connect(dbname='films')
connection.close()