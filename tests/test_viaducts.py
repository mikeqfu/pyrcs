from pyrcs.other_assets.viaducts import Viaducts

if __name__ == '__main__':

    viaducts = Viaducts()

    test_data_dir = "dat"

    railways_viaducts_data = viaducts.fetch_railway_viaducts()

    railways_viaducts_dat = railways_viaducts_data[viaducts.Key]
    print("\n{}: ".format(viaducts.Name))
    for k, v in railways_viaducts_dat.items():
        print(f"\n  {k}:\n  {type(v)}, {v.shape}")
    # Railway viaducts:
    #
    #   Page 1 (A-C):
    #   <class 'pandas.core.frame.DataFrame'>, (526, 7)
    #
    #   Page 2 (D-G):
    #   <class 'pandas.core.frame.DataFrame'>, (317, 7)
    #
    #   Page 3 (H-K):
    #   <class 'pandas.core.frame.DataFrame'>, (186, 7)
    #
    #   Page 4 (L-P):
    #   <class 'pandas.core.frame.DataFrame'>, (447, 7)
    #
    #   Page 5 (Q-S):
    #   <class 'pandas.core.frame.DataFrame'>, (473, 7)
    #
    #   Page 6 (T-Z):
    #   <class 'pandas.core.frame.DataFrame'>, (258, 7)

    print("\n{}: {}".format(viaducts.LUDKey, railways_viaducts_data[viaducts.LUDKey]))
    # Last updated date: xxxx-xx-xx

    railways_viaducts_data_ = viaducts.fetch_railway_viaducts(update=True, pickle_it=True, data_dir=test_data_dir)

    railways_viaducts_dat_ = railways_viaducts_data[viaducts.Key]

    print("\n{} data is consistent:".format(viaducts.Key),
          all((x == y) for x, y in zip(railways_viaducts_dat, railways_viaducts_dat_)))
    # Viaducts data is consistent: True
