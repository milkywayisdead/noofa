from noofa.tests.base import NoofaTest
from noofa.core.sources.conn import _parse_conn_str


class TestParseConnString(NoofaTest):
    """
    Тестирование парсинга строки подключения.
    """
    def setUp(self):
        self._wrong_param = 'wrong_param'
        self.conn_str = 'host=host;port=1;database=db;'
        self.conn_str += f'user=user;password=pwd;ad=true'
        self.conn_str_with_wrong_param = self.conn_str + f';{self._wrong_param}=true'
        self.bad_conn_str = 'param1=1;param2'

    def test_parse(self):
        parsed = _parse_conn_str(self.conn_str)
        for param in ['host', 'port', 'user', 'password', 'database', 'ad']:
            self.assertIn(param, parsed)

    def test_parse_with_wrong_param(self):
        parsed = _parse_conn_str(self.conn_str_with_wrong_param)
        self.assertNotIn(self._wrong_param, parsed)

    def test_bad_conn_str(self):
        self.assertRaises(Exception, _parse_conn_str, self.bad_conn_str)
