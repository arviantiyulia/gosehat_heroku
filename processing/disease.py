
def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_cf = 0.2
    id_disease = 0
    # TODO: Set variabel threshold disini
    cf_list = list(zip(id, cf))
    cursor = conn.cursor()
    id_somedisease = []
    disease_name = []

    cf_new = sorted(cf_list,key=lambda x: x[1], reverse=True)[0:3]
    cf_diurutkan = sorted(cf_list,key=lambda x: x[1], reverse=True)

    # cek apakah melebihi threshold, jika melebihi langsung set max cf (pakai yang bawah)
    # jika tidak ambil 3 item diatas dari array cf_list cari di database

    for i in range(len(cf_new)):
        if cf_new[i][1] > max_cf:
            max_cf = cf_new[i][1]
            id_disease = cf_new[i][0]
        else:
            id_somedisease.append(cf_new[i][0])

    # print("DEBUG> id_disease = ", id_disease)

    # --- AKHIR DARI DEBUG ---
    if id_disease != 0:
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_disease))
        disease_new = cursor.fetchall()
        disease_name = [[i] for i in disease_new]

    else:
        print("INFO> 3 ID tertinggi = ", id_somedisease)
        for id_new in id_somedisease:
            cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_new))
            disease_name.append(cursor.fetchall())


    # --- HANYA UNTUK TUJUAN DEBUG ---
    print("\nINFO> Hasil Certainty Factor: ")
    for item in range(len(cf_diurutkan)):
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(cf_diurutkan[item][0]))
        disease_name2 = cursor.fetchall()
        print("INFO> ID: ", disease_name2[0][0], " Nama: ", disease_name2[0][1], " CF: ", cf_diurutkan[item][1])


    return disease_name, max_cf
