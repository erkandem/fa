SAMPLE_QUERIES = {
    'fut_cme_cl':
        {
            "ust": "fut",
            "exchange": "cme",
            "symbol": "cl",
            "option_month": "201912",
            "underlying_month": "201912",
            "startdate": "2019-01-01",
            "enddate": "2019-04-01",
            "putcall": "call",
            "ltd": "20191115",
            "metric": "oi",
            "dminus": 365,
            "top_n": 5,
            "order": "desc"
        },
    'eqt_usetf_spy':
        {
            "ust": "eqt",
            "exchange": "usetf",
            "symbol": "spy",
            "startdate": "2019-01-01",
            "enddate": "2019-04-01",
            "putcall": "call",
            "ltd": "20200117",
            "metric": "oi",
            "dminus": 365,
            "top_n": 5,
            "order": "desc"
        },
    'fut_ice_b':
        {
            "ust": "fut",
            "exchange": "ice",
            "symbol": "b",
            "option_month": "201910",
            "underlying_month": "201912",
            "startdate": "2019-01-01",
            "enddate": "2019-04-01",
            "putcall": "call",
            "ltd": "20191028",
            "metric": "oi",
            "dminus": 365,
            "top_n": 5,
            "order": "desc"
        },
    'ind_eurex_dax':
        {
            "ust": "ind",
            "exchange": "eurex",
            "symbol": "dax",
            "startdate": "2019-01-01",
            "enddate": "2019-04-01",
            "putcall": "call",
            "ltd": "20191220",
            "metric": "oi",
            "dminus": 365,
            "top_n": 5,
            "order": "desc"
        }
}


def membrane():
    import json
    from src.delta_data import delta_query
    from src.delta_data import delta_query_sql
    from src.rawoption_data import resolve_schema_and_table_name_sql
    from testing_utilities.db import PgSync

    con = PgSync.get_con()
    args = delta_query()
    relation_sql = resolve_schema_and_table_name_sql(args)
    relation = PgSync.fetch_with_names(con, relation_sql)
    if len(relation[0]) != 2:
        args['schema'] = relation[0]['schema_name']
        args['table'] = relation[0]['table_name']

    delta_sql = delta_query_sql(**args)
    data = PgSync.fetch(con, delta_sql)
    print(json.dumps(data, indent=2))
