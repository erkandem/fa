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


STR_INTERVAL_MONTH = 'month'
STR_INTERVAL_WEEK = 'week'
STR_INTERVAL_HOUR = 'hour'
STR_INTERVAL_DAY = 'day'
STR_INTERVAL_MINUTES = 'minutes'


class IntervalUnitChoices(str, Enum):
    _month = STR_INTERVAL_MONTH
    _week = STR_INTERVAL_WEEK
    _hour = STR_INTERVAL_HOUR
    _day = STR_INTERVAL_DAY
    _minutes = STR_INTERVAL_MINUTES


STR_INTERVAL_VALUES_1 = '1'
STR_INTERVAL_VALUES_2 = '2'
STR_INTERVAL_VALUES_3 = '3'
STR_INTERVAL_VALUES_4 = '4'
STR_INTERVAL_VALUES_5 = '5'
STR_INTERVAL_VALUES_10 = '10'
STR_INTERVAL_VALUES_15 = '15'
STR_INTERVAL_VALUES_20 = '20'
STR_INTERVAL_VALUES_30 = '30'


class IntervalValueChoices(str, Enum):
    _1 = STR_INTERVAL_VALUES_1
    _2 = STR_INTERVAL_VALUES_2
    _3 = STR_INTERVAL_VALUES_3
    _4 = STR_INTERVAL_VALUES_4
    _5 = STR_INTERVAL_VALUES_5
    _10 = STR_INTERVAL_VALUES_10
    _15 = STR_INTERVAL_VALUES_15
    _20 = STR_INTERVAL_VALUES_20
    _30 = STR_INTERVAL_VALUES_30


STR_TIME_TILL_EXPIRY_10D = '10d'
STR_TIME_TILL_EXPIRY_20D = '20d'
STR_TIME_TILL_EXPIRY_1M = '1m'
STR_TIME_TILL_EXPIRY_2M = '2m'
STR_TIME_TILL_EXPIRY_3M = '3m'
STR_TIME_TILL_EXPIRY_4M = '4m'
STR_TIME_TILL_EXPIRY_5M = '5m'
STR_TIME_TILL_EXPIRY_6M = '6m'
STR_TIME_TILL_EXPIRY_7M = '7m'
STR_TIME_TILL_EXPIRY_8M = '8m'
STR_TIME_TILL_EXPIRY_9M = '9m'
STR_TIME_TILL_EXPIRY_12M = '12m'
STR_TIME_TILL_EXPIRY_15M = '15m'
STR_TIME_TILL_EXPIRY_18M = '18m'
STR_TIME_TILL_EXPIRY_21M = '21m'
STR_TIME_TILL_EXPIRY_24M = '24m'


class tteChoices(str, Enum):
    _10d = STR_TIME_TILL_EXPIRY_10D
    _20d = STR_TIME_TILL_EXPIRY_20D
    _1m = STR_TIME_TILL_EXPIRY_1M
    _2m = STR_TIME_TILL_EXPIRY_2M
    _3m = STR_TIME_TILL_EXPIRY_3M
    _4m = STR_TIME_TILL_EXPIRY_4M
    _5m = STR_TIME_TILL_EXPIRY_5M
    _6m = STR_TIME_TILL_EXPIRY_6M
    _7m = STR_TIME_TILL_EXPIRY_7M
    _8m = STR_TIME_TILL_EXPIRY_8M
    _9m = STR_TIME_TILL_EXPIRY_9M
    _12m = STR_TIME_TILL_EXPIRY_12M


