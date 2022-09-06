from .schema import DataSchema
from .components import ComponentsSchema
from .utils import Interpreter, panda_builder


class ReportBuilder:
    """
    Формирователь отчётов.
    """
    def __init__(self, config_dict={}):
        self._dataschema = DataSchema()  # схема данных
        self._components_schema = ComponentsSchema()  # схема компонентов
        self.interpreter = Interpreter()  # интерпретатор для вычисления формул
        self._compiled_queries = {}  #  сформированные запросы
        self._built_dataframes = {}  #  сформированные датафреймы
        self._results = {}  #  результаты запросов (полученные данные)
        sources_conf = config_dict.get('sources', {})
        queries_config = config_dict.get('queries', {})
        dataframes_config = config_dict.get('dataframes', {})
        for s in sources_conf.values():
            self._dataschema.add_source(**s)
        for q in queries_config.values():
            self._dataschema.add_query(**q)
        for df in dataframes_config.values():
            self._dataschema.add_dataframe(**df)

    def build_query(self, query_id):
        """
        Сформировать объект запроса.
        """
        query = self._compiled_queries.get(query_id, None)
        if query is None:
            query = self.get_query(query_id)
            q = query.compile()
            self._compiled_queries[query.id] = q
            return q
        return query

    def get_data(self, query_id):
        query = self.get_query(query_id)
        data = query.execute()
        self._results[query.id] = data
        return data

    def build_dataframe(self, dataframe_id):
        """
        Сформировать датафрейм.
        """
        df = self._built_dataframes.get(dataframe_id, None)
        if df is not None:
            return df
        df = self.get_dataframe(dataframe_id)
        if not df.is_composite:
            dataframe = df.build()
        else:
            build_options = df.build_options
            build_type = build_options['type']
            if build_type == 'join':
                on = build_options['on']
                dataframes = build_options['dataframes']
                dataframes = [self.build_dataframe(df) for df in dataframes]
                dataframe = panda_builder.join(dataframes[0], dataframes[1], on)
            elif build_type == 'union':
                dataframes = build_options['dataframes']
                dataframes = [self.build_dataframe(df) for df in dataframes]
                dataframe = panda_builder.union(dataframes)
        self._built_dataframes[df.id] = dataframe
        return dataframe

    def df_to_dict(self, dataframe_id):
        """
        Датафрейм -> словарь.
        """
        df = self.build_dataframe(dataframe_id)
        return df.to_dict(orient='records')

    def get_source(self, source_id):
        return self._dataschema.get_source(source_id)

    def get_query(self, query_id):
        return self._dataschema.get_query(query_id)

    def get_dataframe(self, dataframe_id):
        return self._dataschema.get_dataframe(dataframe_id)


        

    