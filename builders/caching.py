import json
from datetime import datetime

from ..core.sources.conn import DataQueryResult
from ..core.dataframes import panda_builder
from .builders import ReportBuilder
from .enc import NoofaJsonEncoder


class CacheAgent:
    """
    Средство для подготовки к кэшированию и "декэширования"
    датафреймов и результатов запросов.
    """
    _meta_label = '_meta'

    def __init__(self, data, meta=None):
        self._data = data

        """
        доп. инф. о данных - используется
        для учёта полей даты и времени, которые
        были преобразованы в строки для кэширования и
        потребуют обратного преобразования после получения из кэша
        """
        self._meta = meta

        _DF = panda_builder.pd.DataFrame
        if not isinstance(self._data, _DF):
            self._data = _DF(self._data)

    @classmethod
    def from_cached(cls, cached, **kwargs):
        """
        Создание экзмепляра с использованием полученных из redis данных.
        """
        data = json.loads(cached)
        return cls(
            data['data'],
            data[cls._meta_label],
            **kwargs,
        )

    def load(self, df=True):
        """
        Преобразование полученных из redis данных в датафрейм
        либо словаря с результатами запроса.
        При df=True возвращается датафрейм, при False - словарь с рез. запроса.
        """
        dt_columns = self._meta.get('datetime_columns', [])
        data = self._data.copy(deep=True)
        if dt_columns and not data.empty:
            data[dt_columns] = data[dt_columns].astype('datetime64')
        if df == True:
            return data
        return {
            'data': data.to_dict(orient='records'),
            'columns': list(data.columns.values)
        }

    def dump(self):
        """
        Подготовка данных и преобразование их в строку перед кэшированием
        в redis. При подготовке данных значения столбцов с датой и временем
        преобразуются в строки.
        """
        meta = {'datetime_columns': []}
        df = self._data.copy(deep=True)
        dt_columns = df.select_dtypes(include=['datetime', 'datetimetz'])
        dt_columns = list(dt_columns.columns.values)
        if dt_columns:
            df[dt_columns] = df[dt_columns].astype('str')
            meta['datetime_columns'] = dt_columns
        data = df.to_dict(orient='records')
        return json.dumps({
            'data': data,
            self.__class__._meta_label: meta,
        }, cls=NoofaJsonEncoder)


class CachingReportBuilder(ReportBuilder):
    """
    Формирователь отчётов с функционалом кэширования в redis.
    Это дочерний класс от ReportBuilder с измененными методами get_or_build_dataframe и
    get_data и несколькими дополнительными методами, связанными с кэшированием.
    При создании датафрейма кэшируется его содержимое в виде словаря. При построении
    датафрейма сначала делается попытка получить кэшированное содержимое для датафрейма,
    в случае отсутствия такового - выполняется построение с нуля.
    """
    def __init__(
        self,
        redis_connection=None,
        redis_prefix='',
        redis_expire=300,
        storing_only=False,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

        # соединение с redis
        self._conn = redis_connection

        # префикс для ключей в redis
        self._prefix = redis_prefix if redis_prefix else '__'

        # время хранения значения в кэше
        self._expire = redis_expire

        # режим:
        # 0 - только сохранение в кэш (без обращения к кэшу для получения готовых данных по запросам/датафреймам),
        # 1 - обращение за результатами к кэшу + кэширование новых результатов
        self._mode = 0 if storing_only == True else 1

    def storing_only(self):
        """
        Включить режим только сохранения.
        """
        self._mode = 0

    @property
    def is_storing_only(self):
        return self._mode == 0

    def get_or_build_dataframe(self, dataframe_id):
        from_cache = False

        #  сначала пробуем получить уже готовый дф
        df = self._built_dataframes.get(dataframe_id, None)
        #  если его нет, то пробуем построить его по данным из кэша
        if df is None:
            cached_df = None if self.is_storing_only else self.get_cached_df(dataframe_id)
            if cached_df is not None:
                from_cache = True
                df = cached_df
            #  если в кэше данных нет - строим дф заново
            else:
                df = self.build_dataframe(dataframe_id)

        #  добавляем в словарь готовых дф для возможного последующего использования,
        #  чтобы не обращаться дополнительно к кэшу
        self._built_dataframes[dataframe_id] = df

        #  кэшируем дф для возможного последующего использования его данных другими
        #  экземплярами CachingReportBuilder
        if not from_cache:
            self.cache_df(dataframe_id, df)

        return df

    def get_data(self, query_id):
        from_cache = False

        #  сначала проверяем наличие рез. запроса в сохраненных результатах -
        #  в self._results
        if query_id in self._results:
            data = self._results[query_id]
        else:
            #  если их там нет - пробуем получить из кэша
            data = None if self.is_storing_only else self.get_cached_query_result(query_id)

        #  если в кэше нет результата - выполняем запрос заново
        if data is None:
            data = super().get_data(query_id)
        else:
            from_cache = True
            data = DataQueryResult(**data)

        #  кэшируем для возможного послед. использования
        if not from_cache:
            self.cache_query_result(query_id, data.data)

        return data

    def cache_df(self, dataframe_id, df, ex=None):
        """
        Кэшировать датафрейм.
        dataframe_id - id датафрейма,
        df - экз. pandas.DataFrame либо словарь,
        ex - время хранения в кэше в секундах.
        """
        ca = CacheAgent(df)
        data = ca.dump()
        self._set(
            dataframe_id,
            data,
            'dataframe',
            self._get_expire(ex)
        )

    def get_cached_df(self, dataframe_id):
        """
        Получение кэшированных данных датафрейма.
        dataframe_id - id датафрейма.
        """
        cached_df = self._get(dataframe_id, 'dataframe')
        if cached_df:
            ca = CacheAgent.from_cached(cached_df)
            df = ca.load(df=True)

            # чтобы не было ошибок при получении пустого дф из кэша
            cols = list(df.columns)
            df = df if len(cols) else None

            return df

    def cache_query_result(self, query_id, query_result, ex=None):
        """
        Кэшировать результат запроса.
        query_id - id запроса,
        query_result - результат запроса в виде списка словарей,
        ex - время хранения в кэше в секундах.
        """
        ca = CacheAgent(query_result)
        data = ca.dump()
        self._set(
            query_id,
            data,
            'query',
            self._get_expire(ex)
        )

    def get_cached_query_result(self, query_id):
        """
        Получение кэшированных результатов запроса.
        query_id - id запроса.
        """
        cached_qr = self._get(query_id, 'query')
        if cached_qr:
            ca = CacheAgent.from_cached(cached_qr)
            qr = ca.load(df=False)
            return qr

    def _set(self, key, value, value_type, ex=None, *args, **kwargs):
        """
        Установка значения в кэш.
        """
        self._conn.set(
            self._key(key, value_type),
            value,
            ex=self._get_expire(ex)
        )

    def _get(self, key, value_type):
        """
        Получение значения из кэша.
        """
        return self._conn.get(
            self._key(key, value_type)
        )

    def clear(self, key, value_type):
        self._conn.delete(self._key(key, value_type))

    def _key(self, key, value_type):
        return f'{self._prefix}:{value_type}:{key}'

    def _get_expire(self, expire):
        return expire if expire is not None else self._expire
