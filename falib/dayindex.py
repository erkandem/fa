"""
Copied methods from py_markets project
"""


def get_day_index_schema_name() -> str:
    return 'public'


def get_day_index_table_name(schema_name: str) -> str:
    return f'{schema_name}_bizdt_to_table_name_mapping'
