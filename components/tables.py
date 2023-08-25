from ..core.dataframes.panda_builder import pivot_table, empty
from .base import ReportComponent
from ..utils import get_dtypes
from .utils import apply_filters


class ReportTable(ReportComponent):
    """
    Компонент-таблица.
    """
    def __init__(self, exclude=None, aliases=None, **options):
        super().__init__(**options)
        self.type = 'table'
        self._to_exclude = exclude or []  # столбцы, которые исключ. при выводе

        # словарь для переименования выводимых столбцов;
        # должен иметь формат {название_существующего_столбца1: новое_название, ...}
        self._aliases = aliases or {}
        self._df = None  #  датафрейм, данные из которого будут выводиться в виде таблицы

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        self._df = value

    def build(self, **kwargs):
        """
        Построение таблицы. Под этим подразумевается переименование столбцов
        и отбрасывание лишних столбцов в зависимости от конфигурации таблицы.
        """
        self.df = self.evaluator.evaluate(self.base)

        if self._df is not None:
            if self._aliases:
                self.df = self.df.rename(columns=self._aliases)

            cols = self._to_exclude
            if cols:
                if len(cols) < len(self.df.columns):
                    self.df = self.df.drop(cols, axis=1)
        return self

    def to_csv(self, path=None):
        sep, idx = ';', False
        if path is None:
            return self.df.to_csv(sep=sep, index=idx)
        file = open(path, 'w')
        return self.df.to_csv(file, sep=sep, index=idx)

    def to_excel(self, path):
        return self.df.to_excel(path) if self.df is not None else None

    @property
    def header(self):
        """
        Список наименований столбцов таблицы.
        """
        return self.df.columns.to_list()

    @property
    def body(self):
        """
        Список списков значений соотв. строк таблицы.
        """
        recs = list(self.df.to_records(index=False))
        return [list(r) for r in recs]

    @property
    def data(self):
        """
        Список списков значений ячеек таблицы, включая заголовок.
        """
        data = [self.header]
        for r in self.body:
            data.append(r)
        return data

    @property
    def raw_data(self):
        return self.df.to_dict(orient='records')

    def fillna(self, fill_value=''):
        return self.df.fillna(fill_value)

    def to_dict(self):
        return {
            'header': self.header,
            'body': self.body,
            'title': self.title_text,
            'id': self.id,
        }


class ReportPivotTable(ReportComponent):
    """
    Сводная таблица.
    """
    def __init__(self, pivot_conf=None, **options):
        super().__init__(**options)
        self.type = 'pivot_table'
        self._df = None
        self._pivot_conf = pivot_conf
        self.pivot_df = None

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, value):
        self._df = value

    @property
    def filters_list(self):
        return self._pivot_conf.get('filters', [])

    def build(self, filters=None, **kwargs):
        if not self._check_pivot_conf():
            self.pivot_df = empty()
            return self

        self.df = self.evaluator.evaluate(self.base)
        if self.df is not None and self._pivot_conf is not None:
            if filters:
                df = apply_filters(self.df, filters)
            else:
                df = self.df
            self.pivot_df = pivot_table(df, **self._pivot_conf)
        return self

    @property
    def is_pivot_table(self):
        return True

    def to_html(self, sparsify=True, classes=None, bold_rows=False, **kwargs):
        return self.pivot_df.to_html(
            sparsify=sparsify,
            bold_rows=bold_rows,
            classes=classes,
            **kwargs,
        )

    def _check_pivot_conf(self):
        pc = self._pivot_conf
        index, columns = pc.get('index', []), pc.get('columns', [])
        has_values = bool(pc.get('aggfunc', {}))
        has_groups = bool(index) or bool(columns)
        return has_values and has_groups
