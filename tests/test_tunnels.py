import pandas as pd

from pyrcs.other_assets.tunnels import Tunnels

if __name__ == '__main__':

    tunnels = Tunnels()

    test_data_dir = "dat"

    railway_tunnel_lengths1 = tunnels.fetch_railway_tunnel_lengths()

    railway_tunnel_lengths1_ = railway_tunnel_lengths1[tunnels.Key]
    print("\n{}: ".format(tunnels.Name))
    for k, v in railway_tunnel_lengths1_.items():
        if isinstance(v, pd.DataFrame):
            print(f"\n  {k}:\n  {type(v)}, {v.shape}")
        elif isinstance(v, dict):
            print(f"\n  {k}:")
            for k_, v_ in v.items():
                print(f"\n    {k_}:\n    {type(v_)}, {v_.shape}")
    # Railway tunnel lengths:
    #
    #   Page 1 (A-F):
    #   <class 'pandas.core.frame.DataFrame'>, (769, 12)
    #
    #   Page 2 (G-P):
    #   <class 'pandas.core.frame.DataFrame'>, (793, 12)
    #
    #   Page 3 (Q-Z):
    #   <class 'pandas.core.frame.DataFrame'>, (598, 12)
    #
    #   Page 4 (others):
    #
    #     Tunnels on industrial and other minor lines:
    #     <class 'pandas.core.frame.DataFrame'>, (107, 6)
    #
    #     Large bridges that are not officially tunnels but could appear to be so:
    #     <class 'pandas.core.frame.DataFrame'>, (15, 9)

    print("\n{}: {}".format(tunnels.LUDKey, railway_tunnel_lengths1[tunnels.LUDKey]))
    # Last updated date: xxxx-xx-xx

    railway_tunnel_lengths2 = tunnels.fetch_railway_tunnel_lengths(update=True, pickle_it=True, data_dir=test_data_dir)

    railway_tunnel_lengths2_ = railway_tunnel_lengths2[tunnels.Key]

    print("\n{} data is consistent:".format(tunnels.Key),
          all((x == y) for x, y in zip(railway_tunnel_lengths1_, railway_tunnel_lengths2_)))
    # Tunnels data is consistent: True
