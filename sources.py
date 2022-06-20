import redis
import psycopg2
import requests
from abc import ABC, abstractmethod


class DataSource(ABC):
    """
    Абстрактный источник.
    """

    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def get_data(self):
        pass


class PostgresSource(DataSource):
    """
    Источник postgres.
    """

    def __init__(self, **kwargs):
        self.dbname = kwargs.get('dbname')
        self.host = kwargs.get('host')
        self.port = kwargs.get('port')
        self.user = kwargs.get('user')
        self.password = kwargs.get('password')
        self.connection = self.get_connection()

    def get_tables(self):
        """
        Получение списка таблиц в базе.
        Исключаются таблицы, содержащие системную информацию.
        """

        tables = []

        with self.connection as conn:
            cursor = conn.cursor()
            q = "SELECT table_name FROM information_schema.tables "
            q += "WHERE table_name NOT LIKE 'pg_%' AND "
            q += "table_schema <> 'information_schema';"
            cursor.execute(q)
            res = cursor.fetchall()

        tables = [r[0] for r in res]

        return tables

    def get_connection(self, **kwargs):
        """
        Создание соединения с базой.
        """

        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

        return conn

    def get_data(self, query, **kwargs):
        """
        Получение данных/выполнение sql-запроса.
        """

        data = {}

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()

        return data

    def get_fields(self, table_name, **kwargs):
        """
        Получение списка полей в таблице.

        table_name - имя таблицы из бд.
        """

        fields = []

        with self.connection as conn:
            with conn.cursor() as cursor:
                q = "SELECT column_name, data_type FROM information_schema.columns "
                q += "WHERE table_name = %s"
                cursor.execute(q, (table_name, ))
                res = cursor.fetchall()
                fields = [column[0] for column in res]

        return fields

    def get_table(self, table_name):
        """
        Построение таблицы.

        table_name - имя таблицы из бд.
        """

        from query import Table
        return Table(table_name, self.get_fields(table_name))


class RedisSource(DataSource):
    def __init__(self, **kwargs):
        self.host = kwargs.get('host', 'localhost')
        self.port = kwargs.get('port', 6379)
        self.db = kwargs.get('db', 0)
        self.username = kwargs.get('user', None)
        self.password = kwargs.get('password', None)
        self.source = kwargs.get('source')

    def get_connection(self, **kwargs):
        conn = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            username=self.username,
            password=self.password
        )

        return conn

    def get_data(self, **kwargs):
        data = {}

        with self.get_connection() as conn:
            data = conn.hgetall(self.source)

        return data

    def get_fields(self, **kwargs):
        fields = []

        with self.get_connection() as conn:
            if conn.hlen(self.source):
                pass


class JsonSource(DataSource):
    def __init__(self, url, **kwargs):
        self.url = kwargs.get('url')
        self.params = kwargs.get('params', {})
        self.headers = kwargs.get('headers', {})
        self.auth = kwargs.get('auth', ())

    def get_connection(self, **kwargs):
        conn = requests.Session()
        return conn

    def get_data(self, **kwargs):
        data = {}

        with self.get_connection() as conn:
            resp = conn.get(
                self.url,
                headers=self.headers,
                auth=self.auth,
                params=self.params
            )

            data = resp.json()

        return data

    def get_fields(self, **kwargs):
        pass
