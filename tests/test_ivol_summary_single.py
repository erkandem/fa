from src.ivol_summary_statistics import select_statistics_single


def test_select_statistics_single():
    args = {
        'symbol': 'spy',
        'ust': None,
        'exchange': None,
        'tte': '1m',
        'startdate': None,
        'enddate': None,
        'dminus': 365,
        'delta': 'd050'
    }
    sql = select_statistics_single(args)
    assert type(sql) is str
