from noofa.tests.base import NoofaFunctionTest
from noofa.core.func import sql


class TestSqlFunctions(NoofaFunctionTest):
    """
    Тестирование функций построения sql-запросов.
    """
    @classmethod
    def setUpClass(cls):
        cls.add_cases_from_list(_CASES)

    def test_select(self):
        f1 = sql.SqlSelect('table')
        sql_dict = f1()
        expected_keys = [
            'is_subquery', 'tables', 'base',
            'joins', 'filters', 'values', 'order_by'
        ]
        self.assertCountEqual(sql_dict.keys(), expected_keys)

        expected_keys.append('limit')
        f2 = sql.SqlSelect('table', [], [], [], [], 10)
        sql_dict = f2()
        self.assertCountEqual(sql_dict.keys(), expected_keys)

    def test_join(self):
        f1 = sql.SqlJoin('table1.col1', 'table2.col2')
        sql_dict = f1()
        expected_keys = ['l', 'r', 'j', 'on']
        self.assertCountEqual(sql_dict.keys(), expected_keys)
        self.assertEqual(sql_dict['j'], 'inner')

        f2 = sql.SqlJoin('table1.col1', 'table2.col2', 'left')
        sql_dict = f2()
        self.assertEqual(sql_dict['j'], 'left')

    def test_where(self):
        f = sql.SqlWhere('table.col', '>', 0)
        sql_dict = f()
        expected_keys = ['is_complex', 'table', 'field', 'op', 'value']
        self.assertCountEqual(sql_dict.keys(), expected_keys)

    def test_orderby(self):
        f = sql.SqlOrderBy('asc', 'table.col')
        sql_dict = f()
        expected_keys = ['table', 'fields', 'type']
        self.assertCountEqual(sql_dict.keys(), expected_keys)

    def test_complex_where(self):
        expected_keys = ['is_complex', 'op', 'filters']

        f1 = sql.SqlWhere('table.col', '>', 0)()
        f2 = sql.SqlWhere('table.col', '<', 1)()
        complex_where1 = f1 & f2
        self.assertCountEqual(complex_where1.keys(), expected_keys)
        self.assertCountEqual([f1._q, f2._q], complex_where1['filters'])
        complex_where2 = f1 | f2
        self.assertCountEqual(complex_where2.keys(), expected_keys)
        self.assertCountEqual([f1._q, f2._q], complex_where2['filters'])

"""
Содержимое кортежей в списке _CASES:
(
    Функция,
    сабкейсы (кортеж из аргументов и ожидаемого результата),
    аргументы для проверки ошибки по типу аргумента,
    аргументы для проверки ошибки по кол-ву аргументов
)
"""
_CASES = (
    (sql.SqlSelect, ((('table', ), sql.SqlDict, 'isinstance'), ), ((1, ), ), ()),
    (sql.SqlJoin,
        ((('table.col', 'table1.col', 'inner'), sql.SqlDict, 'isinstance'), ),
        ((1, 2), ),
        (('table', ),)
    ),
    (sql.SqlWhere,
        ((('table.col', '>', 0), sql.SqlWhereDict, 'isinstance'), ),
        ((1, '', ''), ),
        ('table.col',)
     ),
    (sql.SqlOrderBy,
        ((('asc', 'table.col'), sql.SqlDict, 'isinstance'), ),
        (('asc', 0), ),
        ('asc', )
     ),
)