STR_USETF_SYMBOL_DIA = 'dia'
STR_USETF_SYMBOL_EEM = 'eem'
STR_USETF_SYMBOL_EFA = 'efa'
STR_USETF_SYMBOL_EWJ = 'ewj'
STR_USETF_SYMBOL_EWW = 'eww'
STR_USETF_SYMBOL_EWY = 'ewy'
STR_USETF_SYMBOL_EWZ = 'ewz'
STR_USETF_SYMBOL_FEZ = 'fez'
STR_USETF_SYMBOL_FXE = 'fxe'
STR_USETF_SYMBOL_FXI = 'fxi'
STR_USETF_SYMBOL_GDX = 'gdx'
STR_USETF_SYMBOL_GDXJ = 'gdxj'
STR_USETF_SYMBOL_GLD = 'gld'
STR_USETF_SYMBOL_HYG = 'hyg'
STR_USETF_SYMBOL_IBB = 'ibb'
STR_USETF_SYMBOL_IEF = 'ief'
STR_USETF_SYMBOL_IWM = 'iwm'
STR_USETF_SYMBOL_IYR = 'iyr'
STR_USETF_SYMBOL_KRE = 'kre'
STR_USETF_SYMBOL_QQQ = 'qqq'
STR_USETF_SYMBOL_RSX = 'rsx'
STR_USETF_SYMBOL_SLV = 'slv'
STR_USETF_SYMBOL_SMH = 'smh'
STR_USETF_SYMBOL_SPY = 'spy'
STR_USETF_SYMBOL_TLT = 'tlt'
STR_USETF_SYMBOL_UNG = 'ung'
STR_USETF_SYMBOL_USO = 'uso'
STR_USETF_SYMBOL_VXX = 'vxx'
STR_USETF_SYMBOL_XBI = 'xbi'
STR_USETF_SYMBOL_XLB = 'xlb'
STR_USETF_SYMBOL_XLE = 'xle'
STR_USETF_SYMBOL_XLF = 'xlf'
STR_USETF_SYMBOL_XLI = 'xli'
STR_USETF_SYMBOL_XLP = 'xlp'
STR_USETF_SYMBOL_XLU = 'xlu'
STR_USETF_SYMBOL_XLV = 'xlv'
STR_USETF_SYMBOL_XLY = 'xly'
STR_USETF_SYMBOL_XME = 'xme'
STR_USETF_SYMBOL_XOP = 'xop'
STR_USETF_SYMBOL_XRT = 'xrt'

STR_EXCHANGE_CME = 'cme'
STR_EXCHANGE_USETF = 'usetf'
STR_EXCHANGE_ICE = 'ice'
STR_EXCHANGE_EUREX = 'eurex'


class ExchangeChoices(str, Enum):
    _cme = STR_EXCHANGE_CME
    _usetf = STR_EXCHANGE_USETF
    _ice = STR_EXCHANGE_ICE
    _eurex = STR_EXCHANGE_EUREX


class ExchangeChoicesIntraday(str, Enum):
    _cme = STR_EXCHANGE_CME
    _usetf = STR_EXCHANGE_USETF
    _ice = STR_EXCHANGE_ICE


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


STR_UNDERLYING_SECURITY_TYPE_EQUITY = 'eqt'
STR_UNDERLYING_SECURITY_TYPE_FUTURES = 'fut'
STR_UNDERLYING_SECURITY_TYPE_INDEX = 'ind'
STR_UNDERLYING_SECURITY_TYPE_FX = 'fx'


class ustChoices(str, Enum):
    _eqt = STR_UNDERLYING_SECURITY_TYPE_EQUITY
    _fut = STR_UNDERLYING_SECURITY_TYPE_FUTURES
    _ind = STR_UNDERLYING_SECURITY_TYPE_INDEX


class ustChoicesIntraday(str, Enum):
    _eqt = STR_UNDERLYING_SECURITY_TYPE_EQUITY
    _fut = STR_UNDERLYING_SECURITY_TYPE_FUTURES
    _fx = STR_UNDERLYING_SECURITY_TYPE_FX


class iVolEtfChoices(str, Enum):
    _dia = STR_USETF_SYMBOL_DIA
    _eem = STR_USETF_SYMBOL_EEM
    _efa = STR_USETF_SYMBOL_EFA
    _ewj = STR_USETF_SYMBOL_EWJ
    _eww = STR_USETF_SYMBOL_EWW
    _ewy = STR_USETF_SYMBOL_EWY
    _ewz = STR_USETF_SYMBOL_EWZ
    _fez = STR_USETF_SYMBOL_FEZ
    _fxe = STR_USETF_SYMBOL_FXE
    _fxi = STR_USETF_SYMBOL_FXI
    _gdx = STR_USETF_SYMBOL_GDX
    _gdxj = STR_USETF_SYMBOL_GDXJ
    _gld = STR_USETF_SYMBOL_GLD
    _hyg = STR_USETF_SYMBOL_HYG
    _ibb = STR_USETF_SYMBOL_IBB
    _ief = STR_USETF_SYMBOL_IEF
    _iwm = STR_USETF_SYMBOL_IWM
    _iyr = STR_USETF_SYMBOL_IYR
    _kre = STR_USETF_SYMBOL_KRE
    _qqq = STR_USETF_SYMBOL_QQQ
    _rsx = STR_USETF_SYMBOL_RSX
    _slv = STR_USETF_SYMBOL_SLV
    _smh = STR_USETF_SYMBOL_SMH
    _spy = STR_USETF_SYMBOL_SPY
    _tlt = STR_USETF_SYMBOL_TLT
    _ung = STR_USETF_SYMBOL_UNG
    _uso = STR_USETF_SYMBOL_USO
    # _vxx = STR_USETF_SYMBOL_VXX  # disable query, since data is of low quality
    _xbi = STR_USETF_SYMBOL_XBI
    _xlb = STR_USETF_SYMBOL_XLB
    _xle = STR_USETF_SYMBOL_XLE
    _xlf = STR_USETF_SYMBOL_XLF
    _xli = STR_USETF_SYMBOL_XLI
    _xlp = STR_USETF_SYMBOL_XLP
    _xlu = STR_USETF_SYMBOL_XLU
    _xlv = STR_USETF_SYMBOL_XLV
    _xly = STR_USETF_SYMBOL_XLY
    _xme = STR_USETF_SYMBOL_XME
    _xop = STR_USETF_SYMBOL_XOP
    _xrt = STR_USETF_SYMBOL_XRT


