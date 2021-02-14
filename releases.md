### Release history



#### [0.2.13](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.13)

*9 January 2021*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.12...0.2.13) since [v0.2.12](https://github.com/mikeqfu/pyrcs/tree/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d):

- modified the following classes/methods of the sub-package [line_data](https://github.com/mikeqfu/pyrcs/tree/19429031fdd3ea8d0bfab8cdea43e2804636e278/pyrcs/line_data) with bug fixes:
  - [Electrification.get_indep_line_names()](https://github.com/mikeqfu/pyrcs/commit/e539d508b97bfa1ca6740fd5bd281e60c23e94dc)
  - [ELRMileage.collect_mileage_file()](https://github.com/mikeqfu/pyrcs/commit/d67827f636c9cd5a7bf43c64c1fff226c09f4625)
  - [LOR.collect_elr_lor_converter()](https://github.com/mikeqfu/pyrcs/commit/ab2d79b9ed96f71083bf0656d0b1f1bde214837d)
- modified the following classes/methods of the sub-package [other_assets](https://github.com/mikeqfu/pyrcs/tree/19429031fdd3ea8d0bfab8cdea43e2804636e278/pyrcs/other_assets) with bug fixes:
  - [Depots.collect_four_digit_pre_tops_codes](https://github.com/mikeqfu/pyrcs/commit/af2c62b1807325351a4f5217c710919d25ffc629)
  - [Tunnels.parse_length()](https://github.com/mikeqfu/pyrcs/commit/20b8036d923ea2f36dcb0b9e175afda5182f3e19)
  - [Stations](https://github.com/mikeqfu/pyrcs/commit/b6c075026d62e771c40a5f5b4934b72f9682dfc4)
- modified the following functions in the module [utils](https://github.com/mikeqfu/pyrcs/blob/19429031fdd3ea8d0bfab8cdea43e2804636e278/pyrcs/utils.py) with bug fixes:
  - [parse_tr()](https://github.com/mikeqfu/pyrcs/commit/e9b081523afad4ba5b43173e1f877964e2998c0b#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R426)
  - [parse_date()](https://github.com/mikeqfu/pyrcs/commit/e9b081523afad4ba5b43173e1f877964e2998c0b#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R622)
- updated offline backup data
- updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)



#### [0.2.12](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.12)

*11 November 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.11...0.2.12) since [v0.2.11](https://github.com/mikeqfu/pyrcs/tree/81fe73e419597868e58731cb9417f4583b5a3611):

- enabled the offline mode (by loading local backup when network connection is lost)
- enabled direct access to all classes from importing the package, without having to specifying the sub-modules they reside in
- combined the modules, [~~_line_data~~](https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-51811be1398d2439ca84a8504b8531b0411773c357881c423df0922f44e6923b) and [~~_other_assets~~](https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-b7304475ca50edd2572798e94bb2d0d5e2f627c6f5470d1ad24722efdb803609), into a new module: [collector](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/collector.py)
- made a few modifications to the module [utils](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py):
  - converted functions:
    - [get_site_map()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py#L631) combined from the functions [~~collect_site_map()~~](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL20) and [~~fetch_site_map()~~](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL110) in the module [updater](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/updater.py)
    - [fetch_loc_names_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py#L1037) renamed from [~~fetch_location_names_repl_dict()~~](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L952)
    - [update_loc_names_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py#L1094) renamed from [~~update_location_name_repl_dict()~~](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L1009)
  - newly added functions:
    - [print_connection_error()](https://github.com/mikeqfu/pyrcs/commit/2886648b04174692ff0be58183ec56da27d1c120#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1192-R1205)
    - [print_conn_err()](https://github.com/mikeqfu/pyrcs/commit/b42f0e36a5f231763fd8879c3e50f2e83ca000c4#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1206-R1225)
    - [is_internet_connected()](https://github.com/mikeqfu/pyrcs/commit/03486c21048282d9033bda915924a70f1033645e#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1262-R1283)
- converted the function, [~~get_track_diagrams_items()~~](https://github.com/mikeqfu/pyrcs/commit/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56#diff-3bd1279c5db5b09065ddf6468e4acfb650e3402d8b0c410ce7beaacb667a8135R78) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py), into a new method: [.get_track_diagrams_items()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/line_data/trk_diagr.py#L85) of the class [TrackDiagrams](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/line_data/trk_diagr.py#L21)
- renamed the following methods of the class [SignalBoxes](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/sig_box.py#L28):
  - [~~.collect_signal_box_prefix_codes()~~](https://github.com/mikeqfu/pyrcs/commit/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40#diff-325f75b3f2452c2629af384b19046b16d42d4500c6cba2ca5cf0db5fc0772f4bL99) to [.collect_prefix_codes()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/sig_box.py#L107)
  - [~~.fetch_signal_box_prefix_codes()~~](https://github.com/mikeqfu/pyrcs/commit/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40#diff-325f75b3f2452c2629af384b19046b16d42d4500c6cba2ca5cf0db5fc0772f4bL188)  to [.fetch_prefix_codes()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/sig_box.py#L203)
- renamed the following method of the class [Tunnels](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/tunnel.py#L27):
  - [~~.collect_tunnel_lengths_by_page()~~](https://github.com/mikeqfu/pyrcs/commit/a2df5ad0f6d6a8758a9f0ac122487f09a1ec0a61#diff-d4156e818eca514e7b6c1b2bfbf2ac0a4a1ee2392a31b56a2c5771e87fae14c1L167) to [.collect_lengths_by_page()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/tunnel.py#L177)
- renamed the following methods of the class [Viaducts](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/viaduct.py#L23)
  - [~~.collect_railway_viaducts_by_page()~~](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efL82) to [.collect_viaduct_codes_by_page()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/viaduct.py#L99)
  - [~~.fetch_railway_viaducts()~~](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efL151) to [.fetch_viaduct_codes()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/viaduct.py#L177)
- updated offline backup data
- updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)



#### [0.2.11](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.11)

*31 October 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.10...0.2.11) since [v0.2.10](https://github.com/mikeqfu/pyrcs/tree/35ea90d30696c66fc95899cf9ab343a245089381):

- renamed the following methods of the class [Stations](https://github.com/mikeqfu/pyrcs/blob/81fe73e419597868e58731cb9417f4583b5a3611/pyrcs/other_assets/station.py#L31):
  - [~~.collect_railway_station_data_by_initial()~~](https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c#diff-86956d6a0963926f04ed9d7c6bf99fb9763a0c7cabb22c88c3fa8f68e5a31e19L127) to [.collect_station_data_by_initial()](https://github.com/mikeqfu/pyrcs/blob/81fe73e419597868e58731cb9417f4583b5a3611/pyrcs/other_assets/station.py#L127)
  - [~~.fetch_railway_station_data()~~](https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c#diff-86956d6a0963926f04ed9d7c6bf99fb9763a0c7cabb22c88c3fa8f68e5a31e19L246) to [.fetch_station_data()](https://github.com/mikeqfu/pyrcs/blob/81fe73e419597868e58731cb9417f4583b5a3611/pyrcs/other_assets/station.py#L245)
- updated offline backup data
- updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)



#### [0.2.10](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.10)

*25 October 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.9...0.2.10) since [v0.2.9](https://github.com/mikeqfu/pyrcs/tree/109c8a3d870f8b2795edc3132bafef38a6f1d56e):

- renamed the following modules and a few of their functions, with minor code revisions:
  - [~~crs_nlc_tiploc_stanox~~](https://github.com/mikeqfu/pyrcs/commit/095b9d946e3c1f4a72b33ee1926f41654914f27c) to [loc_id](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/loc_id.py)
  - [~~electrification~~](https://github.com/mikeqfu/pyrcs/commit/e3b8bf752403b2d962528723b40977d0172e7182) to [elec](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/elec.py)
  - [~~track_diagrams~~](https://github.com/mikeqfu/pyrcs/commit/5712990892792d404cb9c883f313abcb0848479b) to [trk_diagr](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/trk_diagr.py)
  - [~~tunnels~~](https://github.com/mikeqfu/pyrcs/commit/31854d6d2e98690c5d92ee074cdb8a03e293e987) to [tunnel](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/tunnel.py)
- renamed the following modules without code revisions:
  - [~~elrs_mileages~~](https://github.com/mikeqfu/pyrcs/commit/22b05dab9a51ffa69849be04ff26a5d8d444f9ca) to [elr_mileage](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/elr_mileage.py)
  - [~~line_names~~](https://github.com/mikeqfu/pyrcs/commit/0c7130c122cb9f55ce721711cf02935cb0f86e60) to [line_name](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/line_name.py)
  - [~~lor_codes~~](https://github.com/mikeqfu/pyrcs/commit/12e4cd04e598f9d74a0b4eb7f616b9f9e24e4b5e) to [lor_code](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/lor_code.py)
  - [~~depots~~](https://github.com/mikeqfu/pyrcs/commit/750e50c52124b2a28c121b88957bdae84eafecf6) to [depot](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/depot.py)
  - [~~features~~](https://github.com/mikeqfu/pyrcs/commit/1d9645f9c9b754cf507f0c6b60ea96a26a3d105c) to [feature](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/feature.py)
  - [~~signal_boxes~~](https://github.com/mikeqfu/pyrcs/commit/8cd5a1eba435d8a961b2065a1e61a12c04d91248) to [sig_box](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/sig_box.py)
  - [~~stations~~](https://github.com/mikeqfu/pyrcs/commit/e0814219e719b82325dd5ff6c308f4a45cc43818) to [station](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/station.py)
  - [~~viaducts~~](https://github.com/mikeqfu/pyrcs/commit/b3d89ed5948319fc547737e752debb460b85991c) to [viaduct](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/viaduct.py)
- updated offline backup data
- updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/) with substantial revisions



#### [0.2.9](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.9)

*13 September 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.8...0.2.9) since [v0.2.8](https://github.com/mikeqfu/pyrcs/tree/7d50599fcef5b038756ff39d30a531dd46d76c97):

- updated offline backup data
- updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)



#### [0.2.8](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.8)

*13 September 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.7...0.2.8) since [v0.2.7](https://github.com/mikeqfu/pyrcs/tree/0e33eb393089fa706daedf31f1475dd3493c82ae):

- made modifications to the module [utils](https://github.com/mikeqfu/pyrcs/blob/4bcd0a2e329f37d7c74a3b5b9b3d9e56ba5df508/pyrcs/utils.py)
  - a deleted function: [~~fake_requests_headers()~~](https://github.com/mikeqfu/pyrcs/commit/4bcd0a2e329f37d7c74a3b5b9b3d9e56ba5df508#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L547-L562) 
  - a new function: [fix_nr_mileage_str()](https://github.com/mikeqfu/pyrcs/commit/bc9ec4d9789e74851832fd548959bfc5d41f0041)
  - [a bug fix](https://github.com/mikeqfu/pyrcs/commit/dbf794d6c4ac176b8b5220f3931d65dd237f3d45) in the function [nr_mileage_num_to_str()](https://github.com/mikeqfu/pyrcs/blob/7d50599fcef5b038756ff39d30a531dd46d76c97/pyrcs/utils.py#L155)
- modified the class [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/7d50599fcef5b038756ff39d30a531dd46d76c97/pyrcs/line_data/elrs_mileages.py#L28) with [bug fixes](https://github.com/mikeqfu/pyrcs/commit/8849e0d33b70e68a1c80e9ec3d49edcc1fc8a21a)
- modified [all sub-modules](https://github.com/mikeqfu/pyrcs/commit/983069544949bd3158c5821787aeaf455d2e8511) with [pyhelpers.validate_input_data_dir()](https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.validate_input_data_dir.html)
- updated offline backup data
- updated [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/)



#### [0.2.7](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.7)

*18 July 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.6...0.2.7) since [v0.2.6](https://github.com/mikeqfu/pyrcs/tree/6b4c9214767f5b37a00ed374a049ab09ac9706b1):

- renamed the following sub-packages, with modifications to all their sub-modules: 
  - [~~line_data_cls~~](https://github.com/mikeqfu/pyrcs/commit/af64bddcbf15e60743e7339f0423c1872bbf3d8e) to [line_data](https://github.com/mikeqfu/pyrcs/tree/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/line_data)
  - [~~other_assets_cls~~](https://github.com/mikeqfu/pyrcs/commit/1939baac8d176ac5be992dd6f94c046b45b71555) to [other_assets](https://github.com/mikeqfu/pyrcs/tree/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/other_assets)
- renamed the following modules:
  - [~~line_data~~](https://github.com/mikeqfu/pyrcs/commit/6784edee320bb0de5e4d472965df95c4819a8e5a) to [_line_data](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/_line_data.py)
  - [~~other_assets~~](https://github.com/mikeqfu/pyrcs/commit/49e5f4bd0e2c9ee835cdfcb2b9d872c0ac9bb40f) to [_other_assets](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/_other_assets.py)
- made modifications to the module [updater](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py) (renamed from [update](https://github.com/mikeqfu/pyrcs/blob/67f07a14d8e5d527cd86c85163b4d38c4278af26/pyrcs/update.py)):
  - the function [~~update_pkg_metadata()~~](https://github.com/mikeqfu/pyrcs/commit/116d415eb13b46fced36925d129a29b943fc8c53#diff-4527118d31dfdca143242274ac926ded7c6824b2a95a6b8304bd6c16585a1995L11) renamed to [update_backup_data()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py#L132)
  - new functions: [collect_site_map()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py#L17) and [fetch_site_map()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py#L88)
- modified the module [utils](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/utils.py) with a new function [homepage_url()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/utils.py#L21) and [bug fixes](https://github.com/mikeqfu/pyrcs/commit/be2cd82881420a97784f28f6d3d16d5a4264aa28)
- removed the module [rc_psql](https://github.com/mikeqfu/pyrcs/commit/9ab958fa6ae7df12893509376d91535c52280e31) (Instead, [pyhelpers.sql](https://pyhelpers.readthedocs.io/en/latest/sql.html) is recommended)
- updated offline backup data
- created [PyRCS Documentation](https://pyrcs.readthedocs.io/en/latest/) being hosted at [Read the Docs](https://readthedocs.org/)



#### [0.2.6](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.6)

*8 March 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.5...0.2.6) since [v0.2.5](https://github.com/mikeqfu/pyrcs/tree/e53a7e56146b2c20ca91e6aa278b1c333c09e69a):

- added a new function [fix_num_stanox()](https://github.com/mikeqfu/pyrcs/blob/6b4c9214767f5b37a00ed374a049ab09ac9706b1/pyrcs/utils.py#L600) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/6b4c9214767f5b37a00ed374a049ab09ac9706b1/pyrcs/utils.py)
- updated offline backup data



#### [0.2.5](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.5)

*10 January 2020*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.4...0.2.5) since [v0.2.4](https://github.com/mikeqfu/pyrcs/tree/7d33f4d43c62f2482a45a280067a0ee4d369a603):

- modified the [keys of the dict-type data](https://github.com/mikeqfu/pyrcs/commit/48e2b908984f940c3abe3aba5899de5fe8c285cc) for the following two classes
  - [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/line_data_cls/elrs_mileages.py#L244) 
  - [SignalBoxes](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/other_assets_cls/signal_boxes.py#L18)
- renamed the function [~~update_package_data()~~](https://github.com/mikeqfu/pyrcs/commit/e46e17002cd048db63dc5c7c0e074b4162377705) to [update_pkg_metadata()](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/update.py#L11) in the module [update](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/update.py) 
- tested the package in Python 3.8
- updated offline backup data



#### [0.2.4](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.4)

*4 December 2019*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.3...0.2.4) since [v0.2.3](https://github.com/mikeqfu/pyrcs/tree/f0d8f3b271234fd6710ff6dd4dae9b6315db6c01):

- removed the module [settings](https://github.com/mikeqfu/pyrcs/commit/8e6340bfe078f0cd558f059f89ef1d5029ef62b4)
- updated [import statements](https://github.com/mikeqfu/pyrcs/commit/aca6383be837a241ff0012a53a33ce5469cf676f) in some modules/sub-modules due to changes in their dependencies from [PyHelpers](https://github.com/mikeqfu/pyhelpers)
- made [a few revisions](https://github.com/mikeqfu/pyrcs/commit/0a31277fec3d87f6fe0b561a3b16d013cdd9eb8b) due to changes on the web pages of the data resource
- updated offline backup data



#### [0.2.3](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.3)

*4 October 2019*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.2...0.2.3) since [v0.2.2](https://github.com/mikeqfu/pyrcs/tree/4f4f3c765948f935bd8160071082c2b16237f1db):

- modified the module [utils](https://github.com/mikeqfu/pyrcs/blob/f0d8f3b271234fd6710ff6dd4dae9b6315db6c01/pyrcs/utils.py) with [bug fixes](https://github.com/mikeqfu/pyrcs/commit/7872dc917065623f3cb5f7939a065900c6070af4) 
- updated offline backup data



#### [0.2.2](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.2)

*27 September 2019*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.1...0.2.2) since [v0.2.1](https://github.com/mikeqfu/pyrcs/tree/036453c38c35f12183d5adc0fde88ffd5f402110):

- modified the following methods of the class [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/bc45055b6d07f83bddadd29c590226d7ddb9a7d3/pyrcs/line_data_cls/elrs_mileages.py#L244) in the module [elrs_mileages](https://github.com/mikeqfu/pyrcs/blob/4f4f3c765948f935bd8160071082c2b16237f1db/pyrcs/line_data_cls/elrs_mileages.py) of the sub-package [line_data_cls](https://github.com/mikeqfu/pyrcs/tree/4f4f3c765948f935bd8160071082c2b16237f1db/pyrcs/line_data_cls):
  - [.collect_mileage_file_by_elr()](https://github.com/mikeqfu/pyrcs/commit/3a4b210c8373de14de7740c9ca874db100687200)
  - [.get_conn_mileages()](https://github.com/mikeqfu/pyrcs/commit/bc45055b6d07f83bddadd29c590226d7ddb9a7d3)
- updated offline backup data (with fixes to some minor issues)



#### [0.2.1](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.1)

*18 September 2019*

##### Main [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.0...0.2.1) since [v0.2.0](https://github.com/mikeqfu/pyrcs/tree/a3e4d035a2ce9ef905ec0b65d3ac414798b89804):

- added a function [is_str_float()](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/line_data_cls/elrs_mileages.py#L33) to the module [elrs_mileages](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/line_data_cls/elrs_mileages.py)
- made some modifications to the module [utils](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py):
  - newly added functions:
    - [fetch_location_names_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py#L440)
    - [update_location_name_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py#L465)
  - a deleted function:
    - [~~is_float()~~](https://github.com/mikeqfu/pyrcs/commit/80fed8c2fb3096457a20e543af5f15cb55f40407#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L436-L442)
- renamed and updated all offline backup data



#### [0.2.0](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.0)

*29 August 2019*

**A brand-new release.**

*Note that the initial release and later versions up to v0.1.28 have been deprecated and permanently removed.*