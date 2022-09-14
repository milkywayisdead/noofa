"""
Примеры json-объектов для построения различных объектов.
"""

"""
Конфигурация отчёта.
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

# пример запроса в виде json
jsq = {
    # базовая таблица
    'base': 'category',  

    # таблицы, используемые в запросе
    'tables': ['category', 'film_category'],

    # соединения таблиц  
    'joins': [
        {
            #  левая таблица в соединении
            'l': 'category',  # для первого соединения базовая таблица должна указываться левой
            #  правая таблицы
            'r': 'film_category', 
            #  тип соединения
            'j': 'inner', 
            # по каким полям соединять
            'on': {
                'l': 'category_id',  # поле левой таблицы
                'r': 'category_id'  # поле правой таблицы
            }
        },
    ],

    # фильтры where
    'filters': [
        # если в этом списке несколько фильтров, то они будут объединены через AND

        #  простой фильтр (не состоящий из нескольких условий)
        {
            'is_complex': False, # составной ли фильтр
            'table': 'category', # таблица
            'field': 'category_id',  # поле 
            'op': '==', # оператор
            'value': 5, # значение 
        },

        # составной фильтр
        {
            'is_complex': True,  # это составной фильтр, т.е. в него входят несколько условий
            'op': 'OR', #  оператор для объединения условий
            #  список условий
            'filters': [
                {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '>', 'value': 5},
                {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '<', 'value': 100},
                {'is_complex': True, 'op': 'AND', 'filters': [
                    {'is_complex': False, 'table': 'film_category', 'field': 'category_id', 'op': '>', 'value': 8},
                    {'is_complex': False, 'table': 'category', 'field': 'category_id', 'op': '<', 'value': 10},
                ]}
            ]
        },
    ],

    #  список полей, получаемых в запросе; если список пуст, то выбираются все поля
    'values': [
        {
            'table': 'category',  # название таблицы
            'field': 'last_update',  #  название поля
        }
    ],

    #  сортировка
    'order_by': [
        {
            'table': 'film_category',  # название таблицы
            'fields': ['film_id'],  #  поля
            'type': 'asc',
        }
    ],

    #  количество выбираемых строк
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
            'is_subquery': True,  # здесь указывается, что значение является подзапросом
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
}

# пример описания фильтра для датафрейма в json
panda_filter = [
    {
        'col_name': 'city.city_id',
        'op': '>',
        'value': 12,
        'is_q': False,
    },
    {
        'is_q': True,
        'op': 'or',
        'filters': [
            {
                'col_name': 'address.city_id',
                'op': 'in',
                'value': [33, 35],
                'is_q': False,
            },
            {
                'col_name': 'city.city_id',
                'op': '==',
                'value': 22,
                'is_q': False,
            },
        ],
    },
]

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
        'film': {
            'id': 'film',
            'source': 'test',
            'query': {'base': 'film', 'tables': ['film']},
        },
        'test1': {
            'id': 'test1',
            'source': 'test',
            'query': {'base': 'city', 'tables': ['city']}, #'order_by': [
                #{'table': 'city', 'fields': ['last_name'], 'type': 'desc'},
                #{'table': 'actor', 'fields': ['last_update'], 'type': 'desc'},
            #]},
        },
        'test0': {
            'id': 'test0',
            'source': 'test',
            'query': {'base': 'address', 'tables': ['address']}, #, 'order_by': [
                #{'table': 'film', 'fields': ['last_update'], 'type': 'desc'},
                #{'table': 'actor', 'fields': ['last_update'], 'type': 'desc'},
            #]},
        },
        'test2': {
            'id': 'test2',
            'source': 'test',
            'query': jsq,
        },
        'test3': {
            'id': 'test3',
            'source': 'mysql',
            'query': {'base': 'titanic', 'tables': ['titanic'],},
        }
    },
    'dataframes': {
        'film': {
            'id': 'film',
            'source': 'test',
            'query': 'test2',
            'composite': False,
        },
        'test5': {
            'id': 'test5',
            'source': 'test',
            'query': 'test1',
            'composite': False,
        },
        'test6': {
            'id': 'test6',
            'source': 'test',
            'query': 'test2',
            'composite': False,
        },
        'test7': {
            'id': 'test7',
            'source': 'mysql',
            'query': 'test3',
            'composite': False,
        },
        'test8': {
            'id': 'test8',
            'composite': True,
            'build': {
                'type': 'union',
                'dataframes': ['test7', 'test6', 'test0'],
            },
            'source': None,
            'query': None,
        },
        'test0': {
            'id': 'test0',
            'composite': False,
            'source': 'test',
            'query': 'test0',
        },
        'testjoin': {
            'id': 'testjoin',
            'composite': True,
            'source': None,
            'query': None,
            'build': {
                'type': 'join',
                'dataframes': ['test0', 'test5'],
                'on': ['address.city_id', 'city.city_id'],
            },
            'filters': panda_filter,
            'ordering': {
                'asc': True,
                'cols': ['city.city_id'],
            },
            'columns': [
                {
                    'name': 'test111',
                    'value': '11',
                },
                {
                    'name': 'test1112',
                    'value': 'row["city.city_id"] * 99',
                },
            ],
        },
    },
}