STR_CME_SYMBOL_AD = 'ad'
STR_CME_SYMBOL_BO = 'bo'
STR_CME_SYMBOL_BP = 'bp'
STR_CME_SYMBOL_BZ = 'bz'
STR_CME_SYMBOL_C = 'c'
STR_CME_SYMBOL_CD = 'cd'
STR_CME_SYMBOL_CL = 'cl'
STR_CME_SYMBOL_EC = 'ec'
STR_CME_SYMBOL_ES = 'es'
STR_CME_SYMBOL_FV = 'fv'
STR_CME_SYMBOL_GC = 'gc'
STR_CME_SYMBOL_GE = 'ge'
STR_CME_SYMBOL_GE0 = 'ge0'
STR_CME_SYMBOL_GE2 = 'ge2'
STR_CME_SYMBOL_GE3 = 'ge3'
STR_CME_SYMBOL_GE4 = 'ge4'
STR_CME_SYMBOL_GE5 = 'ge5'
STR_CME_SYMBOL_HG = 'hg'
STR_CME_SYMBOL_HO = 'ho'
STR_CME_SYMBOL_JY = 'jy'
STR_CME_SYMBOL_KW = 'kw'
STR_CME_SYMBOL_LC = 'lc'
STR_CME_SYMBOL_LN = 'ln'
STR_CME_SYMBOL_NG = 'ng'
STR_CME_SYMBOL_NQ = 'nq'
STR_CME_SYMBOL_RB = 'rb'
STR_CME_SYMBOL_S = 's'
STR_CME_SYMBOL_SI = 'si'
STR_CME_SYMBOL_SM = 'sm'
STR_CME_SYMBOL_TU = 'tu'
STR_CME_SYMBOL_TY = 'ty'
STR_CME_SYMBOL_US = 'us'
STR_CME_SYMBOL_W = 'w'


class iVolCmeChoices(str, Enum):
    _ad = STR_CME_SYMBOL_AD
    _bo = STR_CME_SYMBOL_BO
    _bp = STR_CME_SYMBOL_BP
    _bz = STR_CME_SYMBOL_BZ
    _c = STR_CME_SYMBOL_C
    _cd = STR_CME_SYMBOL_CD
    _cl = STR_CME_SYMBOL_CL
    _ec = STR_CME_SYMBOL_EC
    _es = STR_CME_SYMBOL_ES
    _fv = STR_CME_SYMBOL_FV
    _gc = STR_CME_SYMBOL_GC
    _ge = STR_CME_SYMBOL_GE
    _ge0 = STR_CME_SYMBOL_GE0
    _ge2 = STR_CME_SYMBOL_GE2
    _ge3 = STR_CME_SYMBOL_GE3
    _ge4 = STR_CME_SYMBOL_GE4
    _ge5 = STR_CME_SYMBOL_GE5
    _hg = STR_CME_SYMBOL_HG
    _ho = STR_CME_SYMBOL_HO
    _jy = STR_CME_SYMBOL_JY
    _kw = STR_CME_SYMBOL_KW
    _lc = STR_CME_SYMBOL_LC
    _ln = STR_CME_SYMBOL_LN
    _ng = STR_CME_SYMBOL_NG
    _nq = STR_CME_SYMBOL_NQ
    _rb = STR_CME_SYMBOL_RB
    _s = STR_CME_SYMBOL_S
    _si = STR_CME_SYMBOL_SI
    _sm = STR_CME_SYMBOL_SM
    _tu = STR_CME_SYMBOL_TU
    _ty = STR_CME_SYMBOL_TY
    _us = STR_CME_SYMBOL_US
    _w = STR_CME_SYMBOL_W


