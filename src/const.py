"""
 declare and define commonly used constants, lists, dicts etc here
"""
from collections import namedtuple
from enum import Enum

dminusLimits = namedtuple('dminusLimits', ['start', 'end'])

def get_values(enum_obj):
    """create vanilla list from enum values"""
    return [elm.value for elm in enum_obj]


def enum_class_string(obj_list, classname=None):  # pragma: no cover
    """ used during code migration from restplus to fast-api """
    if classname is None:
        classname = ''
    if type(obj_list[0]) is int:
        primitive = 'int'
    elif type(obj_list[0]) is str:
        primitive = 'str'
    else:
        raise TypeError
    header = f'class {classname}({primitive}, Enum):'
    if primitive == 'int':
        members = '\n    '.join([f"""_{e} = {e}""" for e in obj_list])
    elif primitive == 'str':
        members = '\n    '.join([f"""_{e} = '{e}'""" for e in obj_list])
    else:
        raise TypeError
    return f'{header}\n    {members}'


class IntervalUnits(str, Enum):
    _minutes = 'minutes'
    _hour = 'hour'
    _day = 'day'
    _week = 'week'
    _month = 'month'


class tteChoices(str, Enum):
    _10d = '10d'
    _20d = '20d'
    _1m = '1m'
    _2m = '2m'
    _3m = '3m'
    _4m = '4m'
    _5m = '5m'
    _6m = '6m'
    _7m = '7m'
    _8m = '8m'
    _9m = '9m'
    _12m = '12m'


class ExchangeChoices(str, Enum):
    _cme = 'cme'
    _usetf = 'usetf'
    _ice = 'ice'
    _eurex = 'eurex'


class ExchangeChoicesIntraday(str, Enum):
    _cme = 'cme'
    _usetf = 'usetf'
    _ice = 'int'


class offsetSteps(int, Enum):
    _0 = 0
    _5 = 5
    _10 = 10
    _15 = 15
    _20 = 20
    _25 = 25
    _30 = 30
    _35 = 35
    _40 = 40


class ustChoices(str, Enum):
    _eqt = 'eqt'
    _fut = 'fut'
    _ind = 'ind'


class ustChoicesIntraday(str, Enum):
    _eqt = 'eqt'
    _fut = 'fut'
    _fx = 'fx'


class iVolEtfChoices(str, Enum):
    _dia = 'dia'
    _eem = 'eem'
    _efa = 'efa'
    _ewj = 'ewj'
    _eww = 'eww'
    _ewy = 'ewy'
    _ewz = 'ewz'
    _fez = 'fez'
    _fxe = 'fxe'
    _fxi = 'fxi'
    _gdx = 'gdx'
    _gdxj = 'gdxj'
    _gld = 'gld'
    _hyg = 'hyg'
    _ibb = 'ibb'
    _ief = 'ief'
    _iwm = 'iwm'
    _iyr = 'iyr'
    _kre = 'kre'
    _qqq = 'qqq'
    _rsx = 'rsx'
    _slv = 'slv'
    _smh = 'smh'
    _spy = 'spy'
    _tlt = 'tlt'
    _ung = 'ung'
    _uso = 'uso'
    _vxx = 'vxx'
    _xbi = 'xbi'
    _xlb = 'xlb'
    _xle = 'xle'
    _xlf = 'xlf'
    _xli = 'xli'
    _xlp = 'xlp'
    _xlu = 'xlu'
    _xlv = 'xlv'
    _xly = 'xly'
    _xme = 'xme'
    _xop = 'xop'
    _xrt = 'xrt'


class iVolCmeChoices(str, Enum):
    _ad = 'ad'
    _bo = 'bo'
    _bp = 'bp'
    _bz = 'bz'
    _c = 'c'
    _cd = 'cd'
    _cl = 'cl'
    _ec = 'ec'
    _es = 'es'
    _fv = 'fv'
    _gc = 'gc'
    _ge = 'ge'
    _ge0 = 'ge0'
    _ge2 = 'ge2'
    _ge3 = 'ge3'
    _ge4 = 'ge4'
    _ge5 = 'ge5'
    _hg = 'hg'
    _ho = 'ho'
    _jy = 'jy'
    _kw = 'kw'
    _lc = 'lc'
    _ln = 'ln'
    _ng = 'ng'
    _nq = 'nq'
    _rb = 'rb'
    _s = 's'
    _si = 'si'
    _sm = 'sm'
    _tu = 'tu'
    _ty = 'ty'
    _us = 'us'
    _w = 'w'


class iVolEurexChoicesFut(str, Enum):
    _bobl = 'bobl'
    _bund = 'bund'
    _schatz = 'schatz'
    _ovs2 = 'ovs2'


class iVolEurexChoicesInd(str, Enum):
    _dax = 'dax'
    _estx50 = 'estx50'
    _mdax = 'mdax'
    _smi = 'smi'
    _tecdax = 'tecdax'


