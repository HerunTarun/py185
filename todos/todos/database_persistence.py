import os
from contextlib import contextmanager

import logging
import psycopg2
from psycopg2.extras import DictCursor

LOG_FORMAT = '%(asctime)s -%(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

class DatabasePersistence:
    def __init__(self):
        self._setup_schema()

    @contextmanager
    def _database_connect(self):
        if os.environ.get('FLASK_ENV') == 'production':
            connection = psycopg2.connect(os.environ['DATABASE_URL'])
        else:
            connection = psycopg2.connect(dbname='todos')

        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _setup_schema(self):
        if not self._check_table_exists('lists'):
            with self._database_connect() as conn:
                with conn.cursor() as cursor:
                    create_list_table = """
                        CREATE TABLE lists (
                        id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        title varchar(255) NOT NULL UNIQUE);
                    """
                    cursor.execute(create_list_table)

        if not self._check_table_exists('todos'):
            with self._database_connect() as conn:
                with conn.cursor() as cursor:
                    create_todos_table = """
                        CREATE TABLE todos (
                        id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        title text NOT NULL,
                        completed boolean NOT NULL DEFAULT false,
                        list_id integer NOT NULL
                        REFERENCES lists(id) ON DELETE CASCADE);
                    """
                    cursor.execute(create_todos_table)

    def _check_table_exists(self, table_name):
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                query_table = """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                    """
                cursor.execute(query_table, (table_name,))
                result = cursor.fetchone()

        return result[0]


    def find_list(self, list_id):
        query = """
            SELECT lists.*,
                    COUNT(todos.id) AS todos_count,
                    COUNT(NULLIF(todos.completed, True)) AS todos_remaining
            FROM lists
            LEFT JOIN todos
            ON todos.list_id = lists.id
            WHERE lists.id = %s
            GROUP BY lists.id
            ORDER BY lists.title
        """
        logger.info("Executing query: %s with list_id: %s", query, list_id)
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (list_id,))
                lst = cursor.fetchone()
                if not lst:
                    return None
                else:
                    lst = dict(lst)

        return lst

    def find_todos_for_list(self, list_id):
        query = "SELECT * FROM todos WHERE list_id = %s"
        logger.info("Executing query: %s with list_id: %s", query, list_id)
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, (list_id,))
                return cursor.fetchall()

    def all_lists(self):
        query = """
            SELECT lists.*,
                    COUNT(todos.id) AS todos_count,
                    COUNT(NULLIF(todos.completed, True)) AS todos_remaining
            FROM lists
            LEFT JOIN todos
            ON todos.list_id = lists.id
            GROUP BY lists.id
            ORDER BY lists.title
        """
        logger.info("Executing query: %s", query)
        with self._database_connect() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

        lists = [dict(result) for result in results]
        return lists

    def create_new_list(self, title):
        query = "INSERT INTO lists (title) VALUES (%s)"
        logger.info("Executing query: %s with title: %s", query, title)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (title,))

    def update_list_by_id(self, list_id, new_title):
        query = "UPDATE lists SET title = %s WHERE id = %s"
        logger.info("Executing query: %s with list_id: %s and new_title: %s",
                    query, list_id, new_title)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (new_title, list_id,))

    def delete_list(self, list_id):
        query = "DELETE FROM lists WHERE id = %s"
        logger.info("Executing query: %s with list_id: %s",
                    query, list_id)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id,))

    def create_new_todo(self, list_id, todo_title):
        query = "INSERT INTO todos (list_id, title) VALUES (%s, %s)"
        logger.info("Executing query: %s with list_id: %s and todo_title: %s",
                    query, list_id, todo_title)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id, todo_title,))

    def delete_todo_from_list(self, list_id, todo_id):
        query = "DELETE FROM todos WHERE list_id = %s AND id = %s"
        logger.info("Executing query: %s with list_id: %s and id: %s",
                    query, list_id, todo_id)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id, todo_id,))

    def update_todo_status(self, list_id, todo_id, new_status):
        query = """
            UPDATE todos
            SET completed = %s
            WHERE list_id = %s AND id = %s
        """
        logger.info("Executing query: %s with list_id: %s, id: %s, status: %s",
                    query, list_id, todo_id, new_status)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (new_status, list_id, todo_id,))

    def mark_all_todos_completed(self, list_id):
        query = "UPDATE todos SET completed = True WHERE list_id = %s"
        logger.info("Executing query: %s with list_id: %s",
                    query, list_id)
        with self._database_connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (list_id,))