STR_EUREX_SYMBOL_BOBL = 'bobl'
STR_EUREX_SYMBOL_BUND = 'bund'
STR_EUREX_SYMBOL_SCHATZ = 'schatz'
STR_EUREX_SYMBOL_OVS2 = 'ovs2'
STR_EUREX_SYMBOL_DAX = 'dax'
STR_EUREX_SYMBOL_ESTX50 = 'estx50'
STR_EUREX_SYMBOL_MDAX = 'mdax'
STR_EUREX_SYMBOL_SMI = 'smi'
STR_EUREX_SYMBOL_TECDAX = 'tecdax'


class iVolEurexChoicesFut(str, Enum):
    _bobl = STR_EUREX_SYMBOL_BOBL
    _bund = STR_EUREX_SYMBOL_BUND
    _schatz = STR_EUREX_SYMBOL_SCHATZ
    _ovs2 = STR_EUREX_SYMBOL_OVS2


class iVolEurexChoicesInd(str, Enum):
    _dax = STR_EUREX_SYMBOL_DAX
    _estx50 = STR_EUREX_SYMBOL_ESTX50
    _mdax = STR_EUREX_SYMBOL_MDAX
    _smi = STR_EUREX_SYMBOL_SMI
    _tecdax = STR_EUREX_SYMBOL_TECDAX


class iVolEurexChoices(str, Enum):
    _bobl = STR_EUREX_SYMBOL_BOBL
    _bund = STR_EUREX_SYMBOL_BUND
    _schatz = STR_EUREX_SYMBOL_SCHATZ
    _ovs2 = STR_EUREX_SYMBOL_OVS2
    _dax = STR_EUREX_SYMBOL_DAX
    _estx50 = STR_EUREX_SYMBOL_ESTX50
    _mdax = STR_EUREX_SYMBOL_MDAX
    _smi = STR_EUREX_SYMBOL_SMI
    _tecdax = STR_EUREX_SYMBOL_TECDAX


STR_ICE_SYMBOL_B = 'b'  # 254 Brent Crude Futures
STR_ICE_SYMBOL_T = 't'  # 425 WTI Crude Futures
STR_ICE_SYMBOL_G = 'g'  # 5817 Gas Oil Futures
STR_ICE_SYMBOL_N = 'n'  # 495 NYH RBOB Gasoline
STR_ICE_SYMBOL_CC = 'cc'  # 578 Cocoa Futures
STR_ICE_SYMBOL_KC = 'kc'  # 580 Coffee C Futures
STR_ICE_SYMBOL_CZ = 'cz'  # 588 Cotton No. 2 Futures
STR_ICE_SYMBOL_SB = 'sb'  # 582 Sugar No. 11 Futures


class iVolChoicesIce(str, Enum):
    _b = STR_ICE_SYMBOL_B
    _t = STR_ICE_SYMBOL_T
    _g = STR_ICE_SYMBOL_G
    _n = STR_ICE_SYMBOL_N
    _cc = STR_ICE_SYMBOL_CC
    _kc = STR_ICE_SYMBOL_KC
    _ct = STR_ICE_SYMBOL_CZ
    _sb = STR_ICE_SYMBOL_SB


STR_NTH_CONTRACT_ONE = 1
STR_NTH_CONTRACT_TWO = 2
STR_NTH_CONTRACT_THREE = 3
STR_NTH_CONTRACT_FOUR = 4
STR_NTH_CONTRACT_FIVE = 5
STR_NTH_CONTRACT_SIX = 6
STR_NTH_CONTRACT_SEVEN = 7
STR_NTH_CONTRACT_EIGHT = 8
STR_NTH_CONTRACT_NINE = 9
STR_NTH_CONTRACT_TEN = 10
STR_NTH_CONTRACT_ELEVEN = 11
STR_NTH_CONTRACT_TWELVE = 12
STR_NTH_CONTRACT_THIRTEEN = 13
STR_NTH_CONTRACT_FOURTEEN = 14
STR_NTH_CONTRACT_FITHTEEN = 15
STR_NTH_CONTRACT_SIXTEEN = 16
STR_NTH_CONTRACT_SEVENTEEN = 17
STR_NTH_CONTRACT_EIGHTTEEN = 18
STR_NTH_CONTRACT_NINETEEN = 19
STR_NTH_CONTRACT_TWENTY = 20
STR_NTH_CONTRACT_TWENTYONE = 21
STR_NTH_CONTRACT_TWENTYTWO = 22
STR_NTH_CONTRACT_TWENTYTHREE = 23
STR_NTH_CONTRACT_TWENTYFOUR = 24


