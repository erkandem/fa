from collections import namedtuple
from starlette.status import  HTTP_400_BAD_REQUEST
from starlette.exceptions import  HTTPException

BaseContract = namedtuple(
    'BaseContract',
    ['ust', 'exchange', 'symbol']
)

ALLOWED_SECURITY_TYPES = [
    "eqt",
    "fut",
    "ind"
]

ALLOWED_EXCHANGES = [
    {
        'security_type': 'ind',
        'exchanges': ["eurex"],
    },
    {
        'security_type': 'fut',
        'exchanges': ["cme", "eurex", "ice"]
    },
    {
        'security_type': 'eqt',
        'exchanges': ["usetf", "usyh"]
    }
]

ALLOWED_CONFIGS_DICT = [
    {'ust': 'ind', 'exchange': 'eurex', 'symbol': 'dax'},
    {'ust': 'ind', 'exchange': 'eurex', 'symbol': 'estx50'},
    {'ust': 'ind', 'exchange': 'eurex', 'symbol': 'mdax'},
    {'ust': 'ind', 'exchange': 'eurex', 'symbol': 'smi'},
    {'ust': 'ind', 'exchange': 'eurex', 'symbol': 'tecdax'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'ad'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'bo'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'bp'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'bz'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'c'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'cd'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'cl'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'ec'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'es'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'fv'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'gc'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'hg'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'ho'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'jy'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'kw'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'lc'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'ln'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'ng'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'nq'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'rb'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 's'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'si'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'sm'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'tu'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'ty'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'us'},
    {'ust': 'fut', 'exchange': 'cme', 'symbol': 'w'},
    {'ust': 'fut', 'exchange': 'eurex', 'symbol': 'bobl'},
    {'ust': 'fut', 'exchange': 'eurex', 'symbol': 'bund'},
    {'ust': 'fut', 'exchange': 'eurex', 'symbol': 'schatz'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'b'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'cc'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'ct'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'g'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'kc'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'n'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 'sb'},
    {'ust': 'fut', 'exchange': 'ice', 'symbol': 't'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'dia'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'eem'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'efa'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'ewj'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'eww'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'ewy'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'ewz'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'fez'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'fxe'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'fxi'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'gdx'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'gdxj'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'gld'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'hyg'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'ibb'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'ief'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'iwm'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'iyr'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'kre'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'qqq'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'rsx'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'slv'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'smh'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'spy'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'tlt'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'ung'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'uso'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xbi'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xlb'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xle'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xlf'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xli'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xlp'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xlu'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xlv'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xly'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xme'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xop'},
    {'ust': 'eqt', 'exchange': 'usetf', 'symbol': 'xrt'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'dia'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'eem'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'efa'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'ewj'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'eww'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'ewy'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'ewz'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'fez'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'fxe'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'fxi'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'gdx'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'gdxj'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'gld'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'hyg'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'ibb'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'ief'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'iwm'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'iyr'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'kre'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'qqq'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'rsx'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'slv'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'smh'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'spy'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'tlt'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'ung'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'uso'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xbi'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xlb'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xle'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xlf'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xli'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xlp'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xlu'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xlv'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xly'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xme'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xop'},
    {'ust': 'eqt', 'exchange': 'usyh', 'symbol': 'xrt'}
]

ALLOWED_CONFIGS = [BaseContract(**elm) for elm in ALLOWED_CONFIGS_DICT]


def _validate_config(config: BaseContract):
    return True if config in ALLOWED_CONFIGS else False


def validate_config(args: {}):
    """ check whether ust, exchange, symbol are valid """
    is_valid = _validate_config(
        BaseContract(
            ust=args['ust'].lower(),
            exchange=args['exchange'].lower(),
            symbol=args['symbol'].lower()
        )
    )
    if not is_valid:
        raise HTTPException(
            detail=(
                'could not validate the combo'
                ' of security type of the underlying (`ust`),'
                ' `exchange` and `symbol`.'
                ' Data is probably not available for this symbol.'
            ),
            status_code=HTTP_400_BAD_REQUEST
        )
