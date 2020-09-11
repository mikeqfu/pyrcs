from pyrcs.other_assets.features import Features

if __name__ == '__main__':
    features = Features()

    test_data_dir = "dat"

    print("\n{}: ".format(features.Name))

    # HABDs and WILDs
    habds_and_wilds_codes_data1 = features.fetch_habds_and_wilds()
    habds_and_wilds_codes_data1_ = habds_and_wilds_codes_data1[features.HabdWildKey]

    print(f"\n  {features.HabdWildKey}: ")
    for k, v in habds_and_wilds_codes_data1_.items():
        print(f"\n    {k}:\n    {type(v)}, {v.shape}")

    habds_and_wilds_codes_data2 = features.fetch_habds_and_wilds(update=True, pickle_it=True, data_dir=test_data_dir)
    habds_and_wilds_codes_data2_ = habds_and_wilds_codes_data2[features.HabdWildKey]
    print("\n    {} data is consistent:".format(features.HabdWildKey),
          all((x == y) for x, y in zip(habds_and_wilds_codes_data1_, habds_and_wilds_codes_data2_)))

    # Water trough locations
    water_troughs_locations1 = features.fetch_water_troughs()
    water_troughs_locations1_ = water_troughs_locations1[features.WaterTroughsKey]

    print(f"\n  {features.WaterTroughsKey}:\n  {type(water_troughs_locations1_)}, {water_troughs_locations1_.shape}")
    print(f"\n  {features.LUDKey}:\n  {water_troughs_locations1[features.LUDKey]}")

    water_troughs_locations2 = features.fetch_water_troughs(update=True, pickle_it=True, data_dir=test_data_dir)
    water_troughs_locations2_ = water_troughs_locations2[features.WaterTroughsKey]
    print("\n    {} data is consistent:".format(features.WaterTroughsKey),
          water_troughs_locations1_.equals(water_troughs_locations2_))

    # Telegraph code words
    telegraph_code_words1 = features.fetch_telegraph_codes()
    telegraph_code_words1_ = telegraph_code_words1[features.TelegraphKey]

    print(f"\n  {features.TelegraphKey}: ")
    for k, v in telegraph_code_words1_.items():
        print(f"\n    {k}:\n    {type(v)}, {v.shape}")

    telegraph_code_words2 = features.fetch_telegraph_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    telegraph_code_words2_ = telegraph_code_words2[features.TelegraphKey]
    print("\n    {} data is consistent:".format(features.TelegraphKey),
          all((x == y) for x, y in zip(telegraph_code_words1_, telegraph_code_words2_)))

    # Buzzer codes
    buzzer_codes_data1 = features.fetch_buzzer_codes()
    buzzer_codes_data1_ = buzzer_codes_data1[features.BuzzerKey]

    print(f"\n  {features.BuzzerKey}:\n  {type(buzzer_codes_data1_)}, {buzzer_codes_data1_.shape}")
    print(f"\n  {features.LUDKey}:\n  {buzzer_codes_data1[features.LUDKey]}")

    buzzer_codes_data2 = features.fetch_buzzer_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    buzzer_codes_data2_ = buzzer_codes_data2[features.BuzzerKey]
    print("\n    {} data is consistent:".format(features.BuzzerKey), buzzer_codes_data1_.equals(buzzer_codes_data2_))

    # All
    features_codes = features.fetch_features_codes()
    features_codes_ = features_codes[features.Key]
    print(f"\n{features.Key}: ")
    for k, v in features_codes_.items():
        print(f"\n  {k}:\n  {type(v)}")
