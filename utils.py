from .core.sources.conn import SOURCES_DICT


def get_source(type_):
    return SOURCES_DICT[type_]