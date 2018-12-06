def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_item = 0
    id_disease = 0
    cursor = conn.cursor()

    # print("id perhitungan cf = ", id)
    # print("hasil perhitungan cf = ", cf)
    
    # debug only
    print("hasil CF: ")
    for cf_list in list(zip(id, cf)):
        # print(cf_list)
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(cf_list[0]))
        disease_name = cursor.fetchall()
        # print('disease = ', disease_name[0][0])
        print("ID: ", cf_list[0], " Nama: ", disease_name[0][1], " CF: ", cf_list[1])

    for index in range(len(cf)):
        if cf[index] > max_item:
            max_item = cf[index]
            id_disease = id[index]

    cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_disease))
    disease_name = cursor.fetchall()

    print("penyakit: " + str(disease_name[0][0]))

    return disease_name
