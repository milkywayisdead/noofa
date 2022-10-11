class RecursiveDataframeBuildError(Exception):
    def __init__(self, dataframe_id):
        self.dataframe_id = dataframe_id

    def __str__(self):
        return f'Датафрейм {self.dataframe_id} при построении ссылается на себя'