class iVolEurexChoices(str, Enum):
    _bobl = 'bobl'
    _bund = 'bund'
    _schatz = 'schatz'
    _ovs2 = 'ovs2'
    _dax = 'dax'
    _estx50 = 'estx50'
    _mdax = 'mdax'
    _smi = 'smi'
    _tecdax = 'tecdax'


class iVolChoicesIce(str, Enum):
    _b = 'b'  # 254 Brent Crude Futures
    _t = 't'  # 425 WTI Crude Futures
    _g = 'g'  # 5817 Gas Oil Futures
    _n = 'n'  # 495 NYH RBOB Gasoline
    _cc = 'cc'  # 578 Cocoa Futures
    _kc = 'kc'  # 580 Coffee C Futures
    _ct = 'cz'  # 588 Cotton No. 2 Futures
    _sb = 'sb'  # 582 Sugar No. 11 Futures


class nthContractChoices(int, Enum):
    _1 = 1
    _2 = 2
    _3 = 3
    _4 = 4
    _5 = 5
    _6 = 6
    _7 = 7
    _8 = 8
    _9 = 9
    _10 = 10
    _11 = 11
    _12 = 12


class contiFuturesChoices(str, Enum):
    _cl = 'cl'
    _rb = 'rb'
    _ho = 'ho'
    _b = 'b'
    _g = 'g'


class RawDataMetricChoices(str, Enum):
    _underlying_price = 'underlying_price'
    _settlement_price = 'settlement_price'
    _volume = 'volume'
    _open_interest = 'open_interest'
    _years_until_expiry = 'years_until_expiry'
    _moneyness = 'moneyness'
    _dividend_yield = 'dividend_yield'
    _riskfree_rate = 'riskfree_rate'
    _rawiv = 'rawiv'
    _delta = 'delta'
    _time_value = 'time_value'


RAWOPTION_MAP = {
    'underlying_price': 'undprice',
    'settlement_price': 'settleprice',
    'volume': 'volume',
    'open_interest': 'oi',
    'years_until_expiry': 'yte',
    'moneyness': 'moneyness',
    'dividend_yield': 'divyield',
    'riskfree_rate': 'rfr',
    'rawiv': 'rawiv',
    'delta': 'delta',
    'time_value': 'tv'
}


def metric_mapper_f(m):
    """
    map a database column name to a more human readable name
    """
    if m in RAWOPTION_MAP:
        return RAWOPTION_MAP[m]
    else:
        return 'undprice'


def time_to_var_func(tte):
    """map a database column name to a more human readable name"""
    if tte in list(time_to_var):
        return time_to_var[tte]
    else:
        raise KeyError


time_to_var = {
    '10d': 'var1',
    '20d': 'var2',
    '1m': 'var3',
    '2m': 'var4',
    '3m': 'var5',
    '4m': 'var6',
    '5m': 'var7',
    '6m': 'var8',
    '7m': 'var9',
    '8m': 'var10',
    '9m': 'var11',
    '12m': 'var12',
    '15m': 'var13',
    '18m': 'var14',
    '21m': 'var15',
    '24m': 'var16',
}


class deltaChoices(str, Enum):
    _d010 = 'd010'
    _d015 = 'd015'
    _d020 = 'd020'
    _d025 = 'd025'
    _d030 = 'd030'
    _d035 = 'd035'
    _d040 = 'd040'
    _d045 = 'd045'
    _d050 = 'd050'
    _d055 = 'd055'
    _d060 = 'd060'
    _d065 = 'd065'
    _d070 = 'd070'
    _d075 = 'd075'
    _d080 = 'd080'
    _d085 = 'd085'
    _d090 = 'd090'
    _adjPC = 'adjPC'


class deltaChoicesPractical(str, Enum):
    _d010 = 'd010'
    _d015 = 'd015'
    _d020 = 'd020'
    _d025 = 'd025'
    _d030 = 'd030'
    _d035 = 'd035'
    _d040 = 'd040'
    _d045 = 'd045'
    _d050 = 'd050'
    _d055 = 'd055'
    _d060 = 'd060'
    _d065 = 'd065'
    _d070 = 'd070'
    _d075 = 'd075'
    _d080 = 'd080'
    _d085 = 'd085'
    _d090 = 'd090'


class deltaOffsetChoices(str, Enum):
    _d5 = 5
    _d10 = 10
    _d15 = 15
    _d20 = 20
    _d25 = 25
    _d30 = 30
    _d35 = 35
    _d40 = 40


class intradayPricesCmeSymChoices(str, Enum):
    _a6 = 'a6'
    _cl = 'cl'
    _d6 = 'd6'
    _es = 'es'
    _e6 = 'e6'
    _gc = 'gc'
    _ge = 'ge'
    _gf = 'gf'
    _he = 'he'
    _hg = 'hg'
    _ho = 'ho'
    _j6 = 'j6'
    _ke = 'ke'
    _le = 'le'
    _m6 = 'm6'
    _n6 = 'n6'
    _ng = 'ng'
    _nq = 'nq'
    _qa = 'qa'
    _rb = 'rb'
    _s6 = 's6'
    _si = 'si'
    _tn = 'tn'
    _ud = 'ud'
    _zb = 'zb'
    _zc = 'zc'
    _zf = 'zf'
    _zk = 'zk'
    _zl = 'zl'
    _zm = 'zm'
    _zn = 'zn'
    _zs = 'zs'
    _zt = 'zt'
    _zw = 'zw'


