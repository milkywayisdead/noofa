import json
import redis
import sqlite3
import psycopg2
import pyodbc
import requests
import mysql.connector
from abc import ABC, abstractmethod
from random import choice

from .file_sources import FILE_SOURCES
from .statements import (
    _TEST_QUERIES,
    _TABLES_QUERIES,
    _COLUMNS_QUERIES,
    _FIELDS_QUERIES,
    _CONSTRAINTS_QUERIES,
)


_DEFAULT_MSSQL_DRIVER = '{ODBC Driver 18 for SQL Server}'
_FREE_TDS = '{FreeTDS}'


class DataQueryResult:
    def __init__(self, data, columns=[]):
        self.data = data
        self.columns = columns


class DataSource(ABC):
    """
    Абстрактный источник.
    """

    _is_sql = False
    source_type = ''

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

    @abstractmethod
    def test(self):
        """
        Проверка связи с источником.
        """
        pass

    @property
    def _test_query(self):
        return _TEST_QUERIES.get(self.source_type, None)

    @property
    def _tables_query(self):
        return _TABLES_QUERIES.get(self.source_type, None)

    @property
    def _columns_query(self):
        return _COLUMNS_QUERIES.get(self.source_type, None)

    @property
    def _fields_query(self):
        return _FIELDS_QUERIES.get(self.source_type, None)

    @property
    def _constraints_query(self):
        return _CONSTRAINTS_QUERIES.get(self.source_type, None)

    @property
    def is_sql(self):
        return self.__class__._is_sql

    @property
    def source_type(self):
        return self.__class__.source_type

    def _parse_conn_str(self):
        return _parse_conn_str(self._conn_str)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()


class DatabaseSource(DataSource):
    _is_sql = True
    _wildcard = '%s'
    enquote = False

    @property
    def wildcard(self):
        return self.__class__._wildcard

    @property
    def enquote(self):
        return self.__class__.enquote

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
        return Table(
            table_name,
            self.get_fields(table_name),
            enquote=self.enquote
        )

    def get_table_multiple(self, tables_list):
        from .query import Table

        assert isinstance(tables_list, list), 'tables_list должен быть списком'
        tables = {}
        fields = []

        if tables_list:
            _tables_list = ""
            for table_name in tables_list:
                _tables_list += f"'{table_name}', "
            _tables_list = _tables_list.rstrip(', ')

            with self.connection.cursor() as cursor:
                q = "SELECT column_name, data_type, table_name FROM information_schema.columns "
                q += "WHERE table_name in (%s) ORDER BY table_name" % _tables_list
                cursor.execute(q)
                fields = cursor.fetchall()

        for field_name, data_type, table_name in fields:
            if not table_name in tables:
                tables[table_name] = []
            table = tables[table_name]
            table.append(field_name)

        tables = {
            table_name: Table(table_name, table_fields, enquote=self.enquote)
            for table_name, table_fields in tables.items()
        }

        return tables

    def get_db_structure(self):
        with self.connection.cursor() as cursor:
            cursor.execute(self._columns_query, (self._dbname, ))
            columns_res = cursor.fetchall()
            cursor.execute(self._constraints_query)
            constraints_res = cursor.fetchall()

        return _db_struct(columns=columns_res,
                constraints=constraints_res)


