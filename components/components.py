"""
Классы графических компонентов отчёта.
"""


class ComponentsSchema:
    """
    Схема компонентов отчёта.
    """
    def __init__(self, dataframes={}, **kwargs):
        self._dataframes = dataframes
        self._tables = kwargs.get('tables', {})
        self._charts = kwargs.get('charts', {})

    def from_json(self, json_schema):
        tables_json = json_schema['components']
        for table in tables_json.values():
            id_ = table['id']
            df = self._dataframes[table['dataframe']]
            table['dataframe'] = df
            self._tables[id_] = ReportTable(**table)


class ReportComponent:
    def __init__(self, **options):
        self.id = options['id']
        self.type = options['type']  # chart, table, filter


class ReportTable(ReportComponent):
    """
    Таблица в компонентах отчёта.
    """
    def __init__(self, **options):
        super().__init__(**options)
        self._dataframe = options['dataframe_id']
        self.columns = options.get('columns', {})
        self.aliases = options.get('aliases', {})
        self._data = None

    def build(self):
        if self._data is None:
            data = self._dataframe.get_data()
            self._data = data
        return data

    def update(self):
        data = self._dataframe.get_data()
        self._data = data

    def to_csv(self):
        pass

    def to_xlsx(self):
        pass


class ReportChart(ReportComponent):
    def __init__(self, **options):
        super().__init__(**options)

    def add_dataset(self, dataset):
        pass