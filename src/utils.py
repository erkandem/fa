from datetime import datetime as dt
from datetime import timedelta
import typing as t

from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.const import (
    intraday_prices_cme_sym_choices,
    iv_ice_choices,
    prices_etf_sym_choices,
    prices_fx_sym_choices,
)
from src.schema import validate_config


def ensure_ust_and_exchange_are_set(args: t.Dict[str, t.Any]):
    ensure_exchange_is_set(args)
    ensure_security_type_is_set(args)


def ensure_exchange_is_set(args: t.Dict[str, t.Any]):
    if args['exchange'] is None:
        raise ValueError('Exchange was not set')


def ensure_security_type_is_set(args: t.Dict[str, t.Any]):
    if args['ust'] is None:
        raise ValueError('ust was not set')


def guess_exchange_and_ust(args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    if args['exchange'] is None:
        args['exchange'] = guess_exchange_from_symbol_intraday(args['symbol'])
    if args['ust'] is None:
        args['ust'] = guess_ust_from_symbol_intraday(args['symbol'])
    if args['ust'] is None:
        raise HTTPException(
            detail=(
                f'Could not identify `ust` from symbol {args["symbol"]}.'
                f' Is the symbol covered at all?'
                f' Try adding the exchange of the underlying `exchange`.'
            ),
            status_code=HTTP_400_BAD_REQUEST
        )
    if args['exchange'] is None:
        raise HTTPException(
            detail=(
                f'Could not identify `exchange` from symbol {args["symbol"]}.'
                f' Is the symbol covered at all?'
                f' Try adding the security type of the underlying `ust`.'
            ),
            status_code=HTTP_400_BAD_REQUEST
        )
    validate_config(args)
    return args


def guess_exchange_from_symbol_intraday(symbol: str) -> str:
    mapping = {
        'cme': intraday_prices_cme_sym_choices,
        'usetf': prices_etf_sym_choices,
        'int': prices_fx_sym_choices,
        'ice': iv_ice_choices
    }
    for exchange in list(mapping):
        if symbol.lower() in mapping[exchange]:
            return exchange


def guess_ust_from_symbol_intraday(symbol: str) -> str:
    mapping = {
        'fut': intraday_prices_cme_sym_choices,
        'eqt': prices_etf_sym_choices,
        'fx': prices_fx_sym_choices,
    }
    for ust in list(mapping):
        if symbol.lower() in mapping[ust]:
            return ust


async def add_missing_keys(keys: t.List[str], args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    for key in keys:
        if key not in list(args):
            args[key] = None
    return args


def eod_ini_logic_new(args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
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

    if 'enddate' not in args:
        args['enddate'] = dt.now().date()

    if args['enddate'] is None:
        args['enddate'] = dt.now().date()

    if 'startdate' not in args:
        args['startdate'] = (dt.combine(args['enddate'], dt.min.time()) - delta_d).date()

    if args['startdate'] is None:
        args['startdate'] = (dt.combine(args['enddate'], dt.min.time()) - delta_d).date()

    if args['startdate'] > args['enddate']:
        args['startdate'] = args['enddate']

    args['enddate'] = args['enddate'].strftime('%Y-%m-%d')
    args['startdate'] = args['startdate'].strftime('%Y-%m-%d')
    return args


async def put_call_trafo(args: t.Dict[str, t.Any]) -> t.Dict[str, t.Any]:
    if args['putcall'] == 'put':
        args['putcall'] = 0
    elif args['putcall'] == 'call':
        args['putcall'] = 1
    else:
        raise NotImplementedError()
    return args


class CinfoQueries:
    @staticmethod
    def ust_f():
        return '''
            SELECT DISTINCT ust AS ust
            FROM cinfo
            ORDER BY ust;
        '''

    @staticmethod
    def option_month_underlying_month_f(args: t.Dict[str, t.Any]) -> str:
        """ TODO why do we get duplicate values here?"""
        return f'''
        SELECT option_month, underlying_month
        FROM cinfo
        WHERE ust = '{args['ust']}'
            AND exchange = '{args['exchange']}'
            AND symbol = '{args['symbol']}'
            AND ltd = '{args['ltd']}';
            '''

    @staticmethod
    def first_and_last_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT
              (SELECT DISTINCT bizdt
               FROM {args['schema']}.{args['table']}
               ORDER BY bizdt
               LIMIT 1) AS first,
              (SELECT DISTINCT bizdt
               FROM {args['schema']}.{args['table']}
               ORDER BY bizdt DESC
               LIMIT 1) AS last
            FROM {args['schema']}.{args['table']}
            LIMIT 1;
        '''

    @staticmethod
    def ust_where_exchange_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT ust AS ust
            FROM cinfo
            WHERE exchange = '{args['exchange']}'
            ORDER BY ust;
        '''

    @staticmethod
    def ust_where_symbol_f(args: t.Dict[str, t.Any]):
        return f'''
            SELECT DISTINCT ust AS ust
            FROM cinfo
            WHERE symbol = '{args['symbol']}'
            ORDER BY ust;
        '''

    @staticmethod
    def exchange_f(args: t.Dict[str, t.Any]) -> str:
        return '''
            SELECT DISTINCT exchange AS exchange
            FROM cinfo
            ORDER BY exchange;
        '''

    @staticmethod
    def exchange_where_ust_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT exchange AS exchange
            FROM cinfo
            WHERE ust = '{args['ust']}'
            ORDER BY exchange;
        '''

    @staticmethod
    def exchange_where_symbol_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT exchange AS exchange
            FROM cinfo
            WHERE symbol = '{args['symbol']}'
            ORDER BY exchange;
        '''

    @staticmethod
    def symbol_f(args: t.Dict[str, t.Any]) -> str:
        return '''
            SELECT DISTINCT symbol AS symbol
            FROM cinfo
            ORDER BY symbol;
        '''

    @staticmethod
    def symbol_where_ust_f(args: t.Dict[str, t.Any]):
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM cinfo
            WHERE ust = '{args['ust']}'
            ORDER BY ust;
        '''

    @staticmethod
    def symbol_where_exchange_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM cinfo
            WHERE exchange = '{args['exchange']}'
            ORDER BY symbol;
        '''

    @staticmethod
    def symbol_where_ust_and_exchange_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT symbol AS symbol
            FROM            cinfo
            WHERE           exchange = '{args['exchange']}'
                AND         ust = '{args['ust']}'
            ORDER BY        symbol;
       '''

    @staticmethod
    def ltd_where_ust_exchange_and_symbol_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
        SELECT DISTINCT ltd AS ltd
        FROM            cinfo
        WHERE           symbol = '{args['symbol']}'
            AND         exchange = '{args['exchange']}'
            AND         ust = '{args['ust']}'
        ORDER BY        ltd;
       '''

    @staticmethod
    def ltd_date_where_ust_exchange_and_symbol_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
        SELECT DISTINCT ltd_date AS ltd
        FROM            cinfo
        WHERE           symbol = '{args['symbol']}'
            AND         exchange = '{args['exchange']}'
            AND         ust = '{args['ust']}'
        ORDER BY        ltd_date;
       '''

    @staticmethod
    def get_table_and_schema_by_ltd(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT schema_name, table_name
            FROM    cinfo
            WHERE   ust = '{args['ust']}'
                AND exchange = '{args['exchange']}'
                AND symbol = '{args['symbol']}'
                AND ltd = '{args['ltd']}';
        '''

    @staticmethod
    def get_table_and_schema_by_symbol(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT schema_name, table_name
            FROM    cinfo
            WHERE   ust = '{args['ust']}'
                AND exchange = '{args['exchange']}'
                AND symbol = '{args['symbol']}';
        '''

    @staticmethod
    def get_schema_and_table_for_futures_sql(args: t.Dict[str, t.Any]) -> str:
        return f'''
        SELECT schema_name, table_name
        FROM cinfo
        WHERE   symbol = '{args["symbol"]}'
            AND ust = '{args["ust"]}'
            AND exchange = '{args["exchange"]}'
            AND underlying_month = '{args["underlying_month"]}'
            AND option_month = '{args["option_month"]}'
            AND ltd = '{args["ltd"]}'
        LIMIT 1;
        '''

    @staticmethod
    def get_table_and_schema_by_month_and_year(args: t.Dict[str, t.Any]) -> str:
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
    def strikes_where_table_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT strkpx AS strike
            FROM {args['schema']}.{args['table']}
            ORDER BY strkpx;
        '''

    @staticmethod
    def strikes_where_table_and_pc_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT DISTINCT strkpx AS strike
            FROM {args['schema']}.{args['table']}
            WHERE putcall = {args['putcall']}
            ORDER BY strkpx;
        '''

    @staticmethod
    def first_and_last_date_where_putcall_and_strike_f(args: t.Dict[str, t.Any]) -> str:
        return f'''
            SELECT  MIN(BIZDT) as start_date,
                    MAX(bizdt) as last_date,
            FROM {args['schema']}.{args['table']}
            WHERE putcall = {args['putcall']}
            AND strkpx = {args['strkpx']}
            GROUP BY strkpx
            ORDER BY strkpx;
        '''
