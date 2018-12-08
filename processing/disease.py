def get_disease(conn, cf, id):
    """mencari penyakit dari database sesuai id gejala maks yang didapat"""
    max_cf = 0
    id_disease = 0
    cursor = conn.cursor()
    
    # --- HANYA UNTUK TUJUAN DEBUG ---
    print("\nHasil Certainty Factor: ")
    for cf_list in list(zip(id, cf)):
        cursor.execute("SELECT * FROM penyakit WHERE id_penyakit = " + str(cf_list[0]))
        disease_name = cursor.fetchall()
        print("ID: ", cf_list[0], " Nama: ", disease_name[0][1], " CF: ", cf_list[1])

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
