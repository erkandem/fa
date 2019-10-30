volatility api via FastApi

 TODO: finad a way to add explicit example value `(no example available)`
```
api.add_namespace(surface_ns,        path='/ivol')
api.add_namespace(ivol_at_atm_ns,    path='/ivol/time-series/delta')
api.add_namespace(ivol_by_delta_ns,  path='/ivol/time-series/delta')
api.add_namespace(combos_ns,         path='/ivol/time-series/delta/complex')
api.add_namespace(smile_ns,          path='/ivol')
api.add_namespace(price_ns,          path='/prices/intraday/regular/time-series')
api.add_namespace(pvp_ns,            path='/prices/intraday/regular/pvp')
api.add_namespace(conti_iday_ns,     path='/prices/intraday/continuous')
api.add_namespace(conti_eod_ns,      path='/prices/eod/continuous')
api.add_namespace(conti_spreads_ns,  path='/prices/eod/continuous')
api.add_namespace(regular_fut_ns,    path='/prices/eod/regular')
api.add_namespace(ping_ns,           path='/status')
api.add_namespace(info_ns,           path='/info')
api.add_namespace(rawoption_data_ns, path='/rawoptions')
api.add_namespace(ivol_summaries_ns, path='/summaries')
api.add_namespace(top_oi_n_volume_ns,path='/top-oi-and-volume')
api.add_namespace(auth_ns,           path='/auth')
api.add_namespace(user_ns,           path='/user')
```