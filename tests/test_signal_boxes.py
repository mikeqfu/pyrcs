from pyrcs.other_assets.signal_boxes import SignalBoxes

if __name__ == '__main__':

    signal_boxes = SignalBoxes()

    test_data_dir = "tests\\dat"

    print("\n{}: ".format(signal_boxes.Name))

    signal_box_prefix_codes1 = signal_boxes.fetch_signal_box_prefix_codes()
    signal_box_prefix_codes1_ = signal_box_prefix_codes1[signal_boxes.Key]

    print(f"\n  {signal_boxes.Key}:\n  {type(signal_box_prefix_codes1_)}")
    print("\n  {}: {}".format(signal_boxes.LUDKey, signal_box_prefix_codes1[signal_boxes.LUDKey]))

    signal_box_prefix_codes2 = signal_boxes.fetch_signal_box_prefix_codes(update=True, pickle_it=True,
                                                                          data_dir=test_data_dir)
    signal_box_prefix_codes2_ = signal_box_prefix_codes2[signal_boxes.Key]
    print("  {} data is consistent:".format(signal_boxes.Key),
          all((x == y) for x, y in zip(signal_box_prefix_codes1, signal_box_prefix_codes2)))

    # Non-national rail
    non_national_rail_codes_data1 = signal_boxes.fetch_non_national_rail_codes()
    non_national_rail_codes_data1_ = non_national_rail_codes_data1[signal_boxes.NonNationalRailKey]

    print("\n\n  {}: ".format(signal_boxes.NonNationalRailKey))
    for k, v in non_national_rail_codes_data1_.items():
        print(f"\n    {k}:\n    {type(v)}")
    print("\n  {}: {}".format(signal_boxes.LUDKey, non_national_rail_codes_data1[signal_boxes.LUDKey]))

    non_national_rail_codes_data2 = signal_boxes.fetch_non_national_rail_codes(update=True, pickle_it=True,
                                                                               data_dir=test_data_dir)
    non_national_rail_codes_data2_ = non_national_rail_codes_data2[signal_boxes.NonNationalRailKey]
    print("  {} data is consistent:".format(signal_boxes.NonNationalRailKey),
          all((x == y) for x, y in zip(non_national_rail_codes_data1, non_national_rail_codes_data2)))
    # Data is consistent: True
