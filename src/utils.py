from datetime import timedelta, datetime as dt

from src.const import prices_etf_sym_choices
from src.const import prices_fx_sym_choices
from src.const import iv_ice_choices
from src.const import intraday_prices_cme_sym_choices


async def ensure_ust_and_exchange_are_set(args: {}):
    await ensure_exchange_is_set(args)
    await ensure_security_type_is_set(args)


async def ensure_exchange_is_set(args: {}):
    if args['exchange'] is None:
        raise ValueError('Exchange was not set')


async def ensure_security_type_is_set(args: {}):
    if args['ust'] is None:
        raise ValueError('ust was not set')


async def guess_exchange_and_ust(args: {}) -> {}:
    if args['exchange'] is None:
        args['exchange'] = await guess_exchange_from_symbol_intraday(args['symbol'])
    if args['ust'] is None:
        args['ust'] = await guess_ust_from_symbol_intraday(args['symbol'])
    return args


async def guess_exchange_from_symbol_intraday(symbol: str) -> str:
    mapping = {
        'cme': intraday_prices_cme_sym_choices,
        'usetf': prices_etf_sym_choices,
        'int': prices_fx_sym_choices,
        'ice': iv_ice_choices
    }
    for exchange in list(mapping):
        if symbol.lower() in mapping[exchange]:
            return exchange


async def guess_ust_from_symbol_intraday(symbol: str) -> str:
    mapping = {
        'fut': intraday_prices_cme_sym_choices,
        'eqt': prices_etf_sym_choices,
        'fx': prices_fx_sym_choices
    }
    for ust in list(mapping):
        if symbol.lower() in mapping[ust]:
            return ust


async def add_missing_keys(keys: [str], args: dict) -> dict:
    for key in keys:
        if key not in list(args):
               args[key] = None
    return args


async def eod_ini_logic(args: {}) -> {}:
    """
    assure that the `startdate` and `enddate` keys in the returned dictionary are:
        - ready for postgres which expects `YYYY-MM-DD`
        - `startdate` is bigger or equal to `enddate`
        - are not None
    """
    if 'dminus' not in args:
        args['dminus'] = 20
    if args['dminus'] is None:
        args['dminus'] = 20
    delta_d = timedelta(days=args['dminus'])
    if args['enddate'] is None:
        args['enddate'] = dt.now().date().strftime('%Y%m%d')
    if args['startdate'] is None:
        args['startdate'] = (dt.strptime(args['enddate'], '%Y%m%d') - delta_d).strftime('%Y%m%d')
    enddate = dt.strptime(args['enddate'], '%Y%m%d')
    startdate = dt.strptime(args['startdate'], '%Y%m%d')
    if startdate > enddate:
        startdate = enddate
    args['enddate'] = enddate.strftime('%Y-%m-%d')
    args['startdate'] = startdate.strftime('%Y-%m-%d')
    return args


async def put_call_trafo(args: {}) -> {}:
    if args['putcall'] == 'put':
        args['putcall'] = 0
    elif args['putcall'] == 'call':
        args['putcall'] = 1
    else:
        raise NotImplementedError()
    return args


