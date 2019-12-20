

class Contract:
    """
    Class to combine frequently used settings
    related to a symbol during processing
    """
    delta_keys = [
        'd010', 'd015', 'd020', 'd025',
        'd030', 'd035', 'd040', 'd045',
        'd050',
        'd055', 'd060', 'd065', 'd070',
        'd075', 'd080', 'd085', 'd090'
    ]

    def __init__(
            self,
            security_type: str = None,
            exchange: str = None,
            symbol: str = None,
            **kwargs
    ):
        """
        Args:
            symbol(str):
            security_type(str):
            bday (date):
        """
        self.security_type = security_type
        self.exchange = exchange
        self.symbol = symbol
        #%% in case of futures
        self.contract = None  # e.g.: CLF19 {symbol}{month}{YY}
        self.quandl_symbol = None
        self.contract_yyyy = None  # reference year in 4 digit format
        self.contract_month = None  # reference month in single letter format
        self.quandl_dataset_code = None
        #%% optional
        self.bday = None
        #%% used for yh and qn queries
        self.start_dt = None
        self.end_dt = None
        #%% transaction related variables
        self.source_schema_name = None
        self.target_schema_name = None
        self.source_table_name = None
        self.target_table_name = None
        #%% ivol db related
        self.target_table_name_base = None
        #%% raw options data relevant
        self.chain_id = None
        #%% sql generation
        self.create_table = None
        #%% eod futures prices
        self.quandl_set_name = None
        self.qq = None
        self.__dict__.update(kwargs)

    async def init_via_dict(self, d: dict):
        self.__dict__.update(d)

    def __repr__(self):
        if self.security_type == 'fut':
            return (
                f'{self.security_type}'
                f' {self.exchange}'
                f' {self.symbol}'
                f' {self.contract_month}'
                f' {self.contract_yyyy}'
            ).lower()
        else:
            return (
                f'{self.security_type}'
                f' {self.exchange}'
                f' {self.symbol}'
            ).lower()

    def __str__(self):
        return self.__repr__()

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()

    def __eq__(self, other):
        return all([
            self.security_type == other.security_type,
            self.exchange == other.exchange,
            self.symbol == other.symbol,
            self.contract == other.contract])

    def __hash__(self):
        return hash(f'{self.security_type}{self.exchange}{self.symbol}{self.contract}')

    def compose_obj_name(self):
        if self.security_type.lower() == 'fut':
            if self.symbol is None:
                raise ValueError()
            if self.contract_month is None:
                raise ValueError()
            if self.contract_yyyy is None:
                raise ValueError()
            return f'{self.symbol}{self.contract_month}{self.contract_yyyy}'.lower()
        elif self.security_type.lower() == 'eqt':
            if self.symbol is None:
                raise ValueError()
            return f'{self.symbol}'
        elif self.security_type.lower() == 'ind':
            if self.symbol is None:
                raise ValueError()
            return f'{self.symbol}'
        elif self.security_type.lower() == 'fx':
            if self.symbol is None:
                raise ValueError()
            return f'{self.symbol}'
        else:
            raise NotImplementedError()

    async def compose_prices_eod_schema_name(self):
        if self.security_type is None:
            raise KeyError('security_type not defined')
        if self.exchange is None:
            raise KeyError('security_type not defined')
        return f'{self.security_type}_{self.exchange}_eod'

    async def compose_3_part_schema_name(self):
        if (self.security_type is not None
           and self.exchange is not None
           and self.symbol is not None):
            return f'{self.security_type}_{self.exchange}_{self.symbol}'.lower()
        else:
            raise ValueError(
                f'One ore more properties are None:\n'
                f'security_type: {self.security_type}\n'
                f'exchange: {self.exchange}\n'
                f'symbol: {self.symbol}')

    async def compose_2_part_schema_name(self):
        if self.security_type is None:
            raise KeyError('security_type  not set')
        if self.exchange is None:
            raise KeyError('exchange not set')
        return f'{self.security_type}_{self.exchange}'.lower()

    async def compose_ivol_table_name_base(self):
        return f'{await self.compose_3_part_schema_name()}_dpyd_'.lower()

    async def compose_prices_intraday_table_name(self):
        if self.security_type == 'eqt':
            table_name = f'{await self.compose_2_part_schema_name()}_{self.symbol}_prices_intraday'.lower()
        elif self.security_type == 'fut':
            table_name = f'{await self.compose_2_part_schema_name()}_{self.contract}_prices_intraday'.lower()
        elif self.security_type == 'fx':
            table_name = f'{await self.compose_2_part_schema_name()}_{self.symbol}_prices_intraday'.lower()
        else:
            raise NotImplementedError
        return table_name

    async def compose_prices_eod_index_table_name(self):
        if self.security_type != 'ind':
            raise KeyError('only for indeces')
        schema = await self.compose_2_part_schema_name()
        return f'{schema}_{self.symbol}_prices_eod'.lower()

    async def compose_prices_eod_fut_table_name(self):
        if self.security_type != 'fut':
            raise KeyError('only for futures')
        if self.quandl_set_name is None:
            raise KeyError('quandl_set_name was not set')
        schema = await self.compose_2_part_schema_name()
        return f'{schema}_{self.quandl_set_name}_prices_eod'.lower()

    async def compose_prices_eod_eqt_table_name(self):
        if self.security_type != 'eqt':
            raise KeyError('only for eqt')
        schema = self.compose_3_part_schema_name()
        return f'{schema}_prices_eod'

    async def compose_quandl_set_name(self):
        if self.quandl_symbol is None:
            raise KeyError('quandl_set_name is not set')
        if self.contract_yyyy is None:
            raise KeyError('contract_yyyy is not set')
        if self.contract_month is None:
            raise KeyError('contract_month not set')
        return '{s}{m}{y}'.format(
            s=self.quandl_symbol,
            m=self.contract_month,
            y=self.contract_yyyy).upper()

    async def set_quandl_set_name(self):
        self.quandl_set_name = await self.compose_quandl_set_name()

    async def compose_rawdata_table_name(self):
        if self.chain_id is None:
            raise ValueError('chain_id not set')
        if self.security_type is None:
            raise ValueError('security_type not set')
        if self.exchange is None:
            raise ValueError('exchange not set')
        if self.symbol is None:
            raise ValueError('symbol not set')
        return (
            f'{self.security_type}'
            f'_{self.exchange}'
            f'_{self.symbol}'
            f'_{self.chain_id}'
            f'_raw').lower()

    async def compose_quandl_dataset_code(self):
        if self.exchange is None:
            raise KeyError('exchange not specified')
        if self.quandl_symbol is None:
            raise KeyError('quandl_symbol not specified')
        if self.contract_month is None:
            raise KeyError('contract_month not specified')
        if self.contract_yyyy is None:
            raise KeyError('contract_yyyy not specified')
        dataset = '{e}/{s}{m}{y}'.format(
            e=self.exchange,
            s=self.quandl_symbol,
            m=self.contract_month,
            y=self.contract_yyyy).upper()
        return dataset

    async def set_quandl_dataset_code(self):
        self.quandl_dataset_code = self.compose_quandl_dataset_code()

    async def compose_ivol_final_table_name(self, delta_key):
        await self.assert_valid_delta_key(delta_key)
        await self.assert_target_table_name_base()
        return f'{self.target_table_name_base}{delta_key}'

    async def assert_valid_delta_key(self, delta_key):
        if delta_key not in self.delta_keys:
            raise ValueError(f'value of `delta_key`({delta_key}) not among the allowed values')

    async def assert_target_table_name_base(self):
        if self.target_table_name_base is None:
            raise ValueError(
                f'Value of `target_table_name_base` ({self.target_table_name_base}) was not set')



