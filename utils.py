import redis
import json

from .core.func import collect_func_info
from .core.dataframes import panda_builder
from .pdf import PdfReport
from .builder import ReportBuilder


class CachingReportBuilder(ReportBuilder):
    """
    Формирователь отчётов с функционалом кэширования в redis.
    Это дочерний класс от ReportBuilder с измененными методами get_or_build_dataframe и
    get_data и несколькими дополнительными методами, связанными с кэшированием.
    При создании датафрейма кэшируется его содержимое в виде словаря. При построении
    датафрейма сначала делается попытка получить кэшированное содержимое для датафрейма,
    в случае отсутствия такового - выполняется построение с нуля.
    В конструктор, помимо параметров подключения, можно передавать аргумент prefix вида 'profileN', 
    где N - id профиля отчёта.
    """
    def __init__(self, *args, **kwargs):
        defaults = {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
            'ex': 300,
            'prefix': 'profile0',
        }
        for kw in defaults.keys():
            if kw in kwargs:
                defaults[kw] = kwargs.pop(kw)

        super().__init__(*args, **kwargs)
        self._redis_host = defaults['host']
        self._redis_port = defaults['port']
        self._redis_db = defaults['db']
        self._prefix = defaults['prefix']
        self._ex = defaults['ex']  # время жизни кэшированных записей в секундах
        self._conn = None

    def get_or_build_dataframe(self, dataframe_id):
        #  сначала пробуем получить уже готовый дф
        df = self._built_dataframes.get(dataframe_id, None)
        #  если его нет, то пробуем построить его по данным из кэша
        if df is None:
            cached_df = self.get_cached_df(dataframe_id)
            if cached_df:
                df = panda_builder.new(cached_df)
            #  если в кэше данных нет - строим дф заново 
            else:
                df = self.build_dataframe(dataframe_id)

        #  добавляем в словарь готовых дф для возможного последующего использования,
        #  чтобы не обращаться дополнительно к кэшу
        self._built_dataframes[dataframe_id] = df

        #  кэшируем дф для возможного последующего использования его данных другими
        #  экземплярами CachingReportBuilder
        self.cache_df(dataframe_id, df)

        return df

    def get_data(self, query_id):
        #  сначала проверяем наличие рез. запроса в сохраненных результатах -
        #  в self._results
        if query_id in self._results:
            data = self._results[query_id]
        else:
            #  если их там нет - пробуем получить из кэша
            data = self.get_cached_query_result(query_id)
        #  если в кэше нет результата - выполняем запрос заново
        if data is None:
            data = super().get_data(query_id)

        #  кэшируем для возможного послед. использования
        self.cache_query_result(query_id, data)
        return data

    def _connect(self):
        """
        Создание соединения с redis.
        """
        self._conn = redis.Redis(
            host=self._redis_host, 
            port=self._redis_port, 
            db=self._redis_db,
        )

    def _set(self, key, value, value_type='dataframe', ex=None):
        """
        Установка значения в кэш.
        """
        if self._conn is None:
            self._connect()
        _key = f'{self._prefix}:{value_type}:{key}'
        if ex is None:
            ex = self._ex
        self._conn.set(_key, value, ex=ex)

    def _get(self, key, value_type='dataframe'):
        """
        Получение значения из кэша.
        """
        if self._conn is None:
            self._connect()
        return self._conn.get(f'{self._prefix}:{value_type}:{key}')

    def cache_df(self, dataframe_id, df, ex=None):
        """
        Кэшировать датафрейм.
        dataframe_id - id датафрейма,
        df - экз. pandas.DataFrame либо словарь,
        ex - время хранения в кэше в секундах.
        """
        if isinstance(df, panda_builder.pd.DataFrame):
            df = df.to_dict(orient='records')
        df = json.dumps(df)
        self._set(dataframe_id, df, value_type='dataframe', ex=ex)

    def get_cached_df(self, dataframe_id):
        """
        Получение кэшированных данных датафрейма.
        dataframe_id - id датафрейма.
        """
        cached_df = self._get(dataframe_id, value_type='dataframe')
        if cached_df:
            cached_df = json.loads(cached_df)
            return cached_df

    def cache_query_result(self, query_id, query_result, ex=None):
        """
        Кэшировать результат запроса.
        query_id - id запроса,
        query_result - результат запроса в виде списка словарей,
        ex - время хранения в кэше в секундах.
        """
        if isinstance(query_result, list):
            query_result = json.dumps(query_result)
        self._set(query_id, query_result, value_type='query', ex=ex)

    def get_cached_query_result(self, query_id):
        """
        Получение кэшированных результатов запроса.
        query_id - id запроса.
        """
        cached_qr = self._get(query_id, value_type='query')
        if cached_qr:
            cached_qr = json.loads(cached_qr)
            return cached_qr