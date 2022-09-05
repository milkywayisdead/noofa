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

    _is_sql = False

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

    @property
    def is_sql(self):
        return self.__class__._is_sql


class DatabaseSource(DataSource):
    _is_sql = True

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
        self.connection = None

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
            connect_timeout=3,
        )
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def get_data(self, **kwargs):
        query = kwargs['query']
        q, params = query.str_and_params()
        fields = query.requested
        data = []

        with self.connection.cursor() as cursor:
            if params:
                cursor.execute(q, params)
            else:
                cursor.execute(q)

            _data = cursor.fetchall()
            desc = fields 
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

    def get_table(self, table_name):
        """
        Построение таблицы.

        table_name - имя таблицы из бд.
        """
        from .query import Table
        return Table(table_name, self.get_fields(table_name), enquote=True)


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
        self.connection = None

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
            connect_timeout=3,
        )
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def get_data(self, **kwargs):
        query = kwargs['query']
        q, params = query.str_and_params()
        fields = query.requested
        data = []
        with self.connection.cursor() as cursor:
            if params:
                cursor.execute(q, params)
            else:
                cursor.execute(q)

            _data = cursor.fetchall()
            desc = fields
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
        self.connection = None

    def get_connection(self, **kwargs):
        conn = redis.Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            username=self._username,
            password=self._password,
        )
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def get_data(self, **kwargs):
        data = []
        with self.connection as conn:
            _data = conn.hgetall(self.source)

            for k, d in _data.items():
                data.append(json.loads(d))
        return data

    def get_fields(self, **kwargs):
        fields = []
        with self.connection as conn:
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
        self.connection = None

    def get_connection(self, **kwargs):
        conn = requests.Session()
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def get_data(self, **kwargs):
        data = {}
        with self.connection as conn:
            resp = conn.get(
                self._url,
                headers=self._headers,
                auth=self._auth,
                params=self._params
            )
            data = resp.json()
        return data

    def get_fields(self, **kwargs):
        return []


SOURCES_DICT = {
    'postgres': PostgresSource,
    'mysql': MySqlSource,
    'redis': RedisSource,
    'json': JsonSource,
}


def get_source_class(type_):
    return SOURCES_DICT.get(type_, None)