class ContractSync:
    """
    Class to combine frequently used settings
    related to a symbol during processing
    """
    delta_keys = [
        'd010', 'd015', 'd020', 'd025',
        'd030', 'd035', 'd040', 'd045',
        'd050',
        'd055', 'd060', 'd065', 'd070',
        'd075', 'd080', 'd085', 'd090'
    ]

    def __init__(
            self,
            security_type: str = None,
            exchange: str = None,
            symbol: str = None,
            **kwargs
    ):
        """
        Args:
            symbol(str):
            security_type(str):
            bday (date):
        """
        self.security_type = security_type
        self.exchange = exchange
        self.symbol = symbol
        #%% in case of futures
        self.contract = None  # e.g.: CLF19 {symbol}{month}{YY}
        self.quandl_symbol = None
        self.contract_yyyy = None  # reference year in 4 digit format
        self.contract_month = None  # reference month in single letter format
        self.quandl_dataset_code = None
        #%% optional
        self.bday = None
        #%% used for yh and qn queries
        self.start_dt = None
        self.end_dt = None
        #%% transaction related variables
        self.source_schema_name = None
        self.target_schema_name = None
        self.source_table_name = None
        self.target_table_name = None
        #%% ivol db related
        self.target_table_name_base = None
        #%% raw options data relevant
        self.chain_id = None
        #%% sql generation
        self.create_table = None
        #%% eod futures prices
        self.quandl_set_name = None
        self.qq = None
        self.__dict__.update(kwargs)

    def init_via_dict(self, d: dict):
        self.__dict__.update(d)

    def __repr__(self):
        if self.security_type == 'fut':
            return (
                f'{self.security_type}'
                f' {self.exchange}'
                f' {self.symbol}'
                f' {self.contract_month}'
                f' {self.contract_yyyy}'
            ).lower()
        else:
            return (
                f'{self.security_type}'
                f' {self.exchange}'
                f' {self.symbol}'
            ).lower()

    def __str__(self):
        return self.__repr__()

    def __lt__(self, other):
        return self.__repr__() < other.__repr__()

    def __eq__(self, other):
        return all([
            self.security_type == other.security_type,
            self.exchange == other.exchange,
            self.symbol == other.symbol,
            self.contract == other.contract])

    def __hash__(self):
        return hash(f'{self.security_type}{self.exchange}{self.symbol}{self.contract}')

    def compose_obj_name(self):
        if self.security_type.lower() == 'fut':
            if self.symbol is None:
                raise ValueError()
            if self.contract_month is None:
                raise ValueError()
            if self.contract_yyyy is None:
                raise ValueError()
            return f'{self.symbol}{self.contract_month}{self.contract_yyyy}'.lower()
        elif self.security_type.lower() == 'eqt':
            if self.symbol is None:
                raise ValueError()
            return f'{self.symbol}'
        elif self.security_type.lower() == 'ind':
            if self.symbol is None:
                raise ValueError()
            return f'{self.symbol}'
        elif self.security_type.lower() == 'fx':
            if self.symbol is None:
                raise ValueError()
            return f'{self.symbol}'
        else:
            raise NotImplementedError()

    def compose_prices_eod_schema_name(self):
        if self.security_type is None:
            raise KeyError('security_type not defined')
        if self.exchange is None:
            raise KeyError('security_type not defined')
        return f'{self.security_type}_{self.exchange}_eod'

    def compose_3_part_schema_name(self):
        if (self.security_type is not None
           and self.exchange is not None
           and self.symbol is not None):
            return f'{self.security_type}_{self.exchange}_{self.symbol}'.lower()
        else:
            raise ValueError(
                f'One ore more properties are None:\n'
                f'security_type: {self.security_type}\n'
                f'exchange: {self.exchange}\n'
                f'symbol: {self.symbol}')

    def compose_2_part_schema_name(self):
        if self.security_type is None:
            raise KeyError('security_type  not set')
        if self.exchange is None:
            raise KeyError('exchange not set')
        return f'{self.security_type}_{self.exchange}'.lower()

    def compose_ivol_table_name_base(self):
        return f'{    self.compose_3_part_schema_name()}_dpyd_'.lower()

    def compose_prices_intraday_table_name(self):
        if self.security_type == 'eqt':
            table_name = f'{    self.compose_2_part_schema_name()}_{self.symbol}_prices_intraday'.lower()
        elif self.security_type == 'fut':
            table_name = f'{    self.compose_2_part_schema_name()}_{self.contract}_prices_intraday'.lower()
        elif self.security_type == 'fx':
            table_name = f'{    self.compose_2_part_schema_name()}_{self.symbol}_prices_intraday'.lower()
        else:
            raise NotImplementedError
        return table_name

    def compose_prices_eod_index_table_name(self):
        if self.security_type != 'ind':
            raise KeyError('only for indeces')
        schema =     self.compose_2_part_schema_name()
        return f'{schema}_{self.symbol}_prices_eod'.lower()

    def compose_prices_eod_fut_table_name(self):
        if self.security_type != 'fut':
            raise KeyError('only for futures')
        if self.quandl_set_name is None:
            raise KeyError('quandl_set_name was not set')
        schema =     self.compose_2_part_schema_name()
        return f'{schema}_{self.quandl_set_name}_prices_eod'.lower()

    def compose_prices_eod_eqt_table_name(self):
        if self.security_type != 'eqt':
            raise KeyError('only for eqt')
        schema = self.compose_3_part_schema_name()
        return f'{schema}_prices_eod'

    def compose_quandl_set_name(self):
        if self.quandl_symbol is None:
            raise KeyError('quandl_set_name is not set')
        if self.contract_yyyy is None:
            raise KeyError('contract_yyyy is not set')
        if self.contract_month is None:
            raise KeyError('contract_month not set')
        return '{s}{m}{y}'.format(
            s=self.quandl_symbol,
            m=self.contract_month,
            y=self.contract_yyyy).upper()

    def set_quandl_set_name(self):
        self.quandl_set_name =     self.compose_quandl_set_name()

    def compose_rawdata_table_name(self):
        if self.chain_id is None:
            raise ValueError('chain_id not set')
        if self.security_type is None:
            raise ValueError('security_type not set')
        if self.exchange is None:
            raise ValueError('exchange not set')
        if self.symbol is None:
            raise ValueError('symbol not set')
        return (
            f'{self.security_type}'
            f'_{self.exchange}'
            f'_{self.symbol}'
            f'_{self.chain_id}'
            f'_raw').lower()

    def compose_quandl_dataset_code(self):
        if self.exchange is None:
            raise KeyError('exchange not specified')
        if self.quandl_symbol is None:
            raise KeyError('quandl_symbol not specified')
        if self.contract_month is None:
            raise KeyError('contract_month not specified')
        if self.contract_yyyy is None:
            raise KeyError('contract_yyyy not specified')
        dataset = '{e}/{s}{m}{y}'.format(
            e=self.exchange,
            s=self.quandl_symbol,
            m=self.contract_month,
            y=self.contract_yyyy).upper()
        return dataset

    def set_quandl_dataset_code(self):
        self.quandl_dataset_code = self.compose_quandl_dataset_code()

    def compose_ivol_final_table_name(self, delta_key):
        self.assert_valid_delta_key(delta_key)
        self.assert_target_table_name_base()
        return f'{self.target_table_name_base}{delta_key}'

    def assert_valid_delta_key(self, delta_key):
        if delta_key not in self.delta_keys:
            raise ValueError(f'value of `delta_key`({delta_key}) not among the allowed values')

    def assert_target_table_name_base(self):
        if self.target_table_name_base is None:
            raise ValueError(
                f'Value of `target_table_name_base` ({self.target_table_name_base}) was not set')

