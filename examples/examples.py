"""
Примеры json-объектов для построения различных объектов.
"""
import os


_chinook_db_file = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/examples/chinook.db'


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
        'sqlite': {
            'id': 'sqlite', # id источника

            # формат данных, по которому будет создаваться источник:
            # json/conn_str/expression - словарь, строка подключения либо выражение
            'from': 'json',
            'type': 'sqlite',
            'value': {
                'dbname': _chinook_db_file,
            },
        },
    },

    # словарь с конфигурациями запросов к БД
    'queries': {
        'sqlite': {
            'id': 'sqlite',  # id запроса
            'source': 'sqlite',  # id источника

            # формат данных, по которому будет создаваться запрос:
            # json/expression - словарь либо выражение
            'from': 'expression', # json/expression

            # этот запрос будет формироваться из выражения
            'value': 'sql_select("albums")',
        },
        'sqlite2': {
            'id': 'sqlite2',
            'source': 'sqlite',
            'from': 'expression',
            'value': 'sql_select("artists")',
        },
        'sqlite3': {
            'id': 'sqlite3',
            'source': 'sqlite',
            'from': 'json',
            'value': {
                'is_subquery': False,
                'base': 'albums',
                'tables': ['albums', 'artists', 'tracks'],
                'joins': [
                    {'l': 'albums', 'r': 'artists', 'j': 'inner', 'on': {'l': 'ArtistId', 'r': 'ArtistId'}},
                    {'l': 'albums', 'r': 'tracks', 'j': 'inner', 'on': {'l': 'AlbumId', 'r': 'AlbumId'}},
                ],
                'filters': [
                    {'is_complex': True, 'op': 'and', 'filters': [
                        {'is_complex': False, 'table': 'albums', 'field': 'AlbumId', 'op': '>', 'value': 100},
                        {'is_complex': False, 'table': 'albums', 'field': 'AlbumId', 'op': '<', 'value': 300},
                    ]},
                    #{'is_complex': False, 'table': 'albums', 'field': 'AlbumId', 'op': 'in', 'value': {
                    #    'is_subquery': True, 'base': 'albums', 'tables': ['albums'], 'values': [{'table': 'albums', 'field': 'AlbumId'}],
                    #}},
                    #{'is_complex': False, 'table': 'albums', 'field': 'ArtistId', 'op': 'in', 'value': [19, 21]},
                ],
                'values': [
                    #{'table': 'albums', 'field': 'Title'}, {'table': 'artists', 'field': 'Name'}
                ],
                'order_by': [
                    {'table': 'albums', 'fields': ['Title'], 'type': 'asc'},
                ],
                'limit': 100,
            },
        },
    },

    #  словарь с конфигурациями датафреймов
    'dataframes': {
        'sqlite': {
            'id': 'sqlite',  # id датафрейма

            # конфигурация основы для датафрейма
            'base': {
                #  тип основы - результат запроса к бд (query, указыается id запроса)
                #  либо выражение - expression, результат которого должен быть в свою очередь датафреймом

                # этот датафрейм будет строиться по результатам запроса
                'type': 'query',
                'source': 'sqlite',  # id источника - актуально при type=query
                'value': 'sqlite',  #  'значение' основания - id запроса либо строка выражения
            },
            # список соединений
            'joins': [
                {
                    'from': 'expression', # аналогично, формат/откуда берется датафрейм - другой датафрейм или выражение
                    'value': 'dataframe(sql_execute(create_connection("sqlite", "database=' + _chinook_db_file + '"), sql_select("artists")))',
                    'on': ['albums.ArtistId', 'artists.ArtistId', ],
                    'type': 'inner',
                },
            ],
            'unions': [],                #{
                #    'from': 'expression',  # значение приклеиваемого дф будет получено из выражения
                #    'value': 'dataframe(sql_execute(create_connection("sqlite", "database=' + _chinook_db_file + '"), sql_select("albums")))',
                    #'dataframe(test5["city.city_id"])',
                    #'from': 'dataframe',
                    #'value': 'sqlite2',
                #}ery',
                #'source': 'sqlite',
                #'value': 'sqlite2',
        },
        'sqlite3': {
            'id': 'sqlite3',
            'base': {
                'type': 'query',
                'source': 'sqlite',
                'value': 'sqlite3',
            },
            'filters': [
                #{'from': 'json', 'value': {'is_q': False, 'col_name': 'tracks.Milliseconds', 'op': '>', 'value': 200000}},
                {'from': 'expression', 'value': 'df_filter("tracks.Milliseconds", ">", 200000) & df_filter("tracks.Milliseconds", "<", 300000)'},
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
            'value': 'sqlite3',
        },
        #  информация по компоновке
        'layout': {
            # Заголовок таблицы, если нужно
            'title_text': 'Таблица1',
            # список столбцов датафрейма, которые исключаются при выводе
            'to_exclude': [],

            # словарь для переименования столбцов;
            # формат {'название_существующего_столбца1': 'новое_название_столбца', ...}
            'aliases': {
                'artists.Name': 'Исполнитель',
                'albums.Title': 'Альбом',
            },
        },
    },
    'lines': {
        'id': 'lines',
        'type': 'figure',  # график
        'engine': 'plotly',  # "движок" - библиотека, которая будет исп. при построении графика
        'figure_type': 'line',  # тип графика
        'base': {
            'from': 'list',  # формат данных, в этом случае - набор отдельных линий
            'value': [
                {
                    'name': 'U2',
                    'x_from': 'expression',
                    'x': 'get_column(filter(sqlite3, df_filter("artists.Name", "==", "U2")), "tracks.TrackId")',
                    'y_from': 'column',
                    'y': {'df_from': 'expression', 'dataframe': 'filter(sqlite3, df_filter("artists.Name", "==", "U2"))', 'column': 'tracks.Bytes'},
                },
                {
                    'name': 'Soundgarden',
                    'x_from': 'column',
                    'x': {'df_from': 'expression', 'dataframe': 'filter(sqlite3, df_filter("artists.Name", "==", "Soundgarden"))', 'column': 'tracks.TrackId'},
                    'y_from': 'expression',
                    'y': 'get_column(filter(sqlite3, df_filter("artists.Name", "==", "Soundgarden")), "tracks.Bytes")',
                },
            ],
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Линии',
            'title_font_size': 12,
        },
    },
    'lines2': {
        'id': 'lines2',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'line',
        'base': {
            'from': 'grouped',  # формат данных, в этом случае - набор отдельных линий
            'value': {'df_from': 'expression', 'dataframe': 'df_head(sqlite3, 50)'},
            'line_group': 'artists.Name',
            'x': 'tracks.TrackId',
            'y': 'tracks.Milliseconds',
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Линии2',
            'title_font_size': 12,
        },
    },
    'pie': {
        'id': 'pie',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'pie',
        'base': {
            'from': 'list',
            'value': [
                {
                    'value': 'min(sqlite3["tracks.Milliseconds"]/1000)',
                    'name': 'Мин. длительность' 
                },
                {
                    'value': 'max(sqlite3["tracks.Milliseconds"]/1000)',
                    'name': 'Макс. длительность' 
                },
                {
                    'value': 'mean(sqlite3["tracks.Milliseconds"]/1000)',
                    'name': 'Средняя длительность' 
                },
            ],
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Пирог1',
            'title_font_size': 30,
        },
    },
    'pie2': {
        'id': 'pie2',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'pie',
        'base': {
            'from': 'dataframe',
            'value': {'df_from': 'dataframe', 'dataframe': 'sqlite3'},
            'values': 'tracks.UnitPrice',
            'names': 'tracks.Name',
        },
        'layout': {
            'showlegend': True,
            'title_text': 'Пирог2',
            'title_font_size': 18,
        },
    },
    'bar': {
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
                    'x': {'df_from': 'expression', 'dataframe': 'sqlite3', 'column': "tracks.Name"},
                    'y': 'sqlite3["tracks.Milliseconds"]',
                    'name': 'Длительность',
                },
                {
                    'x_from': 'expression',
                    'y_from': 'expression',
                    'x': 'sqlite3["tracks.Name"]',
                    'y': 'sqlite3["tracks.Bytes"]',
                    'name': 'Bytes',
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
    'bar2': {
        'id': 'bar2',
        'type': 'figure',
        'engine': 'plotly',
        'figure_type': 'bar',
        'base': {
            'from': 'dataframe',
            'value': {'df_from': 'dataframe', 'dataframe': 'sqlite3'},
            'y': 'tracks.Name',
            'x': 'tracks.Milliseconds',
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
    'components': ['lines2', 'table1', 'pie', 'pie2', 'bar', 'bar2'],
    'orientation': 'landscape',
}