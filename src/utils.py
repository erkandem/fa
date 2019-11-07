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