"""
Конфигурация профиля

{
    # словарь с источниками
    sources: {
        name1: {
            id: название,
            type: тип,
            host: хост,
            port: порт,
            dbname: имя базы,
            user: имя пользователя,
            password: пароль,
        }
    },

    # словарь с запросами
    queries: {
        id: { 
            id: идентификатор запроса,
            source: название источника,
            query: тело запроса,
        },
    },

    # словарь с датафреймами
    {

    }
}
"""

# пример запроса
jsq = {
    'base': 'category',
    'tables': ['category', 'film_category'],
    'joins': [
        {'l': 'category', 'r': 'film_category', 'j': 'inner', 'on': {'l': 'category_id', 'r': 'category_id'}},
    ],
    'filters': [
        {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '==', 'value': 5},
        {'is_complex': True, 'op': 'OR', 'filters': [
            {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '>', 'value': 5},
            {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '<', 'value': 100},
            {'is_complex': True, 'op': 'AND', 'filters': [
                {'is_complex': False, 'table': 'film_category', 'field': 'category_id', 'op': '>', 'value': 8},
                {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '<', 'value': 10},
            ]}
        ]},
    ],
    'values': [],
    'limit': 5,
}

# пример запроса с подзапросами в фильтрах IN
jsq1 = {
    'base': 'category',
    'tables': ['category', 'film_category'],
    'joins': [
        {'l': 'category', 'r': 'film_category', 'j': 'inner', 'on': {'l': 'category_id', 'r': 'category_id'}},
    ],
    'filters': [
        {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': 'in', 'value': {
            'is_subquery': True,
             'base': 'category',
             'tables': ['category'],
             'values': [{'table': 'category', 'field': 'category_id'}],
        }},
        {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': 'in', 'value': {
            'is_subquery': True,
            'base': 'category',
            'tables': ['category'],
            'values': [{'table': 'category', 'field': 'category_id'}],
            'filters': [
                {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': 'in', 'value': {
                    'is_subquery': True,
                    'base': 'category',
                    'tables': ['category'],
                    'values': [{'table': 'category', 'field': 'category_id'}],
                }},
            ]
        }},
    ],
    #'values': [{'table': 'category', 'field': 'last_update'}],
}

test_conf = {
    'sources': {
        'test': {
            'id': 'test',
            'type': 'postgres',
            'host': 'localhost',
            'port': 5432,
            'dbname': 'reports',
            'user': 'max',
            'password': '12345',
        },
        'mysql': {
            'type': 'mysql',
            'id': 'mysql',
            'host': 'localhost',
            'port': 3306,
            'dbname': 'test',
            'user': 'max',
            'password': '12345',
        }
    },
    'queries': {
        'test1': {
            'id': 'test1',
            'source': 'test',
            'query': {'base': 'actor', 'tables': ['actor'], 'order_by': [
                {'table': 'actor', 'fields': ['last_name'], 'type': 'desc'},
                #{'table': 'actor', 'fields': ['last_update'], 'type': 'desc'},
            ]},
        },
        'test2': {
            'id': 'test2',
            'source': 'test',
            'query': jsq1,
        },
        'test3': {
            'id': 'test3',
            'source': 'mysql',
            'query': {'base': 'titanic', 'tables': ['titanic'],},
        }
    },
    'dataframes': {
        'test5': {
            'id': 'test5',
            'source': 'test',
            'query': 'test1',
        },
        'test6': {
            'id': 'test6',
            'source': 'test',
            'query': 'test2',
        },
        'test7': {
            'id': 'test7',
            'source': 'mysql',
            'query': 'test3',
        }
    },
    'components': {
        'table1': {
            'dataframe': 'test5',
        },
    }
}