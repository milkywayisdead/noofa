_TEST_QUERIES = {
    'postgres': 'SELECT 1',
    'mysql': 'SELECT 1',
    'sqlite': 'SELECT 1',
    'mssql': 'SELECT 1',
}


_TABLES_QUERIES = {
    'postgres': "SELECT table_name FROM information_schema.tables " + \
            "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') ORDER BY table_name;",

    'mysql': "SELECT table_name FROM information_schema.tables " + \
            "WHERE table_schema = %s ORDER BY table_name",

    'mssql': 'SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;',

    'sqlite': "SELECT name FROM sqlite_master WHERE type='table';",
}


_COLUMNS_QUERIES = {
    'postgres': "SELECT table_name, column_name, data_type FROM information_schema.columns " + \
            "WHERE table_schema NOT IN ('pg_catalog', 'information_schema') ORDER BY table_name, column_name;",

    'mysql': "SELECT table_name, column_name, column_type from information_schema.columns " + \
            "WHERE table_schema = %s ORDER BY table_name, column_name;",

    'mssql': "SELECT table_name, column_name, data_type FROM information_schema.columns " + \
            "ORDER BY table_name, column_name;",
}


_FIELDS_QUERIES = {
    'postgres': "SELECT column_name FROM information_schema.columns " + \
            "WHERE table_name = %s AND table_schema NOT IN ('pg_catalog', 'information_schema') " + \
            "ORDER BY column_name;",

    'mysql': "SELECT column_name FROM information_schema.columns " + \
            "WHERE table_name = %s AND table_schema = %s ORDER BY column_name;",

    'mssql': "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS " + \
            "WHERE TABLE_NAME = {?} ORDER BY COLUMN_NAME;",

    'sqlite': "SELECT * from %s;",
}


_PG_MSSQL_CONSTR_Q = "SELECT tc.table_name as referencing_table, " + \
        "tc.constraint_type as constr_type, " + \
        "ksu.column_name as col_name, " + \
        "ccu.table_name as referenced_table, " + \
        "ccu.column_name as referenced_column " + \
        "FROM information_schema.table_constraints as tc " + \
        "INNER JOIN information_schema.key_column_usage as ksu " + \
        "ON tc.constraint_name = ksu.constraint_name " + \
        "AND tc.table_schema = ksu.table_schema " + \
        "INNER JOIN information_schema.constraint_column_usage as ccu " + \
        "ON tc.constraint_name = ccu.constraint_name " + \
        "AND tc.table_schema = ccu.table_schema " + \
        "WHERE tc.constraint_type in ('PRIMARY KEY', 'FOREIGN KEY') " + \
        "ORDER BY constr_type, referencing_table"


_MYSQL_CONSTR_Q = "SELECT tc.table_name as referencing_table, " + \
        "tc.constraint_type as constr_type, " + \
        "kcu.column_name as col_name, " + \
        "kcu.referenced_table_name as referenced_table, " + \
        "kcu.referenced_column_name as referenced_column " + \
        "FROM information_schema.table_constraints as tc " + \
        "INNER JOIN information_schema.key_column_usage as kcu " + \
        "ON tc.constraint_name = kcu.constraint_name " + \
        "AND tc.table_schema = kcu.table_schema " + \
        "AND tc.table_name = kcu.table_name " + \
        "WHERE tc.constraint_type in ('PRIMARY KEY', 'FOREIGN KEY') " + \
        "AND tc.table_schema = %s"


_CONSTRAINTS_QUERIES = {
    'postgres': _PG_MSSQL_CONSTR_Q,
    'mssql': _PG_MSSQL_CONSTR_Q,
    'mysql': _MYSQL_CONSTR_Q,
}
