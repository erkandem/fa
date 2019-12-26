"""
path = '/home/kan/Desktop/intraday.csv'
path = '/home/kan/dev/py/fa/fa/data/intraday.csv'

\copy (SELECT * FROM eqt_usetf.eqt_usetf_spy_prices_intraday ORDER BY dt DESC LIMIT 30000) TO <path>  WITH CSV DELIMITER ',' HEADER;
COPY zip_codes FROM '/path/to/csv/ZIP_CODES.txt' WITH (FORMAT csv);
"""

from datetime import datetime as dt
from testing_utilities.db import PgSync
import csv

SCHEMA = 'public'
TABLE = 'play_with_windows'

engine = PgSync().get_con(db_name='fastapi_tests')

def create_price_table_sql(schema, table):
    return f'''
    CREATE TABLE IF NOT EXISTS {schema}.{table}
    (
        dt timestamp without time zone NOT NULL,
        tz_offset smallint,
        open_value double precision,
        high_value double precision,
        low_value double precision,
        close_value double precision,
        volume_value integer,
        PRIMARY KEY (dt)
    );'''


def insert_price_table(schema, table):
    return f'INSERT INTO {schema}.{table} values(%s, %s, %s, %s, %s, %s, %s);'


def create_table(schema, table):
    PgSync.execute(engine, create_price_table_sql(schema, table))
    result = PgSync.fetch(engine, f'SELECT EXISTS (SELECT 1 FROM {schema}.{table});')
    assert result[0][0]


def insert_demo_values(schema, table):
    csv_data = csv.reader(open('/home/kan/dev/py/fa/fa/data/intraday.csv', 'r'), delimiter=',')
    for n, row in enumerate(csv_data):
        if n > 0:
            PgSync.execute(engine, insert_price_table(schema, table), vars=row)


#############################################################################
#                                                                           #
#                                                                           #
#                                                                           #
#                                                                           #
#                                                                           #
#############################################################################

floor_to_minutes = '''
select 
    to_timestamp(
        floor(
            (
            extract('epoch' FROM %s)
            ) / %s
        ) * %s

    )   AT TIME ZONE 'UTC';
'''

'''
SELECT dt from public.play_with_windows

'''

def test_floor_to_minutes():
    """
    either
        AT TIME ZONE 'UTC'
    or
        result = (result - result.utcoffset()).replace(tzinfo=None)

    """
    multiplier = 60 * 1
    now = dt(2019, 1, 1, 20, 5, 19, 50)
    now_truncated = dt(2019, 1, 1, 20, 5, 0, 0)
    result = PgSync.fetch(
        engine,
        floor_to_minutes,
        vars=(now, multiplier, multiplier,)
    )[0][0]
    assert result == now_truncated


def test_floor_to_two():
    """
    either
        AT TIME ZONE 'UTC'
    or
        result = (result - result.utcoffset()).replace(tzinfo=None)

    """
    multiplier = 60 * 1
    now = dt(2019, 1, 1, 20, 5, 19, 50)
    now_truncated = dt(2019, 1, 1, 20, 5, 0, 0)
    result = PgSync.fetch(
        engine,
        floor_to_minutes,
        vars=(now, multiplier, multiplier,)
    )[0][0]
    assert result == now_truncated

'''
SELECT 
	dt,
	to_timestamp(
	--
	) AT TIME ZONE 'UTC',
	tz_offset, 
	open_value, 
	high_value, 
	low_value, 
	close_value, 
	volume_value
FROM public.play_with_windows
LIMIT 10;
'''

# floor((extract('epoch' FROM dt)) / (60 * 1)) *(60 * 1) -- 1 minutes
# ok but easier to use date_trunc('minutes', column)
# but actually unnecessary since the data is already at 1 minute granularity

# floor((extract('epoch' FROM dt)) / (60 * 5)) * (60 * 5) -- 5 minutes
# ok

# floor((extract('epoch' FROM dt)) / (60 * 60 * 1) ) * (60 * 60 * 1) -- one hourly
# ok but easier to use date_trunc('hour', column)

# floor((extract('epoch' FROM dt)) / (60 * 60 * 2) ) * (60 * 60 * 2) -- two hourly
# ok

# floor((extract('epoch' FROM dt)) / (60 * 60 * 24) ) * (60 * 60 * 24) -- daily
# works but easier to use date_trunc('day', column)

# floor((extract('epoch' FROM dt)) / (60 * 60 * 24 * 7) ) * (60 * 60 * 24 * 7) -- 2 days
# works but does not start at monday
# therefore and especially because it is easier: date_trunc('week', column)
# likewise for week and month
