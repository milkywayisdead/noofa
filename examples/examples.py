"""
Примеры json-объектов для построения различных объектов.
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
    #  словарь с конфигурациями источников
    'sources': {
        'test': {
            'id': 'test',  # id источника

            # формат данных, по которому будет создаваться источник:
            # json/conn_str/expression - словарь, строка подключения либо выражение
            'from': 'json',  
            'type': 'postgres',
            'value': {
                'host': 'localhost',
                'port': 5432,
                'dbname': 'reports',
                'user': 'max',
                'password': '12345',
            },
        },

        # здесь при создании источника будет использоваться строка подключения
        'mysql': {
            'from': 'conn_str',
            'id': 'mysql',
            'type': 'mysql',
            'value': 'host=localhost;database=test;user=max;port=3306;password=12345',
        },

        # здесь при создании источника будет использоваться выражение
        'redis': {
            'from': 'expression',
            'id': 'redis',
            'type': 'redis',
            'value': 'create_connection("redis", "host=localhost;port=6379;database=1")',
        },
    },

    # словарь с конфигурациями запросов к БД
    'queries': {
        'film': {
            'id': 'film',  # id запроса
            'source': 'test',  # id источника

            # формат данных, по которому будет создаваться запрос:
            # json/expression - словарь либо выражение
            'from': 'json', # json/expression

            # этот запрос будет формироваться из словаря
            'value': {'base': 'film', 'tables': ['film']},
        },
        'test3': {
            'id': 'test3',
            'source': 'mysql',
            'from': 'expression',
            # этот запрос будет формироваться из выражения
            'value': 'sql_select("titanic")',
        },
        'test1': {
            'id': 'test1',
            'source': 'test',
            'from': 'json',
            'value': {'base': 'city', 'tables': ['city']},
        },
        'test0': {
            'id': 'test0',
            'source': 'test',
            'from': 'json',
            'value': {'base': 'address', 'tables': ['address']},
        },
        'test2': {
            'id': 'test2',
            'source': 'test',
            'from': 'json',
            'value': jsq,
        },
    },

    #  словарь с конфигурациями датафреймов
    'dataframes': {
        'film': {
            'id': 'film',  # id датафрейма

            # конфигурация основы для датафрейма
            'base': {
                #  тип основы - результат запроса к бд (query, указыается id запроса)
                #  либо выражение - expression, результат которого должен быть в свою очередь датафреймом

                # этот датафрейм будет строиться по результатам запроса
                'type': 'query',
                #  'значение' основания - id запроса либо строка выражения
                'value': 'film',
                'source': 'test',  # id источника - актуально при type=query
            },
            # список конфигураций 'склеиваний' с датафреймом
            'unions': [
                #{
                    #  формат 'приклеиваемого' значения - датафрейм или выражение
                    #'from': 'dataframe',  # склеиваться будет с другим датафреймом 
                    #'value': 'test5',  # нужно указать id датафрейма
                #},
                {
                    'from': 'expression',  # значение приклеиваемого дф будет получено из выражения
                    'value': 'dataframe(test5["city.city_id"])',  
                }
            ],
            # список соединений
            'joins': [
                {
                    'from': 'expression',  # аналогично, формат/откуда берется датафрейм - другой датафрейм или выражение
                    'value': 'dataframe(sql_execute(create_connection("postgres", "database=reports;user=max;password=12345;"), sql_select("address")))',
                    'on': ['city.city_id', 'address.city_id', ],
                    'type': 'inner',
                },
            ],
            # список фильтров
            'filters': [
                {
                    'from': 'json',
                    'value': {
                        'is_q': False,
                        'col_name': 'city.city_id',
                        'op': '>',
                        'value': 10,
                    },
                },
                {
                    'from': 'expression',
                    'value': 'df_filter("city.city_id", "<", 20)',
                },
            ],
            'ordering': [],
            'columns': [],
        },
        'test': {
            'id': 'test5',
            'base': {
                'type': 'query',
                'value': 'test1',
                'source': 'test',
            },
        },
        'test0': {
            'id': 'test0',
            'base': {
                'type': 'query',
                'value': 'test0',
                'source': 'mysql',
            },
        },
        'testjoin': {
            'id': 'testjoin',
            'base': {
                'type': 'expression',
                'value': 'df_join(test0, test5, "address.city_id", "city.city_id", "inner")',
            },
            'filters': [
                {
                    'from': 'json',
                    'value': {
                        'col_name': 'city.city_id',
                        'op': '>',
                        'value': 12,
                        'is_q': False,
                    },
                },
                {
                    'from': 'json',
                    'value': {
                        'is_q': True,
                        'op': 'or',
                        'filters': [
                            {
                                'col_name': 'address.city_id',
                                'op': '>',
                                'value': 20,
                                'is_q': False,
                            },
                            {
                                'col_name': 'city.city_id',
                                'op': '<',
                                'value': 100,
                                'is_q': False,
                            },
                        ],
                    },
                },
            ],
            'ordering': {
                'asc': True,
                'cols': ['city.city_id'],
            },
            #  список конф. изменений либо добавлений столбцов
            'columns': [
                {
                    #  источник значений - выражение (expression), применение выражения к строкам датафрейма (apply)
                    'from': 'expression',
                    'name': 'test111',
                    'value': '11',
                },
                {
                    'from': 'apply',
                    'name': 'test1112',
                    'value': 'row["city.city_id"] * idx',
                },
            ],
        },
    },
}

#  кофигурация компонентов отчёта
components_conf = {
    'table1': {
        'id': 'table1',
        #  тип компонента - таблица или график - table/figure
        'type': 'table',

        #  основа - получаемые данные
        'base': {
            #  откуда берутся данные - датафрейм/выражение
            'from': 'dataframe',  # dataframe/expression/json
            'value': 'testjoin',
        },
        #  информация по компоновке
        'layout': {
            # Заголовок таблицы, если нужно
            'title_text': 'Таблица1',
            # список столбцов датафрейма, которые исключаются при выводе
            'to_exclude': ['city.city_id', 'address.address_id', 'address.address2', 'address.city_id'],

            # словарь для переименования столбцов;
            # формат {'название_существующего_столбца1': 'новое_название_столбца', ...}
            'aliases': {
                'city.city': 'город',
            },
        },
    },
    'figure1': {
        'id': 'fig1',
        'type': 'figure',  # график
        'engine': 'plotly',  # "движок" - библиотека, которая будет исп. при построении графика
        'figure_type': 'line',  # тип графика
        'base': {
            'from': 'list',  # формат данных, в этом случае - набор отдельных линий
            'value': [
                {
                    'name': 'Alberta',
                    'x_from': 'expression',
                    'x': 'get_column(filter(test0, df_filter("address.district", "==", "Alberta")), "address.address_id")',
                    'y_from': 'column',
                    'y': {'df_from': 'expression', 'dataframe': 'filter(test0, df_filter("address.district", "==", "Alberta"))', 'column': 'address.phone'},
                },
                {
                    'name': 'QLD',
                    'x_from': 'column',
                    'x': {'df_from': 'expression', 'dataframe': 'filter(test0, df_filter("address.district", "==", "QLD"))', 'column': "address.address_id"},
                    'y_from': 'expression',
                    'y': 'get_column(filter(test0, df_filter("address.district", "==", "QLD")), "address.phone")',
                },
            ],
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Графег1',
            'title_font_size': 12,
        },
    },
    'figure2': {
        'id': 'fig2',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'line',
        'base': {
            'from': 'grouped',  # формат данных, в этом случае - набор отдельных линий
            'value': {'df_from': 'dataframe', 'dataframe': 'test0'},
            'line_group': 'address.district',
            'x': 'address.address_id',
            'y': 'address.phone',
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Графег2',
            'title_font_size': 12,
        },
    },
    'figure3': {
        'id': 'fig3',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'pie',
        'base': {
            'from': 'list',
            'value': [
                {
                    'value': 'mean(test0["address.address_id"])',
                    'name': 'Жужа' 
                },
                {
                    'value': 'min(test0["address.address_id"])',
                    'name': 'Жожа' 
                },
            ],
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Графег2',
            'title_font_size': 12,
        },
    },
    'figure4': {
        'id': 'fig4',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'pie',
        'base': {
            'from': 'dataframe',
            'value': {'df_from': 'dataframe', 'dataframe': 'df_head(test0, 10)'},
            'values': 'address.address_id',
            'names': 'address.district',
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Графег2',
            'title_font_size': 18,
        },
    },
    'figure4': {
        'id': 'bar',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'bar',
        'base': {
            'from': 'list',
            'value': [
                {
                    'x_from': 'column',
                    'y_from': 'expression',
                    'x': {'df_from': 'expression', 'dataframe': 'filter(test0, df_filter("address.district", "==", "QLD"))', 'column': "address.district"},
                    'y': 'test0["address.address_id"]',
                    'name': 'b52',
                },
                {
                    'x_from': 'expression',
                    'y_from': 'expression',
                    'x': 'test0["address.district"]',
                    'y': 'test0["address.address_id"]',
                    'name': 'b53',
                },
            ],
            'barmode': 'relative',
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Столбцы',
            'title_font_size': 18,
        },
    },
    'figure5': {
        'id': 'bar2',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'hbar',
        'base': {
            'from': 'dataframe',
            'value': {'df_from': 'dataframe', 'dataframe': 'df_head(test0, 8)'},
            'y': 'address.district',
            'x': 'address.address_id',
            'barmode': 'relative',
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Столбцы',
            'title_font_size': 18,
        },
    },
}


document_conf = {
    #  список id компонентов, которые будут включены в pdf-документ
    'components': ['fig2', 'table1', 'bar2', 'table1', 'bar'],
}