class nthContractChoices(int, Enum):
    _1 = STR_NTH_CONTRACT_ONE
    _2 = STR_NTH_CONTRACT_TWO
    _3 = STR_NTH_CONTRACT_THREE
    _4 = STR_NTH_CONTRACT_FOUR
    _5 = STR_NTH_CONTRACT_FIVE
    _6 = STR_NTH_CONTRACT_SIX
    _7 = STR_NTH_CONTRACT_SEVEN
    _8 = STR_NTH_CONTRACT_EIGHT
    _9 = STR_NTH_CONTRACT_NINE
    _10 = STR_NTH_CONTRACT_TEN
    _11 = STR_NTH_CONTRACT_ELEVEN
    _12 = STR_NTH_CONTRACT_TWELVE


class contiFuturesChoices(str, Enum):
    _cl = STR_CME_SYMBOL_CL
    _rb = STR_CME_SYMBOL_RB
    _ho = STR_CME_SYMBOL_HO
    _b = STR_ICE_SYMBOL_B
    _g = STR_ICE_SYMBOL_G


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
    # mapping between publicly exposed human readable column names and
    # database column name
    STR_TIME_TILL_EXPIRY_10D: 'var1',
    STR_TIME_TILL_EXPIRY_20D: 'var2',
    STR_TIME_TILL_EXPIRY_1M: 'var3',
    STR_TIME_TILL_EXPIRY_2M: 'var4',
    STR_TIME_TILL_EXPIRY_3M: 'var5',
    STR_TIME_TILL_EXPIRY_4M: 'var6',
    STR_TIME_TILL_EXPIRY_5M: 'var7',
    STR_TIME_TILL_EXPIRY_6M: 'var8',
    STR_TIME_TILL_EXPIRY_7M: 'var9',
    STR_TIME_TILL_EXPIRY_8M: 'var10',
    STR_TIME_TILL_EXPIRY_9M: 'var11',
    STR_TIME_TILL_EXPIRY_12M: 'var12',
    STR_TIME_TILL_EXPIRY_15M: 'var13',
    STR_TIME_TILL_EXPIRY_18M: 'var14',
    STR_TIME_TILL_EXPIRY_21M: 'var15',
    STR_TIME_TILL_EXPIRY_24M: 'var16',
}

STR_DELTA_CHOICES_D010 = 'd010'
STR_DELTA_CHOICES_D015 = 'd015'
STR_DELTA_CHOICES_D020 = 'd020'
STR_DELTA_CHOICES_D025 = 'd025'
STR_DELTA_CHOICES_D030 = 'd030'
STR_DELTA_CHOICES_D035 = 'd035'
STR_DELTA_CHOICES_D040 = 'd040'
STR_DELTA_CHOICES_D045 = 'd045'
STR_DELTA_CHOICES_D050 = 'd050'
STR_DELTA_CHOICES_D055 = 'd055'
STR_DELTA_CHOICES_D060 = 'd060'
STR_DELTA_CHOICES_D065 = 'd065'
STR_DELTA_CHOICES_D070 = 'd070'
STR_DELTA_CHOICES_D075 = 'd075'
STR_DELTA_CHOICES_D080 = 'd080'
STR_DELTA_CHOICES_D085 = 'd085'
STR_DELTA_CHOICES_D090 = 'd090'
STR_DELTA_CHOICES_ADJUSTMENT = 'adjPC'


class deltaChoices(str, Enum):
    _d010 = STR_DELTA_CHOICES_D010
    _d015 = STR_DELTA_CHOICES_D015
    _d020 = STR_DELTA_CHOICES_D020
    _d025 = STR_DELTA_CHOICES_D025
    _d030 = STR_DELTA_CHOICES_D030
    _d035 = STR_DELTA_CHOICES_D035
    _d040 = STR_DELTA_CHOICES_D040
    _d045 = STR_DELTA_CHOICES_D045
    _d050 = STR_DELTA_CHOICES_D050
    _d055 = STR_DELTA_CHOICES_D055
    _d060 = STR_DELTA_CHOICES_D060
    _d065 = STR_DELTA_CHOICES_D065
    _d070 = STR_DELTA_CHOICES_D070
    _d075 = STR_DELTA_CHOICES_D075
    _d080 = STR_DELTA_CHOICES_D080
    _d085 = STR_DELTA_CHOICES_D085
    _d090 = STR_DELTA_CHOICES_D090
    _adjPC = STR_DELTA_CHOICES_ADJUSTMENT