class pricesFxSymChoices(str, Enum):
    _audusd = 'audusd'
    _eurusd = 'eurusd'
    _gbpusd = 'gbpusd'
    _usdbrl = 'usdbrl'
    _usdcad = 'usdcad'
    _usdchf = 'usdchf'
    _usdcny = 'usdcny'
    _usdjpy = 'usdjpy'
    _usdmxn = 'usdmxn'
    _usdnok = 'usdnok'
    _usdrub = 'usdrub'
    _usdsek = 'usdsek'
    _dxy = 'dxy'




class pricesEtfSymChoices(str, Enum):
    _dia = 'dia'
    _eem = 'eem'
    _efa = 'efa'
    _ewj = 'ewj'
    _eww = 'eww'
    _ewy = 'ewy'
    _ewz = 'ewz'
    _fez = 'fez'
    _fxe = 'fxe'
    _fxi = 'fxi'
    _gdx = 'gdx'
    _gdxj = 'gdxj'
    _gld = 'gld'
    _hyg = 'hyg'
    _ibb = 'ibb'
    _ief = 'ief'
    _iwm = 'iwm'
    _iyr = 'iyr'
    _kre = 'kre'
    _qqq = 'qqq'
    _rsx = 'rsx'
    _slv = 'slv'
    _smh = 'smh'
    _spy = 'spy'
    _tlt = 'tlt'
    _ung = 'ung'
    _uso = 'uso'
    _vxx = 'vxx'
    _xbi = 'xbi'
    _xlb = 'xlb'
    _xle = 'xle'
    _xlf = 'xlf'
    _xli = 'xli'
    _xlp = 'xlp'
    _xlu = 'xlu'
    _xlv = 'xlv'
    _xly = 'xly'
    _xme = 'xme'
    _xop = 'xop'
    _xrt = 'xrt'


class futuresMonthChars(str, Enum):
    _f = 'f'
    _g = 'g'
    _h = 'h'
    _j = 'j'
    _k = 'k'
    _m = 'm'
    _n = 'n'
    _q = 'q'
    _u = 'u'
    _v = 'v'
    _x = 'x'
    _z = 'z'


class OrderChoices(str, Enum):
    _asc = 'asc'
    _desc = 'desc'


class PutCallChoices(str, Enum):
    _put = 'put'
    _call = 'call'


class TopOiChoices(str, Enum):
    _volume = 'volume'
    _oi = 'oi'


pc_choices = get_values(PutCallChoices)
topoi_choices = get_values(TopOiChoices)

order_choices = get_values(OrderChoices)
futures_month_chars = get_values(futuresMonthChars)
prices_etf_sym_choices = get_values(pricesEtfSymChoices)
conti_futures_choices = get_values(contiFuturesChoices)
nth_contract_choices = get_values(nthContractChoices)
iv_eurex_choices_ind = get_values(iVolEurexChoicesInd)
iv_eurex_choices_fut = get_values(iVolEurexChoicesFut)
iv_etf_choices = get_values(iVolEtfChoices)
ust_choices = get_values(ustChoices)
ust_choices_intraday = get_values(ustChoicesIntraday)
tte_choices = get_values(tteChoices)
exchange_choices = get_values(ExchangeChoices)
exchange_choices_intraday = get_values(ExchangeChoicesIntraday)
iv_cme_choices = get_values(iVolCmeChoices)
intraday_prices_cme_sym_choices = get_values(intradayPricesCmeSymChoices)
delta_choices = get_values(deltaChoices)
delta_choices_practical = get_values(deltaChoicesPractical)
offset_steps = get_values(offsetSteps)
iv_eurex_choices = get_values(iVolEurexChoices)
iv_ice_choices = get_values(iVolChoicesIce)
prices_fx_sym_choices = get_values(pricesFxSymChoices)
delta_offset_choices  = enum_class_string(deltaOffsetChoices)

iv_all_sym_choices = iv_etf_choices + iv_cme_choices + iv_eurex_choices + iv_ice_choices


cme_arg_list = [
    'symbol',
    'month',
    'year',
    'startdate',
    'enddate',
    'iunit',
    'interval',
    'order'
]

fx_arg_list= [
    'symbol',
    'startdate',
    'enddate',
    'iunit',
    'interval',
    'order'
]
etf_arg_list = fx_arg_list


prices_intraday_all_symbols = (
        prices_fx_sym_choices
        + prices_etf_sym_choices
        + intraday_prices_cme_sym_choices)
