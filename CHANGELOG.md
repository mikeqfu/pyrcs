# Changelog / Release notes

<br/>

## **[1.0.1](https://github.com/mikeqfu/pyrcs/releases/tag/1.0.1)**

(*19 March 2025*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/1.0.0...1.0.1) since [1.0.0](https://pypi.org/project/pyrcs/1.0.0/):**

- Enhanced existing tests to improve coverage and reliability. 
- Fixed minor bugs. 
- Updated project requirements.

**For more information and detailed specifications, check out the [PyRCS 1.0.1 documentation](https://pyrcs.readthedocs.io/en/1.0.1/).**

<br/>

## **[1.0.0](https://github.com/mikeqfu/pyrcs/releases/tag/1.0.0)**

(*3 March 2025*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.7...1.0.0) since [0.3.7](https://pypi.org/project/pyrcs/0.3.7/):**

- **Major Release:** Version 1.0.0 introduces significant improvements to both code and documentation.
  - *Code enhancements*: Optimised performance and refactored core modules for better readability and maintainability.
  - *Bug fixes*: Resolved various issues identified through practical use.
- **License Update:** This release is now licensed under the [MIT License](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE), providing greater flexibility and usability.

**For more information and detailed specifications, check out the [PyRCS 1.0.0 documentation](https://pyrcs.readthedocs.io/en/1.0.0/).**

<br/>

## **[0.3.7](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.7)**

(*16 September 2023*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.6...0.3.7) since [0.3.6](https://pypi.org/project/pyrcs/0.3.6/):**

- Enhanced the functions [get_site_map()](https://github.com/mikeqfu/pyrcs/commit/c306b102bb681e4148c56fd595b784ae8da813c5#diff-9f446a48cdb82259e3132abf65a2d39122ee7d123d7968ec2b6780123c5d6819L404-R410) and [parse_tr()](https://github.com/mikeqfu/pyrcs/commit/c306b102bb681e4148c56fd595b784ae8da813c5#diff-9f446a48cdb82259e3132abf65a2d39122ee7d123d7968ec2b6780123c5d6819L65-R176) in the [parser](https://github.com/mikeqfu/pyrcs/blob/e2f6576a5d74cd6ab7070c0bfaf1dffffca78150/pyrcs/parser.py) module.
- Fixed potential bugs and made improvements to [various classes](https://github.com/mikeqfu/pyrcs/commit/df087f2a52ffe0b287ecd04e59ac08ece7b310c9).

**For more information and detailed specifications, check out [PyRCS 0.3.7 documentation](https://pyrcs.readthedocs.io/en/0.3.7/).**

<br/>

## **[0.3.6](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.6)**

(*10 June 2023*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.5...0.3.6) since [0.3.5](https://pypi.org/project/pyrcs/0.3.5/):**

- Improved the following functions and classes with bug fixes:
  - [parse_tr()](https://github.com/mikeqfu/pyrcs/commit/66914b12e42bf81f7f19415ec50598efdaf0d03d) in the module [parser](https://github.com/mikeqfu/pyrcs/blob/203ab72e713c54537c4e9a4721c16c930deafd44/pyrcs/parser.py);
  - [format_err_msg()](https://github.com/mikeqfu/pyrcs/commit/83e311bddcc6247f58ad2dd165195278ff7a0fe8) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/203ab72e713c54537c4e9a4721c16c930deafd44/pyrcs/utils.py);
  - [Stations](https://github.com/mikeqfu/pyrcs/commit/0b5062bf64214fd5ca3cd9ec7c50a33b570ad4ad) in the module [other_assets.station](https://github.com/mikeqfu/pyrcs/blob/203ab72e713c54537c4e9a4721c16c930deafd44/pyrcs/other_assets/station.py);
  - [LocationIdentifiers](https://github.com/mikeqfu/pyrcs/commit/ac582ccde71e3e9309dba983ec04cb13c181a942) in the module [line_data.loc_id](https://github.com/mikeqfu/pyrcs/blob/203ab72e713c54537c4e9a4721c16c930deafd44/pyrcs/line_data/loc_id.py).

**For more information and detailed specifications, check out [PyRCS 0.3.6 documentation](https://pyrcs.readthedocs.io/en/0.3.6/).**

<br/>

## **[0.3.5](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.5)**

(*26 February 2023*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.4...0.3.5) since [0.3.4](https://pypi.org/project/pyrcs/0.3.4/):**

- Improved the following function and methods with bug fixes:
  - [kilometer_to_yard()](https://github.com/mikeqfu/pyrcs/commit/994e9f3c3145ad73b47164dd898118b0a0c70ace) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/46d519c2ba0a390bf053c6c90df3c79746c6381e/pyrcs/converter.py);
  - [LocationIdentifiers.collect_codes_by_initial()](https://github.com/mikeqfu/pyrcs/commit/6892fc38d91f731ef4677f274262ec5bd0c4c532);
  - [ELRMileages.collect_mileage_file()](https://github.com/mikeqfu/pyrcs/commit/cc2d30bff507a4f2c49c60e0cac78c9c0fdcef2a).

**For more information and detailed specifications, check out [PyRCS 0.3.5 documentation](https://pyrcs.readthedocs.io/en/0.3.5/).**

<br/>

## **[0.3.4](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.4)**

(*9 January 2023*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.3...0.3.4) since [0.3.3](https://pypi.org/project/pyrcs/0.3.3/):**

- Improved the modules [collector](https://github.com/mikeqfu/pyrcs/blob/c77554a4686b630d0b95bc155722c7e5c7a7c453/pyrcs/collector.py) and [_updater](https://github.com/mikeqfu/pyrcs/blob/c77554a4686b630d0b95bc155722c7e5c7a7c453/pyrcs/_updater.py) with a [bug fix](https://github.com/mikeqfu/pyrcs/commit/986637ed7df18bc5e656d4ba0aab736105f4dfb7). 

**For more information and detailed specifications, check out [PyRCS 0.3.4 documentation](https://pyrcs.readthedocs.io/en/0.3.4/).**

<br/>

## **[0.3.3](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.3)**

(*15 November 2022*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.2...0.3.3) since [0.3.2](https://pypi.org/project/pyrcs/0.3.2/):**

- Fixed a major bug in the function [parse_tr()](https://github.com/mikeqfu/pyrcs/commit/3348c9cdfe62197405d68fa8aa8d5c053a9fae78) in the module [parser](https://github.com/mikeqfu/pyrcs/blob/4f63edb931e1a174b5ce61326d2741f3a6e3a7a9/pyrcs/parser.py).
- Improved the following classes with bug fixes: [LocationIdentifiers](https://github.com/mikeqfu/pyrcs/commit/68a8ae4ac202af90a0181fcc11371f45b8869c5a), [LOR](https://github.com/mikeqfu/pyrcs/commit/3a1137f56fbda55da72315f872671d8d27b62401) and [Stations](https://github.com/mikeqfu/pyrcs/commit/2a62e5ac7c9461f151efa7d9fc95227bc30ac4c2).
- Transform the function [parse_location_name()](https://github.com/mikeqfu/pyrcs/commit/12759e6b0e22a61f46a3189a5efc1c5aa0758d13) into a class method [LocationIdentifiers.parse_location_name()](https://github.com/mikeqfu/pyrcs/commit/68a8ae4ac202af90a0181fcc11371f45b8869c5a#diff-9892665521535dc0b2b16a9a95a1c7c2cbae159ebc7233522df340514a2b7200R417).

**For more information and detailed specifications, check out [PyRCS 0.3.3 documentation](https://pyrcs.readthedocs.io/en/0.3.3/).**

<br/>

## **[0.3.2](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.2)**

(*18 August 2022*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.1...0.3.2) since [0.3.1](https://pypi.org/project/pyrcs/0.3.1/):**

- Fixed a few minor bugs.

**For more information and detailed specifications, check out [PyRCS 0.3.2 documentation](https://pyrcs.readthedocs.io/en/0.3.2/).**

<br/>

## **[0.3.1](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.1)**

(*14 June 2022*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.3.0...0.3.1) since [0.3.0](https://pypi.org/project/pyrcs/0.3.0/):**

- Updated import statements due to [a major change](https://github.com/mikeqfu/pyhelpers/releases/tag/1.4.0) in the dependency package [PyHelpers](https://pypi.org/project/pyhelpers/).

**For more information and detailed specifications, check out [PyRCS 0.3.1 documentation](https://pyrcs.readthedocs.io/en/0.3.1/).**

<br/>

## **[0.3.0](https://github.com/mikeqfu/pyrcs/releases/tag/0.3.0)**

(*16 May 2022*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.15...0.3.0) since [0.2.15](https://pypi.org/project/pyrcs/0.2.15/):**

- Split the module old [utils](https://github.com/mikeqfu/pyrcs/blob/dd7bb9df95ee86939b790eaba1f79e10bc54d1a4/pyrcs/utils.py) into three new modules: [utils](https://github.com/mikeqfu/pyrcs/commit/c55830dd3c250425916ba275eb9429972441b7e5), [converter](https://github.com/mikeqfu/pyrcs/commit/19c8d3911c86db02fbc94f64bb4a22e9de88fa6c) and [parser](https://github.com/mikeqfu/pyrcs/commit/34be0c12604694eb580bf55192e2ebe7fa0645d1).
- Made extensive modifications (with bug fixes).

**For more information and detailed specifications, check out [PyRCS 0.3.0 documentation](https://pyrcs.readthedocs.io/en/0.3.0/).**

<br/>

## **[0.2.15](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.15)**

(*27 March 2021*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.14...0.2.15) since [0.2.14](https://pypi.org/project/pyrcs/0.2.14/):**

- Changed the [dependency requirements](https://github.com/mikeqfu/pyrcs/commit/99c6b5400b0cc89540bd9de7060cb4562ff0b684) for the package.

**For more information and detailed specifications, check out [PyRCS 0.2.15 documentation](https://pyrcs.readthedocs.io/en/0.2.15/).**

<br/>

## **[0.2.14](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.14)**

(*22 March 2021*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.13...0.2.14) since [0.2.13](https://pypi.org/project/pyrcs/0.2.13/):**

- Improved the following functions and class methods with bug fixes:
  - [get_site_map()](https://github.com/mikeqfu/pyrcs/commit/1231bdb62914485acead5751ea055e063c0fa711#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L636-R814) and [get_catalogue()](https://github.com/mikeqfu/pyrcs/commit/1231bdb62914485acead5751ea055e063c0fa711#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L844-R991) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/fd7e40834af60dc80d334e541cd26fe9d88865bc/pyrcs/utils.py);
  - [LocationIdentifiers.collect_loc_codes_by_initial()](https://github.com/mikeqfu/pyrcs/commit/ca7bd7132bfc1c40327425335934a019fd69388e);
  - [Stations.collect_station_data_by_initial()](https://github.com/mikeqfu/pyrcs/commit/69df19d4e3692ca6f1642c7e029a61fd6ec72fa3).

**For more information and detailed specifications, check out [PyRCS 0.2.14 documentation](https://pyrcs.readthedocs.io/en/0.2.14/).** 

<br/>

## **[0.2.13](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.13)**

(*9 January 2021*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.12...0.2.13) since [0.2.12](https://pypi.org/project/pyrcs/0.2.12/):**

- Improved the following functions and classes/methods with bug fixes:
  - [parse_tr()](https://github.com/mikeqfu/pyrcs/commit/e9b081523afad4ba5b43173e1f877964e2998c0b#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R426) and [parse_date()](https://github.com/mikeqfu/pyrcs/commit/e9b081523afad4ba5b43173e1f877964e2998c0b#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R622) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/19429031fdd3ea8d0bfab8cdea43e2804636e278/pyrcs/utils.py);
  - [Electrification.get_indep_line_names()](https://github.com/mikeqfu/pyrcs/commit/e539d508b97bfa1ca6740fd5bd281e60c23e94dc), [ELRMileage.collect_mileage_file()](https://github.com/mikeqfu/pyrcs/commit/d67827f636c9cd5a7bf43c64c1fff226c09f4625) and [LOR.collect_elr_lor_converter()](https://github.com/mikeqfu/pyrcs/commit/ab2d79b9ed96f71083bf0656d0b1f1bde214837d) in the sub-package [line_data](https://github.com/mikeqfu/pyrcs/tree/19429031fdd3ea8d0bfab8cdea43e2804636e278/pyrcs/line_data);
  - [Depots.collect_four_digit_pre_tops_codes](https://github.com/mikeqfu/pyrcs/commit/af2c62b1807325351a4f5217c710919d25ffc629), [Tunnels.parse_length()](https://github.com/mikeqfu/pyrcs/commit/20b8036d923ea2f36dcb0b9e175afda5182f3e19) and [Stations](https://github.com/mikeqfu/pyrcs/commit/b6c075026d62e771c40a5f5b4934b72f9682dfc4) in the sub-package [other_assets](https://github.com/mikeqfu/pyrcs/tree/19429031fdd3ea8d0bfab8cdea43e2804636e278/pyrcs/other_assets).

**For more information and detailed specifications, check out [PyRCS 0.2.13 documentation](https://pyrcs.readthedocs.io/en/0.2.13/).** 

<br/>

## **[0.2.12](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.12)**

(*11 November 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.11...0.2.12) since [0.2.11](https://pypi.org/project/pyrcs/0.2.11/):**

- Enabled an offline mode (when Internet connection is lost).
- Renamed the following:
  - class methods: 
    - in the class [SignalBoxes](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/sig_box.py#L28):
      - [~~.collect_signal_box_prefix_codes()~~](https://github.com/mikeqfu/pyrcs/commit/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40#diff-325f75b3f2452c2629af384b19046b16d42d4500c6cba2ca5cf0db5fc0772f4bL99) to [.collect_prefix_codes()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/sig_box.py#L107);
      - [~~.fetch_signal_box_prefix_codes()~~](https://github.com/mikeqfu/pyrcs/commit/8996f89566f53b4d2e24d8f99b1e0b0444ee0b40#diff-325f75b3f2452c2629af384b19046b16d42d4500c6cba2ca5cf0db5fc0772f4bL188) to [.fetch_prefix_codes()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/sig_box.py#L203);
    - in the class [Tunnels](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/tunnel.py#L27):
      - [~~.collect_tunnel_lengths_by_page()~~](https://github.com/mikeqfu/pyrcs/commit/a2df5ad0f6d6a8758a9f0ac122487f09a1ec0a61#diff-d4156e818eca514e7b6c1b2bfbf2ac0a4a1ee2392a31b56a2c5771e87fae14c1L167) to [.collect_lengths_by_page()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/tunnel.py#L177);
    - in the class [Viaducts](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/viaduct.py#L23):
      - [~~.collect_railway_viaducts_by_page()~~](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efL82) to [.collect_viaduct_codes_by_page()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/viaduct.py#L99);
      - [~~.fetch_railway_viaducts()~~](https://github.com/mikeqfu/pyrcs/commit/aa5325bc12b84b0f18ef39548efc1f7d268d5347#diff-f4e1105c5b49529eafc015218cb58dc9b9483837fb76542988186546b44745efL151) to [.fetch_viaduct_codes()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/other_assets/viaduct.py#L177);
  - functions in the module [utils](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py):
    - [~~fetch_location_names_repl_dict()~~](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L952) to [fetch_loc_names_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py#L1037);
    - [~~update_location_name_repl_dict()~~](https://github.com/mikeqfu/pyrcs/commit/e923c3780a5f8dbe856f0d19a87fb09cd3ae7315#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L1009) to [update_loc_names_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py#L1094).
- Removed the functions [~~collect_site_map()~~](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL20) and [~~fetch_site_map()~~](https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL110) from the module [updater](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/updater.py). 
- Added the following:
  - a new module [collector](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/collector.py) - combining two modules [~~_line_data~~](https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-51811be1398d2439ca84a8504b8531b0411773c357881c423df0922f44e6923b) and [~~_other_assets~~](https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-b7304475ca50edd2572798e94bb2d0d5e2f627c6f5470d1ad24722efdb803609);
  - new functions [print_connection_error()](https://github.com/mikeqfu/pyrcs/commit/2886648b04174692ff0be58183ec56da27d1c120#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1192-R1205), [print_conn_err()](https://github.com/mikeqfu/pyrcs/commit/b42f0e36a5f231763fd8879c3e50f2e83ca000c4#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1206-R1225), [is_internet_connected()](https://github.com/mikeqfu/pyrcs/commit/03486c21048282d9033bda915924a70f1033645e#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282R1262-R1283) and [get_site_map()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py#L631) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py);
  - a new method [TrackDiagrams.get_track_diagrams_items()](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/line_data/trk_diagr.py#L85) - adapted from the function [~~get_track_diagrams_items()~~](https://github.com/mikeqfu/pyrcs/commit/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56#diff-3bd1279c5db5b09065ddf6468e4acfb650e3402d8b0c410ce7beaacb667a8135R78) previously in the module [utils](https://github.com/mikeqfu/pyrcs/blob/bb66ee658a2b60e2ffe5e16381e8737b57c65b3d/pyrcs/utils.py).
- Enabled direct access to all classes from importing the package, without having to specifying the sub-modules in which they each reside.

**For more information and detailed specifications, check out [PyRCS 0.2.12 documentation](https://pyrcs.readthedocs.io/en/0.2.12/).** 

<br/>

## **[0.2.11](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.11)**

(*31 October 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.10...0.2.11) since [0.2.10](https://pypi.org/project/pyrcs/0.2.10/):**

- Renamed the following methods of the class [Stations](https://github.com/mikeqfu/pyrcs/blob/81fe73e419597868e58731cb9417f4583b5a3611/pyrcs/other_assets/station.py#L31):
  - [~~.collect_railway_station_data_by_initial()~~](https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c#diff-86956d6a0963926f04ed9d7c6bf99fb9763a0c7cabb22c88c3fa8f68e5a31e19L127) to [.collect_station_data_by_initial()](https://github.com/mikeqfu/pyrcs/blob/81fe73e419597868e58731cb9417f4583b5a3611/pyrcs/other_assets/station.py#L127);
  - [~~.fetch_railway_station_data()~~](https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c#diff-86956d6a0963926f04ed9d7c6bf99fb9763a0c7cabb22c88c3fa8f68e5a31e19L246) to [.fetch_station_data()](https://github.com/mikeqfu/pyrcs/blob/81fe73e419597868e58731cb9417f4583b5a3611/pyrcs/other_assets/station.py#L245).

**For more information and detailed specifications, check out [PyRCS 0.2.11 documentation](https://pyrcs.readthedocs.io/en/0.2.11/).** 

<br/>

## **[0.2.10](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.10)**

(*25 October 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.9...0.2.10) since [0.2.9](https://pypi.org/project/pyrcs/0.2.9/):**

- Renamed the following sub-modules **(with minor modifications)**:
  - [~~crs_nlc_tiploc_stanox~~](https://github.com/mikeqfu/pyrcs/commit/095b9d946e3c1f4a72b33ee1926f41654914f27c) to [loc_id](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/loc_id.py);
  - [~~electrification~~](https://github.com/mikeqfu/pyrcs/commit/e3b8bf752403b2d962528723b40977d0172e7182) to [elec](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/elec.py);
  - [~~track_diagrams~~](https://github.com/mikeqfu/pyrcs/commit/5712990892792d404cb9c883f313abcb0848479b) to [trk_diagr](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/trk_diagr.py);
  - [~~tunnels~~](https://github.com/mikeqfu/pyrcs/commit/31854d6d2e98690c5d92ee074cdb8a03e293e987) to [tunnel](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/tunnel.py).
- Renamed the following modules **(without modifications)**:
  - [~~elrs_mileages~~](https://github.com/mikeqfu/pyrcs/commit/22b05dab9a51ffa69849be04ff26a5d8d444f9ca) to [elr_mileage](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/elr_mileage.py);
  - [~~line_names~~](https://github.com/mikeqfu/pyrcs/commit/0c7130c122cb9f55ce721711cf02935cb0f86e60) to [line_name](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/line_name.py);
  - [~~lor_codes~~](https://github.com/mikeqfu/pyrcs/commit/12e4cd04e598f9d74a0b4eb7f616b9f9e24e4b5e) to [lor_code](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/line_data/lor_code.py);
  - [~~depots~~](https://github.com/mikeqfu/pyrcs/commit/750e50c52124b2a28c121b88957bdae84eafecf6) to [depot](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/depot.py);
  - [~~features~~](https://github.com/mikeqfu/pyrcs/commit/1d9645f9c9b754cf507f0c6b60ea96a26a3d105c) to [feature](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/feature.py);
  - [~~signal_boxes~~](https://github.com/mikeqfu/pyrcs/commit/8cd5a1eba435d8a961b2065a1e61a12c04d91248) to [sig_box](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/sig_box.py);
  - [~~stations~~](https://github.com/mikeqfu/pyrcs/commit/e0814219e719b82325dd5ff6c308f4a45cc43818) to [station](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/station.py);
  - [~~viaducts~~](https://github.com/mikeqfu/pyrcs/commit/b3d89ed5948319fc547737e752debb460b85991c) to [viaduct](https://github.com/mikeqfu/pyrcs/blob/6a15470d22d8b2118ae59b688768cad92da92c34/pyrcs/other_assets/viaduct.py).

**For more information and detailed specifications, check out [PyRCS 0.2.10 documentation](https://pyrcs.readthedocs.io/en/0.2.10/).**

<br/>

## **[0.2.9](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.9)**

(*13 September 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.8...0.2.9) since [0.2.8](https://pypi.org/project/pyrcs/0.2.8/):**

- Updated pre-packed data

**For more information and detailed specifications, check out [PyRCS 0.2.9 documentation](https://pyrcs.readthedocs.io/en/0.2.9/).** 

<br/>

## **[0.2.8](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.8)**

(*13 September 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.7...0.2.8) since [0.2.7](https://pypi.org/project/pyrcs/0.2.7/):**

- Removed the function [~~fake_requests_headers()~~](https://github.com/mikeqfu/pyrcs/commit/4bcd0a2e329f37d7c74a3b5b9b3d9e56ba5df508#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L547-L562) from the module [utils](https://github.com/mikeqfu/pyrcs/blob/4bcd0a2e329f37d7c74a3b5b9b3d9e56ba5df508/pyrcs/utils.py).
- Made modifications with bug fixes to: 
  - the class [ELRMileages](https://github.com/mikeqfu/pyrcs/commit/8849e0d33b70e68a1c80e9ec3d49edcc1fc8a21a) in the sub-module [elrs_mileages](https://github.com/mikeqfu/pyrcs/blob/7d50599fcef5b038756ff39d30a531dd46d76c97/pyrcs/line_data/elrs_mileages.py);
  - the function [nr_mileage_num_to_str()](https://github.com/mikeqfu/pyrcs/commit/dbf794d6c4ac176b8b5220f3931d65dd237f3d45) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/4bcd0a2e329f37d7c74a3b5b9b3d9e56ba5df508/pyrcs/utils.py).
- Improved [all sub-modules](https://github.com/mikeqfu/pyrcs/commit/983069544949bd3158c5821787aeaf455d2e8511) with any specified input data directory being validated.
- Added a new function [fix_nr_mileage_str()](https://github.com/mikeqfu/pyrcs/commit/bc9ec4d9789e74851832fd548959bfc5d41f0041) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/4bcd0a2e329f37d7c74a3b5b9b3d9e56ba5df508/pyrcs/utils.py).

**For more information and detailed specifications, check out [PyRCS 0.2.8 documentation](https://pyrcs.readthedocs.io/en/0.2.8/).** 

<br/>

## **[0.2.7](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.7)**

(*18 July 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.6...0.2.7) since [0.2.6](https://pypi.org/project/pyrcs/0.2.6/):**

- Renamed the sub-packages (with modifications to all of their sub-modules): 
  - [~~line_data_cls~~](https://github.com/mikeqfu/pyrcs/commit/af64bddcbf15e60743e7339f0423c1872bbf3d8e) to [line_data](https://github.com/mikeqfu/pyrcs/tree/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/line_data);
  - [~~other_assets_cls~~](https://github.com/mikeqfu/pyrcs/commit/1939baac8d176ac5be992dd6f94c046b45b71555) to [other_assets](https://github.com/mikeqfu/pyrcs/tree/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/other_assets).
- Renamed the modules:
  - [~~line_data~~](https://github.com/mikeqfu/pyrcs/commit/6784edee320bb0de5e4d472965df95c4819a8e5a) to [_line_data](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/_line_data.py);
  - [~~other_assets~~](https://github.com/mikeqfu/pyrcs/commit/49e5f4bd0e2c9ee835cdfcb2b9d872c0ac9bb40f) to [_other_assets](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/_other_assets.py);
  - [~~update~~](https://github.com/mikeqfu/pyrcs/blob/67f07a14d8e5d527cd86c85163b4d38c4278af26/pyrcs/update.py) to [updater](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py).
- Renamed the function [~~update_pkg_metadata()~~](https://github.com/mikeqfu/pyrcs/commit/116d415eb13b46fced36925d129a29b943fc8c53#diff-4527118d31dfdca143242274ac926ded7c6824b2a95a6b8304bd6c16585a1995L11) to [update_backup_data()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py#L132) in the module [updater](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py). 
- Removed the module [~~rc_psql~~](https://github.com/mikeqfu/pyrcs/commit/9ab958fa6ae7df12893509376d91535c52280e31).
- Improved the module [utils](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/utils.py) with [bug fixes](https://github.com/mikeqfu/pyrcs/commit/be2cd82881420a97784f28f6d3d16d5a4264aa28).
- Added new functions:
  - [collect_site_map()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py#L17) and [fetch_site_map()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py#L88) to the module [updater](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/updater.py);
  - [homepage_url()](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/utils.py#L21) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/0e33eb393089fa706daedf31f1475dd3493c82ae/pyrcs/utils.py).

<br/>

## **[0.2.6](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.6)**

(*8 March 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.5...0.2.6) since [0.2.5](https://pypi.org/project/pyrcs/0.2.5/):**

- Added a new function [fix_num_stanox()](https://github.com/mikeqfu/pyrcs/blob/6b4c9214767f5b37a00ed374a049ab09ac9706b1/pyrcs/utils.py#L600) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/6b4c9214767f5b37a00ed374a049ab09ac9706b1/pyrcs/utils.py).

<br/>

## **[0.2.5](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.5)**

(*10 January 2020*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.4...0.2.5) since [0.2.4](https://pypi.org/project/pyrcs/0.2.4/):**

- Renamed the function [~~update_package_data()~~](https://github.com/mikeqfu/pyrcs/commit/e46e17002cd048db63dc5c7c0e074b4162377705) to [update_pkg_metadata()](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/update.py#L11) in the module [update](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/update.py).
- Improved the [keys of the dict-type data](https://github.com/mikeqfu/pyrcs/commit/48e2b908984f940c3abe3aba5899de5fe8c285cc) for relevant methods of the two classes: [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/line_data_cls/elrs_mileages.py#L244) and [SignalBoxes](https://github.com/mikeqfu/pyrcs/blob/e53a7e56146b2c20ca91e6aa278b1c333c09e69a/pyrcs/other_assets_cls/signal_boxes.py#L18).

<br/>

## **[0.2.4](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.4)**

(*4 December 2019*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.3...0.2.4) since [0.2.3](https://pypi.org/project/pyrcs/0.2.3/):**

- Removed the module [~~settings~~](https://github.com/mikeqfu/pyrcs/commit/8e6340bfe078f0cd558f059f89ef1d5029ef62b4).
- Updated [import statements](https://github.com/mikeqfu/pyrcs/commit/aca6383be837a241ff0012a53a33ce5469cf676f) in some modules/sub-modules due to changes in their dependencies.
- Made [some modifications](https://github.com/mikeqfu/pyrcs/commit/0a31277fec3d87f6fe0b561a3b16d013cdd9eb8b) to a few sub-modules due to changes in the corresponding web pages of the Railway Codes website.

<br/>

## **[0.2.3](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.3)**

(*4 October 2019*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.2...0.2.3) since [0.2.2](https://pypi.org/project/pyrcs/0.2.2/):**

- Fixed [a few bugs](https://github.com/mikeqfu/pyrcs/commit/7872dc917065623f3cb5f7939a065900c6070af4) in the module [utils](https://github.com/mikeqfu/pyrcs/blob/f0d8f3b271234fd6710ff6dd4dae9b6315db6c01/pyrcs/utils.py).

<br/>

## **[0.2.2](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.2)**

(*27 September 2019*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.1...0.2.2) since [0.2.1](https://pypi.org/project/pyrcs/0.2.1/):**

- Improved the methods [.collect_mileage_file_by_elr()](https://github.com/mikeqfu/pyrcs/commit/3a4b210c8373de14de7740c9ca874db100687200) and [.get_conn_mileages()](https://github.com/mikeqfu/pyrcs/commit/bc45055b6d07f83bddadd29c590226d7ddb9a7d3) of the class [ELRMileages](https://github.com/mikeqfu/pyrcs/blob/4f4f3c765948f935bd8160071082c2b16237f1db/pyrcs/line_data_cls/elrs_mileages.py#L244) with bug fixes.

<br/>

## **[0.2.1](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.1)**

(*18 September 2019*)

### Notable [changes](https://github.com/mikeqfu/pyrcs/compare/0.2.0...0.2.1) since [0.2.0](https://pypi.org/project/pyrcs/0.2.0/):**

- Removed the function [~~is_float()~~](https://github.com/mikeqfu/pyrcs/commit/80fed8c2fb3096457a20e543af5f15cb55f40407#diff-b10b1cca28c0fc2ed0bdb1f92c3c9f58dcc4279b09ad28a2a4c513a35861c282L436-L442) from the module [utils](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py).
- Added new functions: 
  - [is_str_float()](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/line_data_cls/elrs_mileages.py#L33) to the module [elrs_mileages](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/line_data_cls/elrs_mileages.py);
  - [fetch_location_names_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py#L440) and [update_location_name_repl_dict()](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py#L465) to the module [utils](https://github.com/mikeqfu/pyrcs/blob/036453c38c35f12183d5adc0fde88ffd5f402110/pyrcs/utils.py).

<br/>

## **[0.2.0](https://github.com/mikeqfu/pyrcs/releases/tag/0.2.0)**

(*29 August 2019*)

This is a release of a **brand-new** version.

*Note that the initial releases (of early versions up to **~~0.1.28~~**) had been permanently deleted.*
