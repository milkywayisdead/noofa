class ReportComponent:
    """
    Базовый класс для компонентов отчёта.
    """
    def __init__(self, id=None, build_from=None,
        base_value=None, title_text='', title_font_size=12,
        evaluator=None, **options):
        self.id = id
        self.type = None  # chart, table, pivot_table
        self._build_from = build_from
        self._base = base_value
        self.title_text = title_text
        self._title_font_size = title_font_size

        #  "вычислитель" - объект, который будет вычислять результаты
        #  в случае, когда base либо её части строятся из выражения ('expression');
        #  этим объектом на данный момент должен быть экз. ReportBuilder из noofa.builder.
        self._evaluator = evaluator

    @property
    def evaluator(self):
        return self._evaluator

    @evaluator.setter
    def evaluator(self, value):
        self._evaluator = value

    @property
    def build_from(self):
        """
        Формат, из которого строится основание для компонента.
        """
        return self._build_from

    @property
    def base(self):
        """
        Значение основания, из которого строится компонент.
        """
        return self._base
