"""
Вычисляемое значение в контексте.
"""


class Variable:
    def __init__(self, name, expr, evaluator=None):
        self.name = name  # название
        self.expr = expr  # значение-выражение
        self.evaluated = False  # флаг вычисленного значения
        self.value = None  # вычисленное значение
        self._evaluator = evaluator  # объект-вычислитель (используется ReportBuilder)

    def evaluate(self):
        """
        Получение вычисленного значения.
        Возвращается значение, если оно уже было вычислено.
        В противном случае значение предварительно вычисляется.
        """
        if not self.evaluated:
            self.value = self._evaluator.evaluate(self.expr)
            self.evaluated = True
        return self.value

    def force_set(self, value):
        """
        Принудительное задание значения без вычисления.
        """
        self.value = value
        self.evaluated = True

    def __str__(self):
        return f'{self.name} = {self.value if self.evaluated else self.expr}'