class deltaChoicesPractical(str, Enum):
    _d010 = STR_DELTA_CHOICES_D010
    _d015 = STR_DELTA_CHOICES_D015
    _d020 = STR_DELTA_CHOICES_D020
    _d025 = STR_DELTA_CHOICES_D025
    _d030 = STR_DELTA_CHOICES_D030
    _d035 = STR_DELTA_CHOICES_D035
    _d040 = STR_DELTA_CHOICES_D040
    _d045 = STR_DELTA_CHOICES_D045
    _d050 = STR_DELTA_CHOICES_D050
    _d055 = STR_DELTA_CHOICES_D055
    _d060 = STR_DELTA_CHOICES_D060
    _d065 = STR_DELTA_CHOICES_D065
    _d070 = STR_DELTA_CHOICES_D070
    _d075 = STR_DELTA_CHOICES_D075
    _d080 = STR_DELTA_CHOICES_D080
    _d085 = STR_DELTA_CHOICES_D085
    _d090 = STR_DELTA_CHOICES_D090


STR_DELTA_OFFSET_D000 = '0'
STR_DELTA_OFFSET_D005 = '5'
STR_DELTA_OFFSET_D010 = '10'
STR_DELTA_OFFSET_D015 = '15'
STR_DELTA_OFFSET_D020 = '20'
STR_DELTA_OFFSET_D025 = '25'
STR_DELTA_OFFSET_D030 = '30'
STR_DELTA_OFFSET_D035 = '35'
STR_DELTA_OFFSET_D040 = '40'


class deltaOffsetChoices(str, Enum):
    _d0 = STR_DELTA_OFFSET_D000
    _d5 = STR_DELTA_OFFSET_D005
    _d10 = STR_DELTA_OFFSET_D010
    _d15 = STR_DELTA_OFFSET_D015
    _d20 = STR_DELTA_OFFSET_D020
    _d25 = STR_DELTA_OFFSET_D025
    _d30 = STR_DELTA_OFFSET_D030
    _d35 = STR_DELTA_OFFSET_D035
    _d40 = STR_DELTA_OFFSET_D040


STR_INTRADAY_PRICES_SYMBOL_A6 = 'a6'
STR_INTRADAY_PRICES_SYMBOL_CL = 'cl'
STR_INTRADAY_PRICES_SYMBOL_D6 = 'd6'
STR_INTRADAY_PRICES_SYMBOL_ES = 'es'
STR_INTRADAY_PRICES_SYMBOL_E6 = 'e6'
STR_INTRADAY_PRICES_SYMBOL_GC = 'gc'
STR_INTRADAY_PRICES_SYMBOL_GE = 'ge'
STR_INTRADAY_PRICES_SYMBOL_GF = 'gf'
STR_INTRADAY_PRICES_SYMBOL_HE = 'he'
STR_INTRADAY_PRICES_SYMBOL_HG = 'hg'
STR_INTRADAY_PRICES_SYMBOL_HO = 'ho'
STR_INTRADAY_PRICES_SYMBOL_J6 = 'j6'
STR_INTRADAY_PRICES_SYMBOL_KE = 'ke'
STR_INTRADAY_PRICES_SYMBOL_LE = 'le'
STR_INTRADAY_PRICES_SYMBOL_M6 = 'm6'
STR_INTRADAY_PRICES_SYMBOL_N6 = 'n6'
STR_INTRADAY_PRICES_SYMBOL_NG = 'ng'
STR_INTRADAY_PRICES_SYMBOL_NQ = 'nq'
STR_INTRADAY_PRICES_SYMBOL_QA = 'qa'
STR_INTRADAY_PRICES_SYMBOL_RB = 'rb'
STR_INTRADAY_PRICES_SYMBOL_S6 = 's6'
STR_INTRADAY_PRICES_SYMBOL_SI = 'si'
STR_INTRADAY_PRICES_SYMBOL_TN = 'tn'
STR_INTRADAY_PRICES_SYMBOL_UD = 'ud'
STR_INTRADAY_PRICES_SYMBOL_ZB = 'zb'
STR_INTRADAY_PRICES_SYMBOL_ZC = 'zc'
STR_INTRADAY_PRICES_SYMBOL_ZF = 'zf'
STR_INTRADAY_PRICES_SYMBOL_ZK = 'zk'
STR_INTRADAY_PRICES_SYMBOL_ZL = 'zl'
STR_INTRADAY_PRICES_SYMBOL_ZM = 'zm'
STR_INTRADAY_PRICES_SYMBOL_ZN = 'zn'
STR_INTRADAY_PRICES_SYMBOL_ZS = 'zs'
STR_INTRADAY_PRICES_SYMBOL_ZT = 'zt'
STR_INTRADAY_PRICES_SYMBOL_ZW = 'zw'


