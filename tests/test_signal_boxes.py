from pyrcs.other_assets.signal_boxes import SignalBoxes

if __name__ == '__main__':

    signal_boxes = SignalBoxes()

    test_data_dir = "dat"

    print("\n{}: ".format(signal_boxes.Name))
    # Signal box prefix codes:

    signal_box_prefix_codes1 = signal_boxes.fetch_signal_box_prefix_codes()
    signal_box_prefix_codes1_ = signal_box_prefix_codes1[signal_boxes.Key]

    print(f"\n  {signal_boxes.Key}:\n    {type(signal_box_prefix_codes1_)}, {signal_box_prefix_codes1_.shape}")
    print("\n  {}: {}".format(signal_boxes.LUDKey, signal_box_prefix_codes1[signal_boxes.LUDKey]))
    #   Signal boxes:
    #     <class 'pandas.core.frame.DataFrame'>, (5507, 8)
    #
    #   Last updated date: xxxx-xx-xx

    signal_box_prefix_codes2 = signal_boxes.fetch_signal_box_prefix_codes(update=True, pickle_it=True,
                                                                          data_dir=test_data_dir)
    signal_box_prefix_codes2_ = signal_box_prefix_codes2[signal_boxes.Key]
    print("\n  {} data is consistent:".format(signal_boxes.Key),
          signal_box_prefix_codes1_.equals(signal_box_prefix_codes2_))
    #   Signal boxes data is consistent: True

    non_national_rail_codes_data1 = signal_boxes.fetch_non_national_rail_codes()
    non_national_rail_codes_data1_ = non_national_rail_codes_data1[signal_boxes.NonNationalRailKey]

    print("\n\n  {}: ".format(signal_boxes.NonNationalRailKey))
    for k, v in non_national_rail_codes_data1_.items():
        if v is None:
            print(f"\n    {k}:\n    {type(v)}")
        elif isinstance(v, str):
            print(f"\n    {k}:\n    {type(v)}, {v}")
        else:
            print(f"\n    {k}:\n    {type(v)}, {v.shape}")
    #   Non-National Rail:
    #
    #     Croydon Tramlink signals:
    #     <class 'NoneType'>
    #
    #     Notes:
    #     <class 'str'>, Signal boxes without known prefixes are excluded.
    #
    #     Docklands Light Railway signals:
    #     <class 'NoneType'>
    #
    #     Edinburgh Tramway signals:
    #     <class 'pandas.core.frame.DataFrame'>, (4, 2)
    #
    #     Glasgow Subway signals:
    #     <class 'NoneType'>
    #
    #     London Underground signals:
    #     <class 'pandas.core.frame.DataFrame'>, (485, 5)
    #
    #     Luas signals:
    #     <class 'NoneType'>
    #
    #     Manchester Metrolink signals:
    #     <class 'pandas.core.frame.DataFrame'>, (21, 2)
    #
    #     Midland Metro signals:
    #     <class 'NoneType'>
    #
    #     Nottingham Tram signals:
    #     <class 'NoneType'>
    #
    #     Sheffield Supertram signals:
    #     <class 'NoneType'>
    #
    #     Tyne & Wear Metro signals:
    #     <class 'NoneType'>
    #
    #     Heritage, minor and miniature railways and other "special" signals:
    #     <class 'pandas.core.frame.DataFrame'>, (128, 4)

    print("\n  {}: {}".format(signal_boxes.LUDKey, non_national_rail_codes_data1[signal_boxes.LUDKey]))
    #  Last updated date: xxxx-xx-xx

    non_national_rail_codes_data2 = signal_boxes.fetch_non_national_rail_codes(update=True, pickle_it=True,
                                                                               data_dir=test_data_dir)
    non_national_rail_codes_data2_ = non_national_rail_codes_data2[signal_boxes.NonNationalRailKey]
    print("\n  {} data is consistent:".format(signal_boxes.NonNationalRailKey),
          all((x == y) for x, y in zip(non_national_rail_codes_data1_, non_national_rail_codes_data2_)))
    #   Non-National Rail data is consistent: True
