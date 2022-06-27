import json
import redis
import psycopg2
import requests
import mysql.connector
from abc import ABC, abstractmethod
from random import choice


class DataSource(ABC):
    """
    Абстрактный источник.
    """

    @abstractmethod
    def get_connection(self):
        """
        Создание соединения.
        """
        pass

    @abstractmethod
    def get_data(self):
        """
        Получение данных.
        """
        pass


class DatabaseSource(DataSource):
    @abstractmethod
    def get_tables(self):
        """
        Получение списка таблиц в базе.
        Исключаются таблицы, содержащие системную информацию.
        """
        pass

    @abstractmethod
    def get_fields(self, table_name, **kwargs):
        """
        Получение списка полей в таблице.

        table_name - имя таблицы из бд.
        """
        pass

    def get_table(self, table_name):
        """
        Построение таблицы.

        table_name - имя таблицы из бд.
        """

        from .query import Table
        return Table(table_name, self.get_fields(table_name))


class PostgresSource(DatabaseSource):
    """
    Источник postgres.
    """

    def __init__(self, **kwargs):
        self._dbname = kwargs.get('dbname')
        self._host = kwargs.get('host')
        self._port = kwargs.get('port', 5432)
        self._user = kwargs.get('user')
        self._password = kwargs.get('password')
        self.connection = self.get_connection()

    def get_tables(self):
        tables = []

        with self.connection.cursor() as cursor:
            q = "SELECT table_name FROM information_schema.tables "
            q += "WHERE table_name NOT LIKE 'pg_%' AND "
            q += "table_schema <> 'information_schema';"
            cursor.execute(q)
            res = cursor.fetchall()

        tables = [r[0] for r in res]

        return tables

    def get_connection(self, **kwargs):
        conn = psycopg2.connect(
            host=self._host,
            port=self._port,
            dbname=self._dbname,
            user=self._user,
            password=self._password,
        )

        return conn

    def get_data(self, query, **kwargs):
        data = []

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            _data = cursor.fetchall()
            desc = [i.name for i in cursor.description]
            
            for d in _data:
                datapiece = {}
                for n, i in enumerate(d):
                    datapiece[desc[n]] = i
                data.append(datapiece)

        return data

    def get_fields(self, table_name, **kwargs):
        fields = []

        with self.connection.cursor() as cursor:
            q = "SELECT column_name, data_type FROM information_schema.columns "
            q += "WHERE table_name = %s"
            cursor.execute(q, (table_name, ))
            res = cursor.fetchall()
            fields = [column[0] for column in res]

        return fields


class MySqlSource(DatabaseSource):
    """
    Источник mysql.
    """
    def __init__(self, **kwargs):
        self._dbname = kwargs.get('dbname')
        self._host = kwargs.get('host')
        self._port = kwargs.get('port', 3306)
        self._user = kwargs.get('user')
        self._password = kwargs.get('password')
        self.connection = self.get_connection()

    def get_tables(self):
        tables = []

        with self.connection.cursor() as cursor:
            q = "SELECT table_name FROM information_schema.tables "
            q += "WHERE table_schema <> 'information_schema';"
            cursor.execute(q)
            res = cursor.fetchall()

        tables = [r[0] for r in res]

        return tables

    def get_connection(self, **kwargs):
        conn = mysql.connector.connect(
            host=self._host,
            port=self._port,
            database=self._dbname,
            user=self._user,
            password=self._password,
        )

        return conn

    def get_data(self, query, **kwargs):
        data = []

        with self.connection.cursor() as cursor:
            cursor.execute(query)
            _data = cursor.fetchall()
            desc = [i[0] for i in cursor.description]
            
            for d in _data:
                datapiece = {}
                for n, i in enumerate(d):
                    datapiece[desc[n]] = i
                data.append(datapiece)

        return data

    def get_fields(self, table_name, **kwargs):
        fields = []

        with self.connection.cursor() as cursor:
            q = "SELECT column_name, data_type FROM information_schema.columns "
            q += "WHERE table_name = %s"
            cursor.execute(q, (table_name, ))
            res = cursor.fetchall()
            fields = [column[0] for column in res]

        return fields


class RedisSource(DataSource):
    def __init__(self, **kwargs):
        self._host = kwargs.get('host', 'localhost')
        self._port = kwargs.get('port', 6379)
        self._db = kwargs.get('db', 0)
        self._username = kwargs.get('user', None)
        self._password = kwargs.get('password', None)
        self.source = kwargs.get('source', '')

    def get_connection(self, **kwargs):
        conn = redis.Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            username=self._username,
            password=self._password,
        )

        return conn

    def get_data(self, **kwargs):
        data = []

        with self.get_connection() as conn:
            _data = conn.hgetall(self.source)

            for k, d in _data.items():
                data.append(json.loads(d))

        return data

    def get_fields(self, **kwargs):
        fields = []

        with self.get_connection() as conn:
            if conn.hlen(self.source):
                rand_key = choice(conn.hkeys(self.source))
                rand_value = conn.hget(self.source, rand_key)
                rand_value = json.loads(rand_value)
                fields = list(rand_value.keys())

        return fields


class JsonSource(DataSource):
    def __init__(self, url, **kwargs):
        self._url = url
        self._params = kwargs.get('params', {})
        self._headers = kwargs.get('headers', {})
        self._auth = kwargs.get('auth', ())

    def get_connection(self, **kwargs):
        conn = requests.Session()
        return conn

    def get_data(self, **kwargs):
        data = {}

        with self.get_connection() as conn:
            resp = conn.get(
                self._url,
                headers=self._headers,
                auth=self._auth,
                params=self._params
            )

            data = resp.json()

        return data

    def get_fields(self, **kwargs):
        pass