class intradayPricesCmeSymChoices(str, Enum):
    _a6 = STR_INTRADAY_PRICES_SYMBOL_A6
    _cl = STR_INTRADAY_PRICES_SYMBOL_CL
    _d6 = STR_INTRADAY_PRICES_SYMBOL_D6
    _es = STR_INTRADAY_PRICES_SYMBOL_ES
    _e6 = STR_INTRADAY_PRICES_SYMBOL_E6
    _gc = STR_INTRADAY_PRICES_SYMBOL_GC
    _ge = STR_INTRADAY_PRICES_SYMBOL_GE
    _gf = STR_INTRADAY_PRICES_SYMBOL_GF
    _he = STR_INTRADAY_PRICES_SYMBOL_HE
    _hg = STR_INTRADAY_PRICES_SYMBOL_HG
    _ho = STR_INTRADAY_PRICES_SYMBOL_HO
    _j6 = STR_INTRADAY_PRICES_SYMBOL_J6
    _ke = STR_INTRADAY_PRICES_SYMBOL_KE
    _le = STR_INTRADAY_PRICES_SYMBOL_LE
    _m6 = STR_INTRADAY_PRICES_SYMBOL_M6
    _n6 = STR_INTRADAY_PRICES_SYMBOL_N6
    _ng = STR_INTRADAY_PRICES_SYMBOL_NG
    _nq = STR_CME_SYMBOL_NQ
    _qa = STR_INTRADAY_PRICES_SYMBOL_QA
    _rb = STR_INTRADAY_PRICES_SYMBOL_RB
    _s6 = STR_INTRADAY_PRICES_SYMBOL_S6
    _si = STR_INTRADAY_PRICES_SYMBOL_SI
    _tn = STR_INTRADAY_PRICES_SYMBOL_TN
    _ud = STR_INTRADAY_PRICES_SYMBOL_UD
    _zb = STR_INTRADAY_PRICES_SYMBOL_ZB
    _zc = STR_INTRADAY_PRICES_SYMBOL_ZC
    _zf = STR_INTRADAY_PRICES_SYMBOL_ZF
    _zk = STR_INTRADAY_PRICES_SYMBOL_ZK
    _zl = STR_INTRADAY_PRICES_SYMBOL_ZL
    _zm = STR_INTRADAY_PRICES_SYMBOL_ZM
    _zn = STR_INTRADAY_PRICES_SYMBOL_ZN
    _zs = STR_INTRADAY_PRICES_SYMBOL_ZS
    _zt = STR_INTRADAY_PRICES_SYMBOL_ZT
    _zw = STR_INTRADAY_PRICES_SYMBOL_ZW


STR_FX_SYMBOL_AUDUSD = 'audusd'
STR_FX_SYMBOL_EURUSD = 'eurusd'
STR_FX_SYMBOL_GBPUSD = 'gbpusd'
STR_FX_SYMBOL_USDBRL = 'usdbrl'
STR_FX_SYMBOL_USDCAD = 'usdcad'
STR_FX_SYMBOL_USDCHF = 'usdchf'
STR_FX_SYMBOL_USDCNY = 'usdcny'
STR_FX_SYMBOL_USDJPY = 'usdjpy'
STR_FX_SYMBOL_USDMXN = 'usdmxn'
STR_FX_SYMBOL_USDNOK = 'usdnok'
STR_FX_SYMBOL_USDRUB = 'usdrub'
STR_FX_SYMBOL_USDSEK = 'usdsek'
STR_FX_SYMBOL_DXY = 'dxy'


class pricesFxSymChoices(str, Enum):
    _audusd = STR_FX_SYMBOL_AUDUSD
    _eurusd = STR_FX_SYMBOL_EURUSD
    _gbpusd = STR_FX_SYMBOL_GBPUSD
    _usdbrl = STR_FX_SYMBOL_USDBRL
    _usdcad = STR_FX_SYMBOL_USDCAD
    _usdchf = STR_FX_SYMBOL_USDCHF
    _usdcny = STR_FX_SYMBOL_USDCNY
    _usdjpy = STR_FX_SYMBOL_USDJPY
    _usdmxn = STR_FX_SYMBOL_USDMXN
    _usdnok = STR_FX_SYMBOL_USDNOK
    _usdrub = STR_FX_SYMBOL_USDRUB
    _usdsek = STR_FX_SYMBOL_USDSEK
    _dxy = STR_FX_SYMBOL_DXY


