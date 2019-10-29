from falib.const import prices_etf_sym_choices
from falib.const import prices_fx_sym_choices
from falib.const import iv_ice_choices
from falib.const import intraday_prices_cme_sym_choices


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
