def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_cf = 0
    id_disease = 0
    # TODO: Set variabel threshold disini
    cf_list = list(zip(id, cf))
    cursor = conn.cursor()
    
    # --- HANYA UNTUK TUJUAN DEBUG ---
    print("\nHasil Certainty Factor: ")
    for item in cf_list:
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(item[0]))
        disease_name = cursor.fetchall()
        print("ID: ", item[0], " Nama: ", disease_name[0][1], " CF: ", item[1])

    # TODO: urutkan cf_list dari tinggi ke rendah
    # cek apakah melebihi threshold, jika melebihi langsung set max cf (pakai yang bawah)
    # jika tidak ambil 3 item diatas dari array cf_list cari di database

    for index in range(len(cf)):
        if cf[index] > max_cf:
            max_cf = cf[index]
            id_disease = id[index]

    # --- AKHIR DARI DEBUG ---

    cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(id_disease))
    disease_name = cursor.fetchall()

    # HANYA UNTUK TUJUAN DEBUG
    print("\nKemungkinan penyakit yang diderita: " + str(disease_name[0][1]))
    print("Dengan nilai certainty factor: ", max_cf)

    return disease_name
