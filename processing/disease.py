import numpy as np

def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_cf = 0.3
    id_disease = 0
    # TODO: Set variabel threshold disini
    # threshold = 0.3
    cf_list = list(zip(id, cf))
    cursor = conn.cursor()
    cf_new = []
    id_somedisease = []

    # TODO: urutkan cf_list dari tinggi ke rendah
    # cf_list.sort(key=lambda tup: tup[1], reverse=True)
    cf_new = sorted(cf_list,key=lambda x: x[1], reverse=True)[0:3]

    # cek apakah melebihi threshold, jika melebihi langsung set max cf (pakai yang bawah)
    # jika tidak ambil 3 item diatas dari array cf_list cari di database

    for i in range(len(cf_new)):
        if cf_new[i][1] > max_cf:
            max_cf = cf_new[i][1]
            id_disease = cf_new[i][0]
            # print("id_disease = ", id_disease)
        else:
            id_somedisease.append(cf_new[i][0])

            # print("id_somedisease = ", id_somedisease)
    # for index in range(len(cf)):
    #     if cf[index] > max_cf:
    #         max_cf = cf[index]
    #         id_disease = id[index]

    # --- HANYA UNTUK TUJUAN DEBUG ---
    print("\nHasil Certainty Factor: ")
    for item in cf_list:
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(item[0]))
        disease_name = cursor.fetchall()
        print("ID: ", item[0], " Nama: ", disease_name[0][1], " CF: ", item[1])

    # --- AKHIR DARI DEBUG ---

    if id_disease is not None:
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_disease))
        disease_name = cursor.fetchall()
        # disease_name = np.array(disease_old)
    if id_somedisease is not None:
        for id_new in id_somedisease:
            cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_new))
            disease_name.append(cursor.fetchall())

    print(disease_name)
    # HANYA UNTUK TUJUAN DEBUG
    # print("\nKemungkinan penyakit yang diderita: " + str(disease_name[0][1]))
    # print("Dengan nilai certainty factor: ", max_cf)

    return disease_name
