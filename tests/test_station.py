from pyrcs.other_assets.stations import Stations

if __name__ == '__main__':

    stations = Stations()

    railway_station_data1 = stations.fetch_railway_station_data()

    railway_station_data1_ = railway_station_data1[stations.StnKey]
    print("\n{}: ".format(stations.Name))
    print(type(railway_station_data1_))
    print("\n{}: {}".format(stations.LUDKey, railway_station_data1[stations.LUDKey]))
    # Stations:
    # <class 'pandas.core.frame.DataFrame'>
    #
    # Last updated date: 2020-06-29

    test_data_dir = "tests\\dat"
    railway_station_data2 = stations.fetch_railway_station_data(update=True, pickle_it=True, data_dir=test_data_dir)

    railway_station_data2_ = railway_station_data2[stations.StnKey]

    print("Data is consistent:", all((x == y) for x, y in zip(railway_station_data1, railway_station_data2)))
    # Data is consistent: True
