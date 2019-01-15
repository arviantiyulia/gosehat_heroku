
def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_cf = 0
    id_disease = 0
    # TODO: Set variabel threshold disini
    cf_list = list(zip(id, cf))
    cursor = conn.cursor()
    cf_new = []
    id_somedisease = []
    disease_name = []

    # TODO: urutkan cf_list dari tinggi ke rendah
    # cf_list.sort(key=lambda tup: tup[1], reverse=True)
    cf_new = sorted(cf_list,key=lambda x: x[1], reverse=True)[0:3]

    # cek apakah melebihi threshold, jika melebihi langsung set max cf (pakai yang bawah)
    # jika tidak ambil 3 item diatas dari array cf_list cari di database

    for i in range(len(cf_new)):
        if cf_new[i][1] >= max_cf:
            max_cf = cf_new[i][1]
            id_disease = cf_new[i][0]
            # print("id_disease = ", id_disease)
        else:
            id_somedisease.append(cf_new[i][0])

    # print("id_somedisease = ", id_somedisease)
    print("id_disease = ", id_disease)
    # for index in range(len(cf)):
    #     if cf[index] > max_cf:
    #         max_cf = cf[index]
    #         id_disease = id[index]

    # --- AKHIR DARI DEBUG ---
    if id_disease != 0:
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_disease))
        disease_new = cursor.fetchall()
        disease_name = [[i] for i in disease_new]
        # print("\nKemungkinan penyakit yang diderita: " + str(disease_name))
        # print("Dengan nilai certainty factor: ", max_cf)

    else:
        print("3 id tertinggi = ", id_somedisease)
        for id_new in id_somedisease:
            cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_new))
            disease_name.append(cursor.fetchall())


    # --- HANYA UNTUK TUJUAN DEBUG ---
    print("\nHasil Certainty Factor: ")
    for item in range(len(cf_list)):
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(cf_list[item][0]))
        disease_name2 = cursor.fetchall()
        print("ID: ", item, " Nama: ", disease_name2[0][1], " CF: ", cf_list[item][1])
    # print("cf_list = ", cf_list[0][)

    # print(disease_name)
    # print(disease_name[0][0][1])
    # HANYA UNTUK TUJUAN DEBUG
    print("\nKemungkinan penyakit yang diderita: " + str(disease_name[0][0][1]))
    print("Dengan nilai certainty factor: ", max_cf)

    return disease_name, max_cf
