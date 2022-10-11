_COMPONENTS_DESC = {
    'source': ['источник', 'm'],
    'query': ['запрос', 'm'],
    'df': ['датафрейм', 'm'],
    'table': ['таблица', 'f'],
    'figure': ['график', 'm'],
}


class SchemaComponentNotFound(Exception):
    def __init__(self, component_id, component_type=None):
        self.component_id = component_id
        self.component_type = component_type

    def __str__(self):
        comp_id = self.component_id
        component_desc = _COMPONENTS_DESC.get(self.component_type, ['компонент', 'm'])
        component_type, gender = component_desc
        found = 'найдена' if gender == 'f' else 'найден'
        return f'В схеме данных не {found} {component_type} "{comp_id}"'