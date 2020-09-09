from pyrcs.other_assets.tunnels import Tunnels

if __name__ == '__main__':

    tunnels = Tunnels()

    railway_tunnel_lengths1 = tunnels.fetch_railway_tunnel_lengths()

    railway_tunnel_lengths1_ = railway_tunnel_lengths1[tunnels.Key]
    print("\n{}: ".format(tunnels.Name))
    for k, v in railway_tunnel_lengths1_.items():
        print(f"{k}:\n{type(v)}")
    print("\n{}: {}".format(tunnels.LUDKey, railway_tunnel_lengths1[tunnels.LUDKey]))
    # Railway tunnel lengths:
    # Page 1 (A-F):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 2 (G-P):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 3 (Q-Z):
    # <class 'pandas.core.frame.DataFrame'>
    # Page 4 (others):
    # <class 'dict'>
    #
    # Last updated date: xxxx-xx-xx

    test_data_dir = "tests\\dat"
    railway_tunnel_lengths2 = tunnels.fetch_railway_tunnel_lengths(update=True, pickle_it=True, data_dir=test_data_dir)

    railway_tunnel_lengths2_ = railway_tunnel_lengths2[tunnels.Key]

    print("Data is consistent:", all((x == y) for x, y in zip(railway_tunnel_lengths1, railway_tunnel_lengths2)))
    # Data is consistent: True