class pricesEtfSymChoices(str, Enum):
    _dia = STR_USETF_SYMBOL_DIA
    _eem = STR_USETF_SYMBOL_EEM
    _efa = STR_USETF_SYMBOL_EFA
    _ewj = STR_USETF_SYMBOL_EWJ
    _eww = STR_USETF_SYMBOL_EWW
    _ewy = STR_USETF_SYMBOL_EWY
    _ewz = STR_USETF_SYMBOL_EWZ
    _fez = STR_USETF_SYMBOL_FEZ
    _fxe = STR_USETF_SYMBOL_FXE
    _fxi = STR_USETF_SYMBOL_FXI
    _gdx = STR_USETF_SYMBOL_GDX
    _gdxj = STR_USETF_SYMBOL_GDXJ
    _gld = STR_USETF_SYMBOL_GLD
    _hyg = STR_USETF_SYMBOL_HYG
    _ibb = STR_USETF_SYMBOL_IBB
    _ief = STR_USETF_SYMBOL_IEF
    _iwm = STR_USETF_SYMBOL_IWM
    _iyr = STR_USETF_SYMBOL_IYR
    _kre = STR_USETF_SYMBOL_KRE
    _qqq = STR_USETF_SYMBOL_QQQ
    _rsx = STR_USETF_SYMBOL_RSX
    _slv = STR_USETF_SYMBOL_SLV
    _smh = STR_USETF_SYMBOL_SMH
    _spy = STR_USETF_SYMBOL_SPY
    _tlt = STR_USETF_SYMBOL_TLT
    _ung = STR_USETF_SYMBOL_UNG
    _uso = STR_USETF_SYMBOL_USO
    _vxx = STR_USETF_SYMBOL_VXX
    _xbi = STR_USETF_SYMBOL_XBI
    _xlb = STR_USETF_SYMBOL_XLB
    _xle = STR_USETF_SYMBOL_XLE
    _xlf = STR_USETF_SYMBOL_XLF
    _xli = STR_USETF_SYMBOL_XLI
    _xlp = STR_USETF_SYMBOL_XLP
    _xlu = STR_USETF_SYMBOL_XLU
    _xlv = STR_USETF_SYMBOL_XLV
    _xly = STR_USETF_SYMBOL_XLY
    _xme = STR_USETF_SYMBOL_XME
    _xop = STR_USETF_SYMBOL_XOP
    _xrt = STR_USETF_SYMBOL_XRT


STR_FUTURES_MONTH_JANUARY = 'f'
STR_FUTURES_MONTH_FEBRUARY = 'g'
STR_FUTURES_MONTH_MARCH = 'h'
STR_FUTURES_MONTH_APRIL = 'j'
STR_FUTURES_MONTH_MAY = 'k'
STR_FUTURES_MONTH_JUNE = 'm'
STR_FUTURES_MONTH_JULY = 'n'
STR_FUTURES_MONTH_AUGUST = 'q'
STR_FUTURES_MONTH_SEPTEMBER = 'u'
STR_FUTURES_MONTH_OCTOBER = 'v'
STR_FUTURES_MONTH_NOVEMBER = 'x'
STR_FUTURES_MONTH_DECEMBER = 'z'


class futuresMonthChars(str, Enum):
    _f = STR_FUTURES_MONTH_JANUARY
    _g = STR_FUTURES_MONTH_FEBRUARY
    _h = STR_FUTURES_MONTH_MARCH
    _j = STR_FUTURES_MONTH_APRIL
    _k = STR_FUTURES_MONTH_MAY
    _m = STR_FUTURES_MONTH_JUNE
    _n = STR_FUTURES_MONTH_JULY
    _q = STR_FUTURES_MONTH_AUGUST
    _u = STR_FUTURES_MONTH_SEPTEMBER
    _v = STR_FUTURES_MONTH_OCTOBER
    _x = STR_FUTURES_MONTH_NOVEMBER
    _z = STR_FUTURES_MONTH_DECEMBER


STR_ORDERING_ASC = 'asc'
STR_ORDERING_DESC = 'desc'


class OrderChoices(str, Enum):
    _asc = STR_ORDERING_ASC
    _desc = STR_ORDERING_DESC


STR_PUT = 'put'
STR_CALL = 'call'


class PutCallChoices(str, Enum):
    _put = STR_PUT
    _call = STR_CALL


STR_VOLUME = 'volume'
STR_OPEN_INTEREST = 'oi'


class TopOiChoices(str, Enum):
    _volume = STR_VOLUME
    _oi = STR_OPEN_INTEREST


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
delta_offset_choices = get_values(deltaOffsetChoices)
interval_value_choices = get_values(IntervalValueChoices)
interval_unit_choices = get_values(IntervalUnitChoices)

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

fx_arg_list = [
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
        + intraday_prices_cme_sym_choices
)
