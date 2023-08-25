import pathlib
import pandas
from abc import ABC, abstractmethod


class FileSource(ABC):
    """
    Абстрактный источник из файла.
    """
    source_type = ''

    def __init__(self, path, file_id=None, read_params={}):
        self.path = path
        self._read_params = read_params

    @abstractmethod
    def get_data(self):
        pass

    def test(self):
        path = pathlib.Path(self.path)
        return path.is_file()

    @property
    def is_sql(self):
        return False

    @property
    def source_type(self):
        return self.__class__.source_type

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass


class CSVSource(FileSource):
    """
    Источник из csv-файла.
    """
    source_type = 'csv'

    def get_data(self):
        self._read_params['sep'] = ';'
        data = pandas.read_csv(self.path, **self._read_params)
        return data


class ExcelSource(FileSource):
    """
    Источник из excel-файла.
    """
    source_type = 'excel'

    def get_data(self):
        data = pandas.read_excel(self.path, **self._read_params)
        return data


FILE_SOURCES = {
    'csv': CSVSource,
    'excel': ExcelSource,
}
