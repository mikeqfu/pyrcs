from pyrcs.other_assets.feature import Features

if __name__ == '__main__':
    features = Features()

    test_data_dir = "dat"

    print("\n{}: ".format(features.Name))
    # Infrastructure features:

    habds_and_wilds_codes_data1 = features.fetch_habds_and_wilds()
    habds_and_wilds_codes_data1_ = habds_and_wilds_codes_data1[features.HabdWildKey]

    print(f"\n  {features.HabdWildKey}: ")
    for k, v in habds_and_wilds_codes_data1_.items():
        print(f"\n    {k}:\n      {type(v)}, {v.shape}")
    #   HABD and WILD:
    #
    #     HABD:
    #       <class 'pandas.core.frame.DataFrame'>, (232, 5)
    #
    #     WILD:
    #       <class 'pandas.core.frame.DataFrame'>, (44, 5)

    habds_and_wilds_codes_data2 = features.fetch_habds_and_wilds(
        update=True, pickle_it=True, data_dir=test_data_dir)
    habds_and_wilds_codes_data2_ = habds_and_wilds_codes_data2[features.HabdWildKey]
    print("\n    {} data is consistent:".format(features.HabdWildKey),
          all((x == y) for x, y in
              zip(habds_and_wilds_codes_data1_, habds_and_wilds_codes_data2_)))
    #     HABD and WILD data is consistent: True

    water_troughs_locations1 = features.fetch_water_troughs()
    water_troughs_locations1_ = water_troughs_locations1[features.WaterTroughsKey]

    print(f"\n  {features.WaterTroughsKey}:\n    {type(water_troughs_locations1_)}, "
          f"{water_troughs_locations1_.shape}")
    print(f"\n    {features.LUDKey}: {water_troughs_locations1[features.LUDKey]}")
    #   Telegraphic codes:
    #
    #     Official codes:
    #       <class 'pandas.core.frame.DataFrame'>, (160, 3)
    #
    #     Unofficial codes:
    #       <class 'pandas.core.frame.DataFrame'>, (7, 2)

    water_troughs_locations2 = features.fetch_water_troughs(
        update=True, pickle_it=True, data_dir=test_data_dir)
    water_troughs_locations2_ = water_troughs_locations2[features.WaterTroughsKey]
    print("\n    {} data is consistent:".format(features.WaterTroughsKey),
          water_troughs_locations1_.equals(water_troughs_locations2_))
    #     Telegraphic codes data is consistent: True

    telegraph_code_words1 = features.fetch_telegraph_codes()
    telegraph_code_words1_ = telegraph_code_words1[features.TelegraphKey]

    print(f"\n  {features.TelegraphKey}: ")
    for k, v in telegraph_code_words1_.items():
        print(f"\n    {k}:\n      {type(v)}, {v.shape}")
    #   Telegraphic codes:
    #
    #     Official codes:
    #     <class 'pandas.core.frame.DataFrame'>, (160, 3)
    #
    #     Unofficial codes:
    #     <class 'pandas.core.frame.DataFrame'>, (7, 2)

    telegraph_code_words2 = features.fetch_telegraph_codes(
        update=True, pickle_it=True, data_dir=test_data_dir)
    telegraph_code_words2_ = telegraph_code_words2[features.TelegraphKey]
    print("\n    {} data is consistent:".format(features.TelegraphKey),
          all((x == y) for x, y in zip(telegraph_code_words1_, telegraph_code_words2_)))
    #     Telegraphic codes data is consistent: True

    buzzer_codes_data1 = features.fetch_buzzer_codes()
    buzzer_codes_data1_ = buzzer_codes_data1[features.BuzzerKey]

    print(f"\n  {features.BuzzerKey}:\n    {type(buzzer_codes_data1_)}, "
          f"{buzzer_codes_data1_.shape}")
    print(f"\n    {features.LUDKey}: {buzzer_codes_data1[features.LUDKey]}")
    #   Buzzer codes:
    #     <class 'pandas.core.frame.DataFrame'>, (13, 2)
    #
    #     Last updated date: 2019-11-24

    buzzer_codes_data2 = features.fetch_buzzer_codes(
        update=True, pickle_it=True, data_dir=test_data_dir)
    buzzer_codes_data2_ = buzzer_codes_data2[features.BuzzerKey]
    print("\n    {} data is consistent:".format(features.BuzzerKey),
          buzzer_codes_data1_.equals(buzzer_codes_data2_))
    #     Buzzer codes data is consistent: True

    features_codes = features.fetch_features_codes()
    features_codes_ = features_codes[features.Key]
    print(f"\n{features.Key}: ")
    for k, v in features_codes_.items():
        print(f"\n  {k}:\n    {type(v)}")
    # Features:
    #
    #   Buzzer codes:
    #     <class 'pandas.core.frame.DataFrame'>
    #
    #   HABD and WILD:
    #     <class 'dict'>
    #
    #   Telegraphic codes:
    #     <class 'dict'>
    #
    #   Water troughs:
    #     <class 'pandas.core.frame.DataFrame'>
    #
    #   National network neutral sections:
    #     <class 'pandas.core.frame.DataFrame'>
