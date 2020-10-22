from pyrcs.line_data.lor_code import LOR

if __name__ == '__main__':
    lor = LOR()

    test_data_dir = "dat"

    print("\n{}: ".format(lor.Name))
    # Line of Route (LOR/PRIDE) codes:

    elr_lor_converter1 = lor.fetch_elr_lor_converter()
    elr_lor_converter1_ = elr_lor_converter1[lor.ELCKey]

    print(f"\n  {lor.ELCKey}:\n    {type(elr_lor_converter1_)}, "
          f"{elr_lor_converter1_.shape}")
    print(f"\n    {lor.LUDKey}: {elr_lor_converter1[lor.LUDKey]}")
    #   ELR/LOR converter:
    #     <class 'pandas.core.frame.DataFrame'>, (1354, 6)
    #
    #     Last updated date: 2019-11-15

    elr_lor_converter2 = lor.fetch_elr_lor_converter(update=True, pickle_it=True,
                                                     data_dir=test_data_dir)
    elr_lor_converter2_ = elr_lor_converter2[lor.ELCKey]
    print("\n    {} data is consistent:".format(lor.ELCKey),
          elr_lor_converter1_.equals(elr_lor_converter2_))
    #     ELR/LOR converter data is consistent: True

    lor_codes_data1 = lor.fetch_lor_codes()
    lor_codes_data1_ = lor_codes_data1[lor.Key]

    print(f"\n  {lor.Key}: ")
    for k, v in lor_codes_data1_.items():
        print(f"\n      {k}:\n        {type(v)}")
    #   LOR:
    #
    #       CY:
    #         <class 'dict'>
    #
    #       EA:
    #         <class 'dict'>
    #
    #       GW:
    #         <class 'dict'>
    #
    #       LN:
    #         <class 'dict'>
    #
    #       MD:
    #         <class 'dict'>
    #
    #       NW/NZ:
    #         <class 'dict'>
    #
    #       SC:
    #         <class 'dict'>
    #
    #       SO:
    #         <class 'dict'>
    #
    #       SW:
    #         <class 'dict'>
    #
    #       XR:
    #         <class 'dict'>

    lor_codes_data2 = lor.fetch_lor_codes(update=True, pickle_it=True,
                                          data_dir=test_data_dir)
    lor_codes_data2_ = lor_codes_data2[lor.Key]

    print("\n    {} data is consistent:".format(lor.Key),
          all((x == y) for x, y in zip(lor_codes_data1_, lor_codes_data2_)))
    #     LOR data is consistent: True
