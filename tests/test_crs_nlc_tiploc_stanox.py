from pyrcs.line_data.crs_nlc_tiploc_stanox import LocationIdentifiers

if __name__ == '__main__':
    lid = LocationIdentifiers()

    test_data_dir = "dat"

    print("\n{}: ".format(lid.Name))

    explanatory_note1 = lid.fetch_multiple_station_codes_explanatory_note()
    explanatory_note2 = lid.fetch_multiple_station_codes_explanatory_note(update=True, pickle_it=True,
                                                                          data_dir=test_data_dir)

    print("\n    {} data is consistent:".format(lid.MSCENKey),
          all((x == y) for x, y in zip(explanatory_note1, explanatory_note2)))

    other_systems_codes1 = lid.fetch_other_systems_codes()
    other_systems_codes1_ = other_systems_codes1[lid.OSKey]

    print(f"\n  {lid.Key}: ")
    for k, v in other_systems_codes1_.items():
        print(f"\n      {k}:\n        {type(v)}, {v.shape}")

    other_systems_codes2 = lid.fetch_other_systems_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    other_systems_codes2_ = other_systems_codes2[lid.OSKey]

    print("\n    {} data is consistent:".format(lid.OSKey),
          all((x == y) for x, y in zip(other_systems_codes1_, other_systems_codes2_)))

    location_codes1 = lid.fetch_location_codes()
    location_codes1_ = location_codes1[lid.Key]

    print(f"\n  {lid.Key}:\n    {type(location_codes1_)}, {location_codes1_.shape}")
    print(f"\n    {lid.LUDKey}: {location_codes1[lid.LUDKey]}")

    location_codes2 = lid.fetch_location_codes(update=True, pickle_it=True, data_dir=test_data_dir)
    location_codes2_ = location_codes2[lid.Key]
    print("\n    {} data is consistent:".format(lid.Key), location_codes1_.equals(location_codes2_))
