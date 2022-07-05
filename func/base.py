class Func:
    """
    Базовая функция.
    """

    #  выполняемая функция
    operation = None

    #  кол-во операндов, участвующих в выполнении функции;
    #  при == -1 кол-во операндов не ограничено.
    operands_num = 0

    #  при True в функцию передаются все операнды,
    #  при False операнды передаются в виде списка
    unpack_values = False

    def __init__(self, *values):
        self._values = [v for v in values]

    def go(self):
        n = self.__class__.operands_num
        op = self.__class__.operation
        unpack_values = self.__class__.unpack_values

        if n == 0:
            return op()
        if n == 1:
            return op(self._values[0])
        if n > 1 or n == -1:
            if n == -1:
                values = self._values
            else:
                values = self._values[:n]

            if unpack_values == True:
                return op(*values)
            else:
                return op(values)



