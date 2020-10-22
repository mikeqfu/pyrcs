from pyrcs.other_assets.station import Stations

if __name__ == '__main__':

    stations = Stations()

    test_data_dir = "dat"

    railway_station_data1 = stations.fetch_railway_station_data()

    railway_station_data1_ = railway_station_data1[stations.StnKey]
    print("\n{}: ".format(stations.Name))
    print(f"\n  {stations.StnKey}:")
    print(f"\n  {type(railway_station_data1_)}, {railway_station_data1_.shape}")
    # Stations:
    #
    #   Railway station data:
    #
    #   <class 'pandas.core.frame.DataFrame'>, (2835, 25)

    print("\n{}: {}".format(stations.LUDKey, railway_station_data1[stations.LUDKey]))
    # Last updated date: xxxx-xx-xx

    print("")

    railway_station_data2 = stations.fetch_railway_station_data(
        update=True, pickle_it=True, data_dir=test_data_dir)
    # No data is available for signal box codes beginning with "X".
    # No data is available for signal box codes beginning with "Z".

    railway_station_data2_ = railway_station_data2[stations.StnKey]

    print("\n{} data is consistent:".format(stations.StnKey),
          railway_station_data1_.equals(railway_station_data2_))
    # Railway station data is consistent: True
