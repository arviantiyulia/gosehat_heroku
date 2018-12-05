from itertools import groupby

def get_id_disease(conn, symptoms):
    """fungsi yang digunakan untuk mendapatkan id penyakit sesuai gejala"""

    cursor = conn.cursor()
    gejala_penyekit_selected, uniquekeys = get_gejala_penyakit_selected(symptoms, cursor)
    penyakit_list = get_penyakit_list(symptoms, cursor)
    all_gejala_penyakit_list = get_all_gejala_penyakit(penyakit_list, cursor)
    normalized_data = normalize_weight(gejala_penyekit_selected, all_gejala_penyakit_list)

    return normalized_data, uniquekeys

def get_penyakit_list(symptoms, cursor):
    """ fungsi yang digunakan untuk mendapat semua daftar penyakit berdasarkan gejala yang dimasukkan pengguna"""

    rows = []
    id_penyakit_list = []

    for symp in symptoms:
        cursor.execute(
            "SELECT id_penyakit FROM gejala_penyakit WHERE id_gejala = " + str(symp)
        )
        rows.append(cursor.fetchall())

    for row in rows:
        for item in row:
            id_penyakit_list.append(item[0])

    # get only unique id
    id_penyakit_list = list(set(id_penyakit_list))
    
    return id_penyakit_list


def get_gejala_penyakit_selected(symptoms, cursor):
    """ fungsi yang digunakan untuk mendapatkan daftar gejala dari penyakit berdasarkan gejala yang dimasukkan pengguna"""

    rows = []
    item_list = []
    id_gejala_penyakit = []
    uniquekeys = []

    # looping untuk mengambil data yang sesuai di database gejala_penyakit dengan id gejala
    for symp in symptoms:
        cursor.execute(
            "SELECT id_penyakit, bobot FROM gejala_penyakit WHERE id_gejala = " + str(symp)
            )
        rows.append(cursor.fetchall())

    # looping untuk menyimpan id penyakit berdasarkan gejala
    for row in rows:
        for item in row:
            item_list.append(item)

    item_list.sort(key=lambda tup: tup[0])

    #looping yang digunakan untuk mengelompokkan id yang sama dalam satu list
    for k, g in groupby(item_list, key=lambda tup: tup[0]):
        id_gejala_penyakit.append(list(g))
        uniquekeys.append(k)

    return id_gejala_penyakit, uniquekeys


def get_all_gejala_penyakit(penyakit_list, cursor):
    """ fungsi yang digunakan untuk mendapatkan semua daftar gejala dari penyakit berdasarkan daftar penyakit yang dipilih"""

    rows = []
    items = []
    gejala_penyakit_list = []

    for penyakit in penyakit_list:
        cursor.execute(
            "SELECT id_penyakit, bobot FROM gejala_penyakit WHERE id_penyakit = " + str(penyakit)
        )
        rows.append(cursor.fetchall())

    for row in rows:
        for item in row:
            items.append(item)

    items.sort(key=lambda tup: tup[0])

    #looping yang digunakan untuk mengelompokkan id yang sama dalam satu list
    for k, g in groupby(items, key=lambda tup: tup[0]):
        gejala_penyakit_list.append(list(g))

    return gejala_penyakit_list


def get_sum_of_weight(data):
    """ fungsi yang digunakan untuk medapatkan total dari bobot gejala dari tiap penyakit """
    total = sum([d[1] for d in data])
    return total


def normalize_weight(gejala_selected, all_gejala_penyakit):
    """ fungsi yang digunakan untuk menormalisasi bobot dari gejala tiap penyakit """
    result = []
    normalized_data = []
    for i in range(len(gejala_selected)):
        for j in range(len(gejala_selected[i])):
            sum_of_weight = get_sum_of_weight(all_gejala_penyakit[i])
            norm = gejala_selected[i][j][1] / sum_of_weight
            result.append((gejala_selected[i][j][0], norm))
    
    #looping yang digunakan untuk mengelompokkan id yang sama dalam satu list
    for k, g in groupby(result, key=lambda tup: tup[0]):
        normalized_data.append(list(g))

    # print("normalized data: ", normalized_data)
    return normalized_data
