"""
 declare and define commonly used constants, lists, dicts etc here
"""
from enum import Enum


def extracted_values_from_enum():
    """create vanilla list from enum values"""
    return [elm.value for elm in tteChoices]


def enum_class_string(obj_list, classname=None):
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
    _b = 'b'
    _g = 'g'


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
        return time_to_var[time_to_var]
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

futures_month_chars = extracted_values_from_enum(futuresMonthChars)
prices_etf_sym_choices = extracted_values_from_enum(pricesEtfSymChoices)
conti_futures_choices = extracted_values_from_enum(contiFuturesChoices)
nth_contract_choices = extracted_values_from_enum(nthContractChoices)
iv_eurex_choices_ind = extracted_values_from_enum(iVolEurexChoicesInd)
iv_eurex_choices_fut = extracted_values_from_enum(iVolEurexChoicesFut)
iv_etf_choices = extracted_values_from_enum(iVolEtfChoices)
ust_choices = extracted_values_from_enum(ustChoices)
ust_choices_intraday = extracted_values_from_enum(ustChoicesIntraday)
tte_choices = extracted_values_from_enum(tteChoices)
exchange_choices = extracted_values_from_enum(ExchangeChoices)
exchange_choices_intraday = extracted_values_from_enum(ExchangeChoicesIntraday)
iv_cme_choices = extracted_values_from_enum(iVolCmeChoices)
intraday_prices_cme_sym_choices = extracted_values_from_enum(intradayPricesCmeSymChoices)
delta_choices = extracted_values_from_enum(deltaChoices)
offset_steps = extracted_values_from_enum(offsetSteps)
iv_eurex_choices = extracted_values_from_enum(iVolEurexChoices)
iv_ice_choices = extracted_values_from_enum(iVolChoicesIce)
iv_all_sym_choices = iv_etf_choices + iv_cme_choices + iv_eurex_choices + iv_ice_choices
prices_fx_sym_choices = extracted_values_from_enum(pricesFxSymChoices)



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
