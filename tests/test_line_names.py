from pyrcs.line_data.line_names import LineNames

if __name__ == '__main__':
    line_names = LineNames()

    test_data_dir = "dat"

    print("\n{}: ".format(line_names.Name))
    # Railway line names:

    line_names_data1 = line_names.fetch_line_names()
    line_names_data1_ = line_names_data1[line_names.Key]

    print(f"\n  {line_names.Key}:\n    {type(line_names_data1_)}, {line_names_data1_.shape}")
    print(f"\n    {line_names.LUDKey}: {line_names_data1[line_names.LUDKey]}")
    #   Line names:
    #     <class 'pandas.core.frame.DataFrame'>, (125, 3)
    #
    #     Last updated date: 2019-10-16

    line_names_data2 = line_names.fetch_line_names(update=True, pickle_it=True, data_dir=test_data_dir)
    line_names_data2_ = line_names_data2[line_names.Key]

    print("\n    {} data is consistent:".format(line_names.Key), line_names_data1_.equals(line_names_data2_))
    #     Line names data is consistent: True
