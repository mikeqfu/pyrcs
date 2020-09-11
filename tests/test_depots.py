from pyrcs.other_assets.depots import Depots

if __name__ == '__main__':
    depots = Depots()

    test_data_dir = "dat"

    print("\n{}: ".format(depots.Name))
    # Depot codes:

    two_char_tops_codes_data1 = depots.fetch_two_char_tops_codes()
    two_char_tops_codes_data1_ = two_char_tops_codes_data1[depots.TCTKey]

    print(f"\n  {depots.TCTKey}:\n    {type(two_char_tops_codes_data1_)}, {two_char_tops_codes_data1_.shape}")
    print(f"\n    {depots.LUDKey}: {two_char_tops_codes_data1[depots.LUDKey]}")
    #   Two character TOPS codes:
    #     <class 'pandas.core.frame.DataFrame'>, (585, 5)
    #
    #     Last updated date: xxxx-xx-xx

    two_char_tops_codes_data2 = depots.fetch_two_char_tops_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    two_char_tops_codes_data2_ = two_char_tops_codes_data2[depots.TCTKey]
    print("\n    {} data is consistent:".format(depots.TCTKey),
          two_char_tops_codes_data1_.equals(two_char_tops_codes_data2_))
    #     Two character TOPS codes data is consistent: True

    four_digit_pre_tops_codes_data1 = depots.fetch_four_digit_pre_tops_codes()
    four_digit_pre_tops_codes_data1_ = four_digit_pre_tops_codes_data1[depots.FDPTKey]

    print(f"\n  {depots.FDPTKey}: ")
    for k, v in four_digit_pre_tops_codes_data1_.items():
        print(f"\n    {k}:\n      {type(v)}, {v.shape}")
    #   Four digit pre-TOPS codes:
    #
    #     Main Works:
    #       <class 'pandas.core.frame.DataFrame'>, (14, 2)
    #
    #     London Midland Region:
    #       <class 'pandas.core.frame.DataFrame'>, (289, 2)
    #
    #     Western Region:
    #       <class 'pandas.core.frame.DataFrame'>, (140, 2)
    #
    #     Southern Region:
    #       <class 'pandas.core.frame.DataFrame'>, (67, 2)
    #
    #     Eastern Region:
    #       <class 'pandas.core.frame.DataFrame'>, (286, 2)
    #
    #     Scottish Region:
    #       <class 'pandas.core.frame.DataFrame'>, (154, 2)

    four_digit_pre_tops_codes_data2 = depots.fetch_four_digit_pre_tops_codes(update=True, pickle_it=True,
                                                                             data_dir=test_data_dir)
    four_digit_pre_tops_codes_data2_ = four_digit_pre_tops_codes_data2[depots.FDPTKey]
    print("\n    {} data is consistent:".format(depots.FDPTKey),
          all((x == y) for x, y in zip(four_digit_pre_tops_codes_data1_, four_digit_pre_tops_codes_data2_)))
    #     Four digit pre-TOPS codes data is consistent: True

    system_1950_codes_data1 = depots.fetch_1950_system_codes()
    system_1950_codes_data1_ = system_1950_codes_data1[depots.S1950Key]

    print(f"\n  {depots.S1950Key}:\n    {type(system_1950_codes_data1_)}, {system_1950_codes_data1_.shape}")
    print(f"\n    {depots.LUDKey}: {two_char_tops_codes_data1[depots.LUDKey]}")
    #   1950 system (pre-TOPS) codes:
    #     <class 'pandas.core.frame.DataFrame'>, (625, 3)
    #
    #     Last updated date: 2020-06-23

    system_1950_codes_data2 = depots.fetch_1950_system_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    system_1950_codes_data2_ = system_1950_codes_data2[depots.S1950Key]
    print("\n    {} data is consistent:".format(depots.S1950Key),
          system_1950_codes_data1_.equals(system_1950_codes_data2_))
    #     1950 system (pre-TOPS) codes data is consistent: True

    gwr_codes_data1 = depots.fetch_gwr_codes()
    gwr_codes_data1_ = gwr_codes_data1[depots.GWRKey]

    print(f"\n  {depots.GWRKey}: ")
    for k, v in gwr_codes_data1_.items():
        print(f"\n    {k}:\n      {type(v)}, {v.shape}")
    #   GWR codes:
    #
    #     Alphabetical codes:
    #       <class 'pandas.core.frame.DataFrame'>, (72, 2)
    #
    #     Numerical codes:
    #       <class 'pandas.core.frame.DataFrame'>, (145, 2)

    gwr_codes_data2 = depots.fetch_gwr_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    gwr_codes_data2_ = gwr_codes_data1[depots.GWRKey]
    print("\n    {} data is consistent:".format(depots.GWRKey),
          all((x == y) for x, y in zip(gwr_codes_data1_, gwr_codes_data2_)))
    #     GWR codes data is consistent: True

    depot_codes = depots.fetch_depot_codes()
    depot_codes_ = depot_codes[depots.Key]
    print(f"\n{depots.Key}: ")
    for k, v in depot_codes_.items():
        print(f"\n  {k}:\n    {type(v)}")
    # Depots:
    #
    #   1950 system (pre-TOPS) codes:
    #     <class 'pandas.core.frame.DataFrame'>
    #
    #   Four digit pre-TOPS codes:
    #     <class 'dict'>
    #
    #   GWR codes:
    #     <class 'dict'>
    #
    #   Two character TOPS codes:
    #     <class 'pandas.core.frame.DataFrame'>
