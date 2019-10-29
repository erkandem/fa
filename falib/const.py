# ----------------------------------------------------------------------
# --- declare and define commonly used constants, lists, dicts etc here
# ----------------------------------------------------------------------


tte_choices = ['10d', '20d', '1m', '2m', '3m', '4m', '5m', '6m', '7m', '8m', '9m', '12m']

exchange_choices = ['cme', 'usetf', 'ice', 'eurex']
exchange_choices_intraday = ['cme', 'usetf', 'int']

offset_steps = [0, 5, 10, 15, 20, 25, 30, 35, 40]

ust_choices = ['eqt', 'fut', 'ind']
ust_choices_intraday = ['eqt', 'fut', 'fx']

iv_etf_choices = [
    'dia', 'eem', 'efa', 'ewj', 'eww', 'ewy', 'ewz', 'fez', 'fxe',
    'fxi', 'gdx', 'gdxj', 'gld', 'hyg', 'ibb', 'ief', 'iwm', 'iyr',
    'kre', 'qqq', 'rsx', 'slv', 'smh', 'spy', 'tlt', 'ung', 'uso',
    'vxx', 'xbi', 'xlb', 'xle', 'xlf', 'xli', 'xlp', 'xlu', 'xlv',
    'xly', 'xme', 'xop', 'xrt']

iv_cme_choices = [
    'ad', 'bo', 'bp', 'bz', 'c', 'cd', 'cl', 'ec', 'es',
    'fv', 'gc', 'ge', 'ge0', 'ge2', 'ge3', 'ge4', 'ge5', 'hg',
    'ho', 'jy', 'kw', 'lc', 'ln', 'ng', 'nq', 'rb', 's',
    'si', 'sm', 'tu', 'ty', 'us', 'w']

iv_eurex_choices_fut = ['bobl', 'bund', 'schatz', 'ovs2']
iv_eurex_choices_ind = ['dax', 'estx50', 'mdax', 'smi', 'tecdax']
iv_eurex_choices = iv_eurex_choices_fut + iv_eurex_choices_ind

iv_ice_choices = ['b', 'g']
nth_contract_choices = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
conti_futures_choices = ['cl', 'rb', 'ho', 'b', 'g']

iv_all_sym_choices = iv_etf_choices  + iv_cme_choices + iv_eurex_choices + iv_ice_choices

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
    :param m:
    :return:
    """
    if m in RAWOPTION_MAP:
        return RAWOPTION_MAP[m]
    else:
        return 'undprice'

# ----------------------------------------------------------------------
# --- conversion `from time til` expiry to `sql column ` to
# ----------------------------------------------------------------------


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

delta_choices = [
    'd010',
    'd015',
    'd020',
    'd025',
    'd030',
    'd035',
    'd040',
    'd045',
    'd050',
    'd055',
    'd060',
    'd065',
    'd070',
    'd075',
    'd080',
    'd085',
    'd090',
    'adjPC',
]


intraday_prices_cme_sym_choices = [
    'a6',
    'cl',
    'd6',
    'es',
    'e6',
    'gc',
    'ge',
    'gf',
    'he',
    'hg',
    'ho',
    'j6',
    'ke',
    'le',
    'm6',
    'n6',
    'ng',
    'nq',
    'qa',
    'rb',
    's6',
    'si',
    'tn',
    'ud',
    'zb',
    'zc',
    'zf',
    'zk',
    'zl',
    'zm',
    'zn',
    'zs',
    'zt',
    'zw',
]
cme_arg_list= [
    'symbol',
    'month',
    'year',
    'startdate',
    'enddate',
    'iunit',
    'interval',
    'order'
]

prices_fx_sym_choices = [
    'audusd',
    'eurusd',
    'gbpusd',
    'usdbrl',
    'usdcad',
    'usdchf',
    'usdcny',
    'usdjpy',
    'usdmxn',
    'usdnok',
    'usdrub',
    'usdsek',
    'dxy',
]

fx_arg_list= [
    'symbol',
    'startdate',
    'enddate',
    'iunit',
    'interval',
    'order'
]

prices_etf_sym_choices = [
    'dia',
    'eem',
    'efa',
    'ewj',
    'eww',
    'ewy',
    'ewz',
    'fez',
    'fxe',
    'fxi',
    'gdx',
    'gdxj',
    'gld',
    'hyg',
    'ibb',
    'ief',
    'iwm',
    'iyr',
    'kre',
    'qqq',
    'rsx',
    'slv',
    'smh',
    'spy',
    'tlt',
    'ung',
    'uso',
    'vxx',
    'xbi',
    'xlb',
    'xle',
    'xlf',
    'xli',
    'xlp',
    'xlu',
    'xlv',
    'xly',
    'xme',
    'xop',
    'xrt',
]

etf_arg_list = fx_arg_list

futures_month_chars = ['f', 'g', 'h', 'j', 'k', 'm', 'n', 'q', 'u', 'v', 'x', 'z']

prices_intraday_all_symbols = (
        prices_fx_sym_choices
        + prices_etf_sym_choices
        + intraday_prices_cme_sym_choices)
