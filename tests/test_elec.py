from pyrcs.line_data.elec import Electrification

if __name__ == '__main__':
    electrification = Electrification()

    test_data_dir = "dat"

    print("\n{}: ".format(electrification.Name))
    # Electrification masts and related features:

    national_network_ole1 = electrification.fetch_national_network_codes()
    national_network_ole1_ = national_network_ole1[electrification.NationalNetworkKey]
    print(f"\n  {electrification.NationalNetworkKey}: ")
    for k, v in national_network_ole1_.items():
        for k_, v_ in v.items():
            if k_ == 'Notes':
                print(f"\n      {k_}:\n        {type(v_)}")
            else:
                print(f"\n      {k}:\n        {type(v_)}, {v_.shape}")
    #   National network:
    #
    #       Traditional numbering system (distance and sequence):
    #         <class 'pandas.core.frame.DataFrame'>, (547, 4)
    #
    #       Notes:
    #         <class 'dict'>
    #
    #       New numbering system (km and decimal):
    #         <class 'pandas.core.frame.DataFrame'>, (28, 3)
    #
    #       Notes:
    #         <class 'str'>
    #
    #       Codes not certain (confirmation is welcome):
    #         <class 'pandas.core.frame.DataFrame'>, (2, 4)
    #
    #       Notes:
    #         <class 'NoneType'>
    #
    #       Suspicious data:
    #         <class 'pandas.core.frame.DataFrame'>, (7, 4)
    #
    #       Notes:
    #         <class 'str'>
    #
    #       An odd one to complete the record:
    #         <class 'pandas.core.frame.DataFrame'>, (1, 3)
    #
    #       Notes:
    #         <class 'NoneType'>
    #
    #       LBSC/Southern Railway overhead system:
    #         <class 'pandas.core.frame.DataFrame'>, (15, 1)
    #
    #       Notes:
    #         <class 'str'>
    #
    #       Codes not known:
    #         <class 'pandas.core.frame.DataFrame'>, (9, 1)
    #
    #       Notes:
    #         <class 'str'>

    national_network_ole2 = electrification.fetch_national_network_codes(
        update=True, pickle_it=True, data_dir=test_data_dir)
    national_network_ole2_ = national_network_ole2[electrification.NationalNetworkKey]
    print("\n    {} data is consistent:".format(electrification.Key),
          all(x['Codes'].equals(y['Codes'])
              for x, y in
              zip(national_network_ole1_.values(), national_network_ole2_.values())))
    #     Electrification data is consistent: True

    independent_lines_ole1 = electrification.fetch_indep_lines_codes()
    independent_lines_ole1_ = independent_lines_ole1[electrification.IndependentLinesKey]

    print(f"\n  {electrification.IndependentLinesKey}: ")
    for k, v in independent_lines_ole1_.items():
        # print(f"\n    {k}:\n      {type(v)}")
        for k_, v_ in v.items():
            if k_ == 'Notes':
                print(f"\n        {k_}:\n          {type(v_)}, {v_}")
            elif k_ == 'Codes':
                if v_ is not None:
                    print(f"\n      {k}:\n        {type(v_)}, {v_.shape}")
                else:
                    print(f"\n      {k}:\n        {type(v_)}")

    independent_lines_ole2 = electrification.fetch_indep_lines_codes(
        update=True, pickle_it=True, data_dir=test_data_dir)
    independent_lines_ole2_ = independent_lines_ole2[electrification.IndependentLinesKey]
    print("\n    {} data is consistent:".format(electrification.IndependentLinesKey),
          all((x == y) for x, y in zip(independent_lines_ole1_, independent_lines_ole2_)))
    #     Independent lines data is consistent: True

    ohns_codes1 = electrification.fetch_ohns_codes()
    ohns_codes1_ = ohns_codes1[electrification.OhnsKey]

    print(f"\n  {electrification.OhnsKey}:\n    {type(ohns_codes1_)}, "
          f"{ohns_codes1_.shape}")
    print(f"\n    {electrification.LUDKey}: {ohns_codes1[electrification.LUDKey]}")

    ohns_codes2 = electrification.fetch_ohns_codes(
        update=True, pickle_it=True, data_dir=test_data_dir)
    ohns_codes2_ = ohns_codes2[electrification.OhnsKey]
    print("\n    {} data is consistent:".format(electrification.OhnsKey),
          ohns_codes1_.equals(ohns_codes2_))

    etz_ole1 = electrification.fetch_etz_codes()
    etz_ole1_ = etz_ole1[electrification.TariffZonesKey]

    print(f"\n  {electrification.TariffZonesKey}: ")
    for k, v in etz_ole1_.items():
        if isinstance(v, str):
            print(f"\n      {k}:\n        {type(v)}, {v}")
        else:
            print(f"\n      {k}:\n        {type(v)}, {v.shape}")

    etz_ole2 = electrification.fetch_etz_codes(
        update=True, pickle_it=True, data_dir=test_data_dir)
    etz_ole2_ = etz_ole2[electrification.TariffZonesKey]
    print("\n    {} data is consistent:".format(electrification.TariffZonesKey),
          all((x == y) for x, y in zip(etz_ole1_, etz_ole2_)))