class CinfoQueries:
    @staticmethod
    def ust_f(args):
        return f'''
            SELECT DISTINCT ust AS ust
            FROM cinfo 
            ORDER BY ust;
        '''

    @staticmethod
    def ust_where_exchange_f(args):
        return f'''
            SELECT DISTINCT ust AS ust
            FROM cinfo 
            WHERE exchange = '{args['exchange']}'
            ORDER BY ust;
        '''

    @staticmethod
    def ust_where_symbol_f(args):
        return f'''
            SELECT DISTINCT ust AS ust
            FROM cinfo 
            WHERE symbol = '{args['symbol']}'
            ORDER BY ust;
        '''

    @staticmethod
    def exchange_f(args):
        return f'''
            SELECT DISTINCT exchange AS exchange
            FROM cinfo 
            ORDER BY exchange;
        '''

    @staticmethod
    def exchange_where_ust_f(args):
        return f'''
            SELECT DISTINCT exchange AS exchange
            FROM cinfo 
            WHERE ust = '{args['ust']}'
            ORDER BY exchange;
        '''

    @staticmethod
    def exchange_where_symbol_f(args):
        return f'''
            SELECT DISTINCT exchange AS exchange
            FROM cinfo 
            WHERE symbol = '{args['symbol']}'
            ORDER BY exchange;
        '''

    @staticmethod
    def symbol_f(args):
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM cinfo 
            ORDER BY symbol;
        '''

    @staticmethod
    def symbol_where_ust_f(args):
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM cinfo 
            WHERE ust = '{args['ust']}']
            ORDER BY ust;
        '''

    @staticmethod
    def symbol_where_exchange_f(args):
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM cinfo 
            WHERE exchange = '{args['exchange']}'
            ORDER BY ust;
        '''

    @staticmethod
    def symbol_where_ust_and_exchange_f(args):
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM            cinfo 
            WHERE           exchange = '{args['exchange']}'
                AND         ust = '{args['ust']}'
            ORDER BY        symbol;
       '''

    @staticmethod
    def ltd_where_ust_exchange_and_symbol_f(args):
        return f'''
        SELECT DISTINCT ltd AS ltd
        FROM            cinfo 
        WHERE           symbol = '{args['symbol']}'
            AND         exchange = '{args['exchange']}'
            AND         ust = '{args['ust']}'
        ORDER BY        ltd;
       '''

    @staticmethod
    def ltd_date_where_ust_exchange_and_symbol_f(args):
        return f'''
        SELECT DISTINCT ltd_date AS ltd
        FROM            cinfo 
        WHERE           symbol = '{args['symbol']}'
            AND         exchange = '{args['exchange']}'
            AND         ust = '{args['ust']}'
        ORDER BY        ltd_date;
       '''

    @staticmethod
    def get_table_and_schema_by_ltd(args):
        return f'''
            SELECT schema_name, table_name 
            FROM    cinfo
            WHERE   ust = '{args['ust']}'
                AND exchange = '{args['exchange']}'
                AND symbol = '{args['symbol']}'
                AND ltd = '{args['ltd']}';
        '''

    @staticmethod
    def get_schema_and_table_for_futures_sql(args):
        return f'''
        SELECT schema_name, table_name
        FROM cinfo
        WHERE   symbol = '{args["symbol"]}'
            AND ust = '{args["ust"]}'
            AND exchange = '{args["exchange"]}'
            AND underlying_month = '{args["underlying_month"]}'
            AND option_month = '{args["option_month"]}'
            AND ltd = '{args["ltd"]}';
            '''

    @staticmethod
    def get_table_and_schema_by_month_and_year(args):
        raise NotImplementedError(
            'It is unclear (by design), whether option month and option year'
            'should actually reference to the month and year of the future. '
            'My second guess is that it is the second one')
        return f'''
            SELECT schema_name, table_name 
            FROM    cinfo
            WHERE   ust = '{args['ust']}'
                AND exchange = '{args['exchange']}'
                AND symbol = '{args['symbol']}'
                AND option_month_code = '{args['month']}'
                AND option_year = '{args['year']}';
        '''

    @staticmethod
    def strikes_where_table_f(args):
        return f'''
            SELECT DISTINCT strkpx AS strike
            FROM {args['schema']}.{args['table']}
            ORDER BY strkpx;
        '''

    @staticmethod
    def strikes_where_table_and_pc_f(args):
        return f'''
            SELECT DISTINCT strkpx AS strike
            FROM {args['schema']}.{args['table']}
            WHERE putcall = {args['putcall']}
            ORDER BY strkpx;
        '''

    @staticmethod
    def first_and_last_date_where_putcall_and_strike_f(args):
        return f'''
            SELECT  MIN(BIZDT) as start_date,
                    MAX(bizdt) as last_date,
            FROM {args['schema']}.{args['table']}
            WHERE putcall = {args['putcall']}
            AND strkpx = {args['strkpx']}
            GROUP BY strkpx 
            ORDER BY strkpx;
        '''

