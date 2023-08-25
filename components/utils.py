def apply_filters(df, filters):
    complex_filter = None
    for col, filters_conf in filters.items():
        type_, values = filters_conf['type'], filters_conf['values']
        dtype = str(df[col].dtype)
        is_num = dtype.startswith('int') or dtype.startswith('float')
        if is_num or dtype == 'bool':
            values = _conv(values, dtype, is_num)

        f = df[col].isin(values)
        if type_ == 'exclude':
            f = ~f
        if complex_filter is None:
            complex_filter = f
        else:
            complex_filter &= f

    if complex_filter is not None:
        return df[complex_filter]

    return df


def _conv(seq, dtype, is_num=False):
    def _bool(value):
        value = value.lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False

    def _num(value):
        try:
            return float(value)
        except:
            return None

    if dtype == 'bool':
        f = _bool
    if is_num:
        f = _num

    converted_values = [i for i in map(f, seq) if i is not None]
    return converted_values
