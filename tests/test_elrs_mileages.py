from pyhelpers.dir import cd
from pyhelpers.store import load_json

from pyrcs.line_data.elrs_mileages import ELRMileages

if __name__ == '__main__':
    em = ELRMileages()

    test_data_dir = "dat"

    print("\n{}: ".format(em.Name))

    elrs_data1 = em.fetch_elr()
    elrs_data1_ = elrs_data1[em.Key]

    print(f"\n  {em.Key}:\n    {type(elrs_data1_)}, {elrs_data1_.shape}")
    print(f"\n    {em.LUDKey}: {elrs_data1[em.LUDKey]}")

    elrs_data2 = em.fetch_elr(update=True, pickle_it=True, data_dir=test_data_dir)
    elrs_data2_ = elrs_data2[em.Key]
    print("\n    {} data is consistent:".format(em.Key), elrs_data1_.equals(elrs_data2_))

    # Mileage files --------------------------------------------------------------------------------------------------
    elr = 'AAL'
    elr_ = em.fetch_mileage_file(elr)
    elr_mileages = elr_['Mileage']
    print(f"\n    Mileage file for '{elr}':\n      {type(elr_mileages)}, {elr_mileages.shape}")

    elr = 'AAM'
    elr_ = em.fetch_mileage_file(elr)
    elr_mileages = elr_['Mileage']
    print(f"\n    Mileage file for '{elr}':\n      {type(elr_mileages)}, {elr_mileages.shape}")

    elr = 'ABK'
    elr_ = em.fetch_mileage_file(elr)
    elr_mileages = elr_['Mileage']
    print(f"\n    Mileage file for '{elr}':\n      {type(elr_mileages)}, {elr_mileages.shape}")

    problematic_elrs = load_json(cd(test_data_dir, "problematic-ELRs.json"))['ELR']
    i = 0
    while i < len(problematic_elrs):
        print("\n", problematic_elrs[i])
        try:
            elr_ = em.fetch_mileage_file(problematic_elrs[i])
            if elr_ is not None:
                elr_mileages = elr_['Mileage']
                print(f"\n    Mileage file for '{elr}':\n      {type(elr_mileages)}, {elr_mileages.shape}")
            else:
                print(f"\n    Mileage file for '{elr}':\n      {type(elr_)}")
        except AssertionError:
            pass
        i += 1

    update = True

    start_elr, end_elr = 'MAC3', 'DBP1'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'NEM5', 'RSY'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'ECM1', 'WIG'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'NAY', 'NOL'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'NAY', 'LTN2'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'BRA', 'LTN1'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'NOL', 'LTN2'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'NOL', 'NCW'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'WEY', 'FRA'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'CGJ5', 'MVE2'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'MAC3', 'DBP1'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'HDR', 'XTD'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'DCL', 'DPS'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")

    start_elr, end_elr = 'FED', 'LTN1'
    start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
        em.get_conn_mileages(start_elr, end_elr, update=update)
    print(f"\n  Connections between '{start_elr}' and '{end_elr}':")
    print(f"    {(start_elr, start_dest_mileage)}\n"
          f"    {(conn_elr, conn_orig_mileage)}\n"
          f"    {(conn_elr, conn_dest_mileage)}\n"
          f"    {(end_elr, end_orig_mileage)}")
