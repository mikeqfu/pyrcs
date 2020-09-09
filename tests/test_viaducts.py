from pyrcs.other_assets.viaducts import Viaducts

if __name__ == '__main__':

    viaducts = Viaducts()

    railways_viaducts_data = viaducts.fetch_railway_viaducts()

    railways_viaducts_dat = railways_viaducts_data[viaducts.Key]
    print("\n{}: ".format(viaducts.Name))
    for k, v in railways_viaducts_dat.items():
        print(f"{k}:\n{type(v)}")
    print("\n{}: {}".format(viaducts.LUDKey, railways_viaducts_data[viaducts.LUDKey]))
    # Railway viaducts:
    # Page 1 (A-C):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 2 (D-G):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 3 (H-K):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 4 (L-P):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 5 (Q-S):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 6 (T-Z):
    # <class 'pandas.core.frame.DataFrame'>
    #
    # Last updated date: xxxx-xx-xx

    test_data_dir = "tests\\dat"
    railways_viaducts_data_ = viaducts.fetch_railway_viaducts(update=True, pickle_it=True, data_dir=test_data_dir)

    railways_viaducts_dat_ = railways_viaducts_data[viaducts.Key]

    print("Data is consistent:", all((x == y) for x, y in zip(railways_viaducts_data, railways_viaducts_data_)))
    # Data is consistent: True
