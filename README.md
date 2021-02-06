# PyRCS

[![PyPI](https://img.shields.io/pypi/v/pyrcs?color=important&label=PyPI)](https://pypi.org/project/pyrcs/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrcs?color=informational&label=Python)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/pypi/l/pyrcs?color=green&label=License)](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyrcs?color=yellow&label=Downloads)](https://pypistats.org/packages/pyrcs)
[![DOI](https://zenodo.org/badge/92501006.svg)](https://zenodo.org/badge/latestdoi/92501006)

**Author**: Qian Fu

PyRCS is an open-source tool for collecting [*Railway Codes*](http://www.railwaycodes.org.uk/index.shtml) used in different UK rail industry systems.

### Cite as

Qian Fu, 2020. PyRCS: an open-source tool for collecting railway codes used in different UK rail industry systems. [doi:10.5281/zenodo.4026744](https://doi.org/10.5281/zenodo.4026744)

### Resources

- [Documentation](https://pyrcs.readthedocs.io/en/latest/)
- [Issue Tracker](https://github.com/mikeqfu/pyrcs/issues)

### License

PyRCS is licensed under [GNU General Public License v3 (GPLv3)](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE).

### Acknowledgement

The development of PyRCS is mainly built on data from the [*Railway Codes*](http://www.railwaycodes.org.uk/index.shtml) website. The author of the package would like to thank the website editor and [all contributors](http://www.railwaycodes.org.uk/misc/acknowledgements.shtm) to the data resources.

### Release history

#### [v0.2.12](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.12)

##### *Main changes (since v0.2.11):*

> - enabled the offline mode (by loading local backup when network connection is lost)
> - enabled direct access to all classes from importing the package, without having to specifying the submodules they reside in
> - combined the modules, [~~_line_data~~](https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-51811be1398d2439ca84a8504b8531b0411773c357881c423df0922f44e6923b) and [~~_other_assets~~](https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-b7304475ca50edd2572798e94bb2d0d5e2f627c6f5470d1ad24722efdb803609), into a new module: [collector](https://github.com/mikeqfu/pyrcs/blob/ac477c9dc6d76a7400ffcf9d031ffd545d662fac/pyrcs/collector.py)
> - combined the functions, [~~collect_site_map()~~](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL20) and [~~fetch_site_map()~~](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL110) in the module [updater](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc), into a new function: [get_site_map()](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R630) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315/pyrcs/utils.py)
> - renamed the following functions in the module: [utils](https://github.com/mikeqfu/pyrcs/blob/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315/pyrcs/utils.py):
>   - [~~fetch_location_names_repl_dict()~~](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L952) to [fetch_loc_names_repl_dict()](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1014)
>   - [~~update_location_name_repl_dict()~~](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L1009) to [update_loc_names_repl_dict()](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1071)
> - converted the function, [~~get_track_diagrams_items()~~](https://github.com/mikeqfu/pyrcs/commit/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56#diff-3bd1279c5db5b09065ddf6468e4acfb650e3402d8b0c410ce7beaacb667a8135R78) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56/pyrcs/utils.py), into a new method: [.get_track_diagrams_items()](https://github.com/mikeqfu/pyrcs/commit/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56) of the class [TrackDiagrams](https://github.com/mikeqfu/pyrcs/blob/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56/pyrcs/line_data/trk_diagr.py#L20) in the module [trk_diagr](https://github.com/mikeqfu/pyrcs/blob/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56/pyrcs/line_data/trk_diagr.py)
> - added the following functions to the module: [utils](https://github.com/mikeqfu/pyrcs/blob/03486c21048282d9033bda915924a70f1033645e/pyrcs/utils.py):
>   - [print_connection_error()](https://github.com/mikeqfu/pyrcs/commit/2886648b04174692ff0be58183ec56da27d1c120)
>   - [print_conn_err()](https://github.com/mikeqfu/pyrcs/commit/b42f0e36a5f231763fd8879c3e50f2e83ca000c4)
>   - [is_internet_connected()](https://github.com/mikeqfu/pyrcs/commit/03486c21048282d9033bda915924a70f1033645e)
> - renamed the following methods of the class: [SignalBoxes](https://github.com/mikeqfu/pyrcs/blob/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40/pyrcs/other_assets/sig_box.py):
>   - [~~.collect_signal_box_prefix_codes()~~](https://github.com/mikeqfu/pyrcs/commit/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40#diff-325f75b3f2452c2629af384b19046b16d42d4500c6cba2ca5cf0db5fc0772f4bL99) to [.collect_prefix_codes()](https://github.com/mikeqfu/pyrcs/blob/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40/pyrcs/other_assets/sig_box.py#L104)
>   - [~~.fetch_signal_box_prefix_codes()~~](https://github.com/mikeqfu/pyrcs/commit/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40#diff-325f75b3f2452c2629af384b19046b16d42d4500c6cba2ca5cf0db5fc0772f4bL188)  to [.fetch_prefix_codes()](https://github.com/mikeqfu/pyrcs/blob/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40/pyrcs/other_assets/sig_box.py#L200)
> - renamed the following method of the class: [Tunnels](https://github.com/mikeqfu/pyrcs/blob/a2df5ad0f6d6a8758a9f0ac122487f09a1ec0a61/pyrcs/other_assets/tunnel.py):
>   - [~~.collect_tunnel_lengths_by_page()~~](https://github.com/mikeqfu/pyrcs/commit/a2df5ad0f6d6a8758a9f0ac122487f09a1ec0a61#diff-d4156e818eca514e7b6c1b2bfbf2ac0a4a1ee2392a31b56a2c5771e87fae14c1L167) to [.collect_lengths_by_page()](https://github.com/mikeqfu/pyrcs/commit/a2df5ad0f6d6a8758a9f0ac122487f09a1ec0a61#diff-d4156e818eca514e7b6c1b2bfbf2ac0a4a1ee2392a31b56a2c5771e87fae14c1R174)
> - renamed the following methods of the class [Viaducts](https://github.com/mikeqfu/pyrcs/blob/aa5325bc12b84b0f18ef39548efc1f7d268d5347/pyrcs/other_assets/viaduct.py)
>   - [~~.collect_railway_viaducts_by_page()~~](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efL82) to [.collect_viaduct_codes_by_page()](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efR96)
>   - [~~.fetch_railway_viaducts()~~](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efL151) to [.fetch_viaduct_codes()](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efR174)
>
>
>  - updated package data
>  - updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)
>

#### [v0.2.11](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.11)

##### *Main changes (since v0.2.10):*

>    - renamed the following methods of the class [Stations](https://github.com/mikeqfu/pyrcs/blob/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c/pyrcs/other_assets/station.py):
>         - [~~.collect_railway_station_data_by_initial()~~](https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c#diff-86956d6a0963926f04ed9d7c6bf99fb9763a0c7cabb22c88c3fa8f68e5a31e19L127) to [.collect_station_data_by_initial()](https://github.com/mikeqfu/pyrcs/blob/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c/pyrcs/other_assets/station.py#L127)
>         - [~~.fetch_railway_station_data()~~](https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c#diff-86956d6a0963926f04ed9d7c6bf99fb9763a0c7cabb22c88c3fa8f68e5a31e19L246) to [.fetch_station_data()](https://github.com/mikeqfu/pyrcs/blob/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c/pyrcs/other_assets/station.py#L245)
>    - updated package data
>    - updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)
>

#### [v0.2.10](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.10)

##### *Main changes (since v0.2.9):*

>    - renamed the following modules and a few of their functions, with minor code revisions:
>         - [~~crs_nlc_tiploc_stanox~~](https://github.com/mikeqfu/pyrcs/commit/095b9d946e3c1f4a72b33ee1926f41654914f27c) to [loc_id](https://github.com/mikeqfu/pyrcs/blob/095b9d946e3c1f4a72b33ee1926f41654914f27c/pyrcs/line_data/loc_id.py)
>         - [~~electrification~~](https://github.com/mikeqfu/pyrcs/commit/e3b8bf752403b2d962528723b40977d0172e7182) to [elec](https://github.com/mikeqfu/pyrcs/blob/e3b8bf752403b2d962528723b40977d0172e7182/pyrcs/line_data/elec.py)
>         - [~~track_diagrams~~](https://github.com/mikeqfu/pyrcs/commit/5712990892792d404cb9c883f313abcb0848479b) to [trk_diagr](https://github.com/mikeqfu/pyrcs/blob/5712990892792d404cb9c883f313abcb0848479b/pyrcs/line_data/trk_diagr.py)
>         - [~~tunnels~~](https://github.com/mikeqfu/pyrcs/commit/31854d6d2e98690c5d92ee074cdb8a03e293e987) to [tunnel](https://github.com/mikeqfu/pyrcs/blob/31854d6d2e98690c5d92ee074cdb8a03e293e987/pyrcs/other_assets/tunnel.py)
>    - renamed the following modules without code revisions:
>       - [~~elrs_mileages~~](https://github.com/mikeqfu/pyrcs/commit/22b05dab9a51ffa69849be04ff26a5d8d444f9ca) to [elr_mileage](https://github.com/mikeqfu/pyrcs/blob/22b05dab9a51ffa69849be04ff26a5d8d444f9ca/pyrcs/line_data/elr_mileage.py)
>       - [~~line_names~~](https://github.com/mikeqfu/pyrcs/commit/0c7130c122cb9f55ce721711cf02935cb0f86e60) to [line_name](https://github.com/mikeqfu/pyrcs/blob/0c7130c122cb9f55ce721711cf02935cb0f86e60/pyrcs/line_data/line_name.py)
>       - [~~lor_codes~~](https://github.com/mikeqfu/pyrcs/commit/12e4cd04e598f9d74a0b4eb7f616b9f9e24e4b5e) to [lor_code](https://github.com/mikeqfu/pyrcs/blob/12e4cd04e598f9d74a0b4eb7f616b9f9e24e4b5e/pyrcs/line_data/lor_code.py)
>       - [~~depots~~](https://github.com/mikeqfu/pyrcs/commit/750e50c52124b2a28c121b88957bdae84eafecf6) to [depot](https://github.com/mikeqfu/pyrcs/blob/750e50c52124b2a28c121b88957bdae84eafecf6/pyrcs/other_assets/depot.py)
>       - [~~features~~](https://github.com/mikeqfu/pyrcs/commit/1d9645f9c9b754cf507f0c6b60ea96a26a3d105c) to [feature](https://github.com/mikeqfu/pyrcs/blob/1d9645f9c9b754cf507f0c6b60ea96a26a3d105c/pyrcs/other_assets/feature.py)
>       - [~~signal_boxes~~](https://github.com/mikeqfu/pyrcs/commit/8cd5a1eba435d8a961b2065a1e61a12c04d91248) to [sig_box](https://github.com/mikeqfu/pyrcs/blob/8cd5a1eba435d8a961b2065a1e61a12c04d91248/pyrcs/other_assets/sig_box.py)
>       - [~~stations~~](https://github.com/mikeqfu/pyrcs/commit/e0814219e719b82325dd5ff6c308f4a45cc43818) to [station](https://github.com/mikeqfu/pyrcs/blob/e0814219e719b82325dd5ff6c308f4a45cc43818/pyrcs/other_assets/station.py)
>       - [~~viaducts~~](https://github.com/mikeqfu/pyrcs/commit/b3d89ed5948319fc547737e752debb460b85991c) to [viaduct](https://github.com/mikeqfu/pyrcs/blob/b3d89ed5948319fc547737e752debb460b85991c/pyrcs/other_assets/viaduct.py)
>    - updated package data
>    - updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/) with substantial revisions
>


#### [v0.2.9](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.9)

##### *Main changes (since v0.2.8):*

>    - updated package data
>    - updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)
>


#### [v0.2.8](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.8)

##### *Main changes (since v0.2.7):*

> - modified all modules (including docstrings) with bug fixes
> - updated package data
> - updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)
>


#### [v0.2.7](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.7)

##### *Main changes (since v0.2.6):*

>   - modified all modules (including docstrings) with bug fixes 
>   - updated package data
>   - created [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/) being hosted at [Read the Docs](https://readthedocs.org/)
>

#### [v0.2.6](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.6)

##### *Main changes (since v0.2.5):*

>   - added a new function [fix_num_stanox()](https://github.com/mikeqfu/pyrcs/commit/fd5df3a101aa565bab2b5c1d9ca840dd1b812291) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/fd5df3a101aa565bab2b5c1d9ca840dd1b812291/pyrcs/utils.py)
>   - updated package data
>


#### [v0.2.5](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.5)

##### *Main changes (since v0.2.4):*

>   - modified the [keys of the dict-type data](https://github.com/mikeqfu/pyrcs/commit/48e2b908984f940c3abe3aba5899de5fe8c285cc) for the two classes: [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/48e2b908984f940c3abe3aba5899de5fe8c285cc/pyrcs/line_data_cls/elrs_mileages.py#L244) and [SignalBoxes](https://github.com/mikeqfu/pyrcs/blob/48e2b908984f940c3abe3aba5899de5fe8c285cc/pyrcs/other_assets_cls/signal_boxes.py#L18)
>   - renamed the function [~~update_package_data()~~](https://github.com/mikeqfu/pyrcs/commit/e46e17002cd048db63dc5c7c0e074b4162377705) in the module [update](https://github.com/mikeqfu/pyrcs/blob/e46e17002cd048db63dc5c7c0e074b4162377705/pyrcs/update.py) to [update_pkg_metadata()](https://github.com/mikeqfu/pyrcs/blob/e46e17002cd048db63dc5c7c0e074b4162377705/pyrcs/update.py#L11)
>   - updated package data
>   - tested the package in Python 3.8
>


#### [v0.2.4](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.4)

##### *Main changes (since v0.2.3):*

>   - removed the module [settings](https://github.com/mikeqfu/pyrcs/commit/8e6340bfe078f0cd558f059f89ef1d5029ef62b4)
>   - updated import statements in all the package modules due to changes in the dependencies from [PyHelpers](https://github.com/mikeqfu/pyhelpers)
>   - made a few revisions due to changes on the web pages of the data source
>   - updated package data
>

#### [v0.2.3](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.3)

##### *Main changes (since v0.2.2):*

>   - updated a few helper functions with [bug fixes](https://github.com/mikeqfu/pyrcs/commit/7872dc917065623f3cb5f7939a065900c6070af4) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/7872dc917065623f3cb5f7939a065900c6070af4/pyrcs/utils.py)
>   - updated package data
>


#### [v0.2.2](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.2)

##### *Main changes (since v0.2.1):*

>   - modified the following methods of the class [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/bc45055b6d07f83bddadd29c590226d7ddb9a7d3/pyrcs/line_data_cls/elrs_mileages.py#L244):
>     - [.collect_mileage_file_by_elr()](https://github.com/mikeqfu/pyrcs/commit/3a4b210c8373de14de7740c9ca874db100687200)
>     - [.get_conn_mileages()](https://github.com/mikeqfu/pyrcs/commit/bc45055b6d07f83bddadd29c590226d7ddb9a7d3)
>   - fixed [a minor issue](https://github.com/mikeqfu/pyrcs/commit/fe6373d2f7ff73cad893a865879e74b2c54d9e86) in the filenames of the package's backup data
>   - updated package data
>

#### [v0.2.1](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.1)

##### *Main changes (since v0.2.0):*

>   - modified the following modules with bug fixes:
>     - [utils](https://github.com/mikeqfu/pyrcs/blob/80fed8c2fb3096457a20e543af5f15cb55f40407/pyrcs/utils.py)
>     - [elrs_mileages](https://github.com/mikeqfu/pyrcs/blob/0dd70c69bea3a8190455cbf36eab659b02d86315/pyrcs/line_data_cls/elrs_mileages.py)
>   - updated and renamed all files of package data
>

#### [v0.2.0](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.0)

**A brand-new release.**

*Note that the initial release and later versions up to v0.1.28 have been deprecated and permanently removed.*