class PostgresSource(DatabaseSource):
    """
    Источник postgres.
    """

    source_type = 'postgres'
    enquote = True

    def __init__(self, host=None, port=5432, dbname=None,
        user=None, password=None, conn_str=None, **kwargs):
        self._dbname = dbname
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._conn_str = conn_str
        self.connection = None

    def get_tables(self):
        tables = []
        with self.connection.cursor() as cursor:
            q = self._tables_query
            cursor.execute(q)
            res = cursor.fetchall()
        tables = [r[0] for r in res]
        return tables

    def get_connection(self):
        if self._conn_str:
            conn_dict = self._parse_conn_str()
            conn_dict['dbname'] = conn_dict.pop('database')
            conn_dict['connect_timeout'] = 3
            return psycopg2.connect(**conn_dict)
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
        print('open')
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        print('close')
        self.connection.commit()
        self.connection.close()
        self.connection = None

    def test(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(self._test_query)
        except:
            return False
        return True

    def get_data(self, query=None, **kwargs):
        q, params = query.str_and_params()
        fields = query.requested
        data = []

        with self.connection.cursor() as cursor:
            if params:
                cursor.execute(q, params)
            else:
                cursor.execute(q)

            _data = cursor.fetchall()
            desc = [f.replace('"', "") for f in fields]
            for d in _data:
                datapiece = {}
                for n, i in enumerate(d):
                    datapiece[desc[n]] = i
                data.append(datapiece)
        return DataQueryResult(data, desc)

    def get_fields(self, table_name):
        fields = []
        with self.connection.cursor() as cursor:
            q = self._fields_query
            cursor.execute(q, (table_name, ))
            res = cursor.fetchall()
            fields = [column[0] for column in res]
        return fields


class MySqlSource(DatabaseSource):
    """
    Источник mysql.
    """

    source_type = 'mysql'

    def __init__(self, host=None, port=3306, dbname=None,
        user=None, password=None, conn_str=None, **kwargs):
        self._dbname = dbname
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._conn_str = conn_str
        self.connection = None

    def get_tables(self):
        tables = []
        with self.connection.cursor() as cursor:
            q = self._tables_query
            cursor.execute(q, (self._dbname, ))
            res = cursor.fetchall()
        tables = [r[0] for r in res]
        return tables

    def get_connection(self):
        if self._conn_str:
            conn_dict = self._parse_conn_str()
            conn_dict['connect_timeout'] = 3
            return mysql.connector.connect(**conn_dict)
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

    def test(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(self._test_query)
        except:
            return False
        return True

    def get_data(self, query=None, **kwargs):
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
        return DataQueryResult(data, desc)

    def get_fields(self, table_name):
        fields = []
        with self.connection.cursor() as cursor:
            q = self._fields_query
            cursor.execute(q, (table_name, self._dbname, ))
            res = cursor.fetchall()
            fields = [column[0] for column in res]
        return fields


class MSSqlSource(DatabaseSource):
    """
    Источник mssql.
    """

    source_type = 'mssql'
    enquote = True
    _wildcard = '?'

    def __init__(self, ad=False, host=None, port=1433,
        dbname=None, user=None, password=None, conn_str=None, **kwargs):
        self._ad = ad
        self._driver = _FREE_TDS if ad == True else _DEFAULT_MSSQL_DRIVER
        self._host = host
        self._port = port
        self._dbname = dbname
        self._user = user
        self._password = password
        self._conn_str = conn_str
        self.connection = None

    def get_tables(self):
        tables = []
        q = self._tables_query
        with self.connection.cursor() as cursor:
            cursor.execute(q)
            res = cursor.fetchall()
        tables = [r[0] for r in res]
        return tables

    def get_connection(self):
        conn_str = self._make_conn_str()
        conn = pyodbc.connect(conn_str, timeout=3)
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def test(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(self._test_query)
        except:
            return False
        return True

    def get_data(self, query=None, **kwargs):
        q, params = query.str_and_params()
        fields = query.requested
        data = []

        with self.connection.cursor() as cursor:
            if params:
                cursor.execute(q, params)
            else:
                cursor.execute(q)

            _data = cursor.fetchall()
            desc = [f.replace('"', "") for f in fields]
            for d in _data:
                datapiece = {}
                for n, i in enumerate(d):
                    datapiece[desc[n]] = i
                data.append(datapiece)
        return DataQueryResult(data, desc)

    def get_fields(self, table_name):
        fields = []
        with self.connection.cursor() as cursor:
            q = self._fields_query
            cursor.execute(q, (table_name, ))
            res = cursor.fetchall()
            fields = [column[0] for column in res]
        return fields

    def _make_conn_str(self):
        if self._conn_str:
            conn_dict = self._parse_conn_str()
            ad = conn_dict.get('ad', 'false')
            driver = _FREE_TDS if ad == 'true' else _DEFAULT_MSSQL_DRIVER
            host, port = conn_dict['host'], conn_dict.get('port', self._port)
            server = f'{host},{port}'
            db = conn_dict['database']
            user, password = conn_dict['user'], conn_dict['password']
        else:
            driver = self._driver
            server = f'{self._host},{self._port}'
            db = self._dbname
            user, password = self._user, self._password

        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={db};'
        conn_str += f'UID={user};PWD={password};ENCRYPT=optional;'

        return conn_str

    def get_db_structure(self):
        with self.connection.cursor() as cursor:
            cursor.execute(self._columns_query)
            columns_res = cursor.fetchall()
            cursor.execute(self._constraints_query)
            constraints_res = cursor.fetchall()

        return _db_struct(columns=columns_res,
                constraints=constraints_res)


class SqliteSource(DatabaseSource):
    """
    Источник sqlite. Используется для демонстрационной конфигурации -
    noofa.examples. Не планируется использовать его как один из доступных
    источников.
    """

    source_type = 'sqlite'
    _wildcard = '?'

    def __init__(self, **kwargs):
        self._db_file = kwargs.get('dbname')
        self._conn_str = kwargs.get('conn_str', None)
        self.connection = None

    def get_tables(self):
        tables = []
        cursor = self.connection.cursor()
        q = self._tables_query
        cursor.execute(q)
        res = cursor.fetchall()
        tables = [r[0] for r in res]
        return tables

    def get_connection(self, **kwargs):
        if self._conn_str:
            conn_dict = self._parse_conn_str()
            return sqlite3.connect(conn_dict['database'])
        conn = sqlite3.connect(self._db_file)
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def test(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute(self._test_query)
            cursor.close()
        except:
            return False
        return True

    def get_data(self, **kwargs):
        query = kwargs['query']
        q, params = query.str_and_params()
        fields = query.requested
        data = []

        cursor = self.connection.cursor()
        if params:
            cursor.execute(q, params)
        else:
            cursor.execute(q)

        _data = cursor.fetchall()
        desc = [f.replace('"', "") for f in fields]
        for d in _data:
            datapiece = {}
            for n, i in enumerate(d):
                datapiece[desc[n]] = i
            data.append(datapiece)
        return DataQueryResult(data, desc)

    def get_fields(self, table_name, **kwargs):
        fields = []
        cursor = self.connection.cursor()
        q = self._fields_query % table_name
        cursor.execute(q)
        fields = [description[0] for description in cursor.description]
        return fields

    def get_table_multiple(self, tables_list):
        from .query import Table

        assert isinstance(tables_list, list), 'tables_list должен быть списком'
        tables = {
            table_name: Table(table_name, self.get_fields(table_name))
            for table_name in tables_list
        }

        return tables


class RedisSource(DataSource):
    """
    Источник redis.
    """

    source_type = 'redis'

    def __init__(self, host='localhost', port=6379, db=0, user=None,
        password=None, source='', conn_str=None, **kwargs):
        self._host = host
        self._port = port
        self._db = db
        self._username = user
        self._password = password
        self.source = source
        self._conn_str = conn_str
        self.connection = None

    def get_connection(self):
        if self._conn_str:
            conn_dict = self._parse_conn_str()
            conn_dict['db'] = conn_dict.pop('database')
            return redis.Redis(**conn_dict)
        conn = redis.Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            username=self._username,
            password=self._password,
            socket_timeout=3,
        )
        return conn

    def open(self):
        if self.connection is not None:
            self.connection.close()
        self.connection = self.get_connection()

    def close(self):
        self.connection.close()
        self.connection = None

    def test(self):
        try:
            result = self.connection.ping()
        except:
            return False
        return result

    def get_data(self):
        data, columns = [], []
        with self.connection as conn:
            _data = conn.hgetall(self.source)

            for k, d in _data.items():
                data.append(json.loads(d))
            if data:
                columns = [key for key in data[0].keys()]
        return DataQueryResult(data, columns)

    def get_tables(self):
        tables = []
        try:
            with self.connection as conn:
                for h in conn.scan_iter(_type='hash'):
                    tables.append(h.decode())
        except:
            pass
        return tables

    def get_fields(self):
        fields = []
        with self.connection as conn:
            if conn.hlen(self.source):
                rand_key = choice(conn.hkeys(self.source))
                rand_value = conn.hget(self.source, rand_key)
                rand_value = json.loads(rand_value)
                fields = list(rand_value.keys())
        return fields


class JsonSource(DataSource):
    """
    Источник из json-ответа.
    Использование среди прочих источников под вопросом.
    """

    source_type = 'json'

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
        return DataQueryResult(data)

    def get_fields(self, **kwargs):
        return []


SOURCES_DICT = {
    'postgres': PostgresSource,
    'mysql': MySqlSource,
    'mssql': MSSqlSource,
    'redis': RedisSource,
    'json': JsonSource,
    'sqlite': SqliteSource,
}
SOURCES_DICT.update(FILE_SOURCES)


def get_source_class(type_):
    return SOURCES_DICT.get(type_, None)


def _parse_conn_str(conn_str):
    """
    Парсинг строки соединения.
    """
    if conn_str.endswith(';'):
        conn_str = conn_str[:-1]
    _ = ['host', 'port', 'database', 'user', 'password', 'ad']
    conn_dict = {}
    conn_str = conn_str.split(';')
    for s in conn_str:
        spl = s.split('=')
        arg, val = spl[0], spl[1]
        if arg in _:
            conn_dict[arg] = val
    return conn_dict


def _db_struct(columns=[], constraints=[]):
    db = {
        'tables': {},
        'relations': [],
    }

    for c in columns:
        table_name, column_name, data_type = c
        table = db['tables'].setdefault(table_name, {
            'name': table_name,
            'columns': [],
            'pk': [],
            'fk': [],
            'fk_cols': [],
            'relates': 0,
            'related_to': 0,
            'related_by': [],
        })
        table['columns'].append({
            'name': column_name,
            'type': data_type,
        })

    for con in constraints:
        (table_name, constr_type, column_name,
            referenced_table, referenced_column) = con
        if constr_type.lower() == 'primary key':
            pk_list = db['tables'][table_name]['pk']
            if not column_name in pk_list:
                pk_list.append(column_name)
        elif constr_type.lower() == 'foreign key':
            db['tables'][table_name]['relates'] += 1
            db['tables'][referenced_table]['related_to'] += 1
            db['tables'][table_name]['fk'].append(referenced_table)
            db['tables'][table_name]['fk_cols'].append(column_name)
            db['tables'][referenced_table]['related_by'].append(table_name)
            db['relations'].append({
                'referencing_table': table_name,
                'referencing_column': column_name,
                'referenced_table': referenced_table,
                'referenced_column': referenced_column,
            })
    return db
