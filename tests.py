import psycopg2
import unittest
from sources import PostgresSource


db = PostgresSource(
    host='localhost',
    port=5432,
    dbname='learn',
    user='max',
    password='12345',        
)


class TestDatabaseSource(unittest.TestCase):
    def setUp(self):
        self.db_source = PostgresSource(
            host='localhost',
            port=5432,
            dbname='learn',
            user='max',
            password='12345',        
        )


from query import Table

def get():
    return db, db.get_table('companies'), db.get_table('countries')


if __name__ == '__main__':
    pass
