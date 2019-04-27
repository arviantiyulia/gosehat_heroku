from operator import itemgetter
from processing.preprocessing import stemming
from collections import defaultdict


def get_symptoms(conn, inputs):
    """
    fungsi yang digunakan untuk mendapatkan id dari database gejala sesuai input user
    :param conn: koneksi database
    :param inputs: inputan user setelah di sinonim
    :return: list result_id yang berisi kumpulan gejala yang didapat dari database sesuai dengan inputan user
    """

    cursor = conn.cursor()
    rows = []
    inputs_new = []

    d = defaultdict(list)

    word = "tidak"
    index_word = [i for i, d in enumerate(inputs) if d == word]

    # print("index = ", index_word)
    # for idx_tidak in index_word:
    #     cek_next_index = index_word + 1

    # print("index = ", cek_next_index)

    for idx, input in enumerate(inputs):
        if idx in index_word:

            print("DEBUG> @symptoms.get_symptoms (mencari tidak) sekarang index ke = ", idx)
            # cek_next_index = idx + 1
            print("index = ", len(inputs) - 1)
            if len(inputs) > 1:
                if inputs[idx + 1] == "sakit":
                    next_id = idx + 2
                    print("DEBUG> @symptoms.get_symptoms BENAR di depan ada kata 'sakit'")
                else:
                    next_id = idx + 1
                    print("DEBUG> @symptoms.get_symptoms SALAH di depan bukan kata 'sakit'")

                join_negation = input + " " + inputs[next_id]
                inputs_new.append(join_negation)

                print("input new = ", inputs_new)

            else:
                inputs_new.append(input)
        else:
            inputs_new.append(input)

    print("DEBUG> Input baru @symptoms.get_symptoms =  ", inputs_new)


    # looping untuk mengambil data yang sesuai di database dengan inputan
    for nama_gejala in inputs_new:
        cursor.execute("SELECT * FROM gejala WHERE nama_gejala LIKE '%" + nama_gejala + "%'")
        rows.append(cursor.fetchall())

    result_id = symptoms_count(rows, inputs_new)

    # --- HANYA UNTUK TUJUAN DEBUG ---
    rows = []
    for id_gejala in result_id:
        cursor.execute("SELECT * FROM gejala WHERE id_gejala='" + str(id_gejala) + "'")
        rows.append(cursor.fetchall())

    # print("gejala = ", rows[0][1])
    print("\nINFO> @symptoms.get_symptoms Daftar gejala: ")
    for row in rows:
        print("INFO> ID: ", row[0][0], " Nama Gejala: ", row[0][1])
    
    # --- AKHIR DARI DEBUG ---
    # print("rows = ", result_id)
    return rows, result_id, inputs_new

def symptoms_count(rows, inputs):
    """
    fungsi ini digunakan untuk menghitung banyaknya input gejala sesuai dengan database gejala
    :param rows: list yang berisi gejala sesuai input user
    :param inputs: inputan user hasil dari sinonim
    :return: list id_gejala berdasarkan inputan user
    """

    arr_id = []

    # looping untuk menyimpan data yang lebih dari 2 gejala
    for row in rows:
        if len(row) > 1:
            id_new = get_max_id(inputs, row)
            arr_id.append(id_new)

        elif len(row) == 1:
            temp_gejala2 = row[0][0]
            arr_id.append(temp_gejala2)


    id_gejala = list(set(arr_id))

    return id_gejala


def get_max_id(input, row):
    """mendapatkan id yang tertinggi dari gejala inputan user"""

    gejala_arr = []
    temp_max_count = []
    min_item = 1000
    id_min_count = 0

    # digunakan untuk inisialisasi variabel baru yang berisi id gejala, count default 0, nama gejala
    for r in row:
        gejala_new = [r[0], 0, r[1]]
        gejala_arr.append(gejala_new)

    gejala_arr = db_stemming(gejala_arr)

    # digunakan untuk mencari nama gejala yang memiliki kata paling sedikit
    for gj in gejala_arr:
        count = 0
        for nama_gejala in gj[2].split(" "):
            if nama_gejala in input:
                count += 1;
        gj[1] = count

    max_ti = max(gejala_arr, key=itemgetter(1))  # mencari id yang memiliki count tertinggi
    max_count = max_ti[1]

    # mencari data yang memiliki count tertinggi dengan max_count
    for sort in gejala_arr:
        if sort[1] == max_count:
            temp_max_count.append(sort)

    # looping digunakan untuk mencari gejala yang jumlah katanya paling sedikit
    for len_count in range(len(temp_max_count)):
        if len(temp_max_count[len_count][2].split()) < min_item:
            min_item = len(temp_max_count[len_count][2].split())
            id_min_count = temp_max_count[len_count][0]

    id_max = id_min_count

    print("INFO> Max id @symptomps = ", id_max)

    return id_max


def db_stemming(gejala_arr):
    """digunakan untuk melakukan stemming hasil gejala yang didapat dari database"""

    for gj in gejala_arr:
        gejala_split = gj[2].split(" ")
        gejala_stemm = stemming(gejala_split)
        gejala_join = ' '.join(gejala_stemm)
        gj[2] = gejala_join

    return gejala_arr


def exclude_symptoms(conn, symptoms, sinonim):
    new_symp = []
    arr_negation = []
    arr_symp = []
    d = defaultdict(list)
    cursor = conn.cursor()

    word = "tidak"
    index_word = [i for i,d in enumerate(sinonim) if word in d]
    print("DEBUG> @symptoms.exclude_symptoms index word = ", index_word)
    print("DEBUG> @symptoms.exclude_symptoms sinonim = ", sinonim)

    
    for symp in symptoms:
        new_symp.append([symp[0][0], symp[0][1], 0])

    print("DEBUG> sinonim exclude @symptoms.exclude_symptoms = ", sinonim)

    for idx in index_word:
        arr_negation.append(sinonim[idx])

    for idx, neg in enumerate(arr_negation):
        for idx_symp, symp in enumerate(new_symp):
            # print("negation = ", neg, "symp = ", symp[1])
            if neg in symp[1]:
                # print("neg = ", neg, "id = ", idx)
                arr_symp.append(symp)
                # arr_negation.pop(idx)
                index_word.pop(idx)
                new_symp.pop(idx_symp)

    print("DEBUG> sinonim exclude @symptoms.exclude_symptoms new_symp = ", new_symp)
    # print("arr_negation = ", arr_negation)
    # print("index word = ", index_word)

    for idx_word in index_word:
        new_symp = remove_symptoms(idx_word, new_symp, sinonim)
        # new_symp = symptoms_rmv

    new_symp.extend(arr_symp)

    # print("new simp setalh negasi dihapus = ", new_symp)
    # print("symptoms_rmv = ", symptoms_rmv)

    gejala_rmv = [i[0] for i in new_symp]

    # --- HANYA UNTUK TUJUAN DEBUG ---
    rows = []
    for id_gejala in gejala_rmv:
        cursor.execute("SELECT * FROM gejala WHERE id_gejala='" + str(id_gejala) + "'")
        rows.append(cursor.fetchall())

    # print("gejala = ", rows[0][1])
    print("\nINFO> @symptoms.exclude_symptoms Daftar gejala: ")
    for row in rows:
        print("INFO> ID: ", row[0][0], " Nama Gejala: ", row[0][1])
    
    # --- AKHIR DARI DEBUG ---

    # print("gjl_rmv = ", gejala_rmv)

    return gejala_rmv


def count_exclude(next_id, new_symp):
    
    # word_val = sinonim[next_id]
    # print("next_id = ", next_id)
    for symp in new_symp:
        # print("new_simp2 = ", symp[1])
        count = 0
        if next_id in symp[1]:
            symp[2] += 1

    # print("new symp2 = ", new_symp)
    return new_symp

def remove_symptoms(idx_word, new_symp, sinonim):

    arr_symp = []
    # next_id = idx_word + 1;
    read_negation = sinonim[idx_word]
    val_negation = read_negation.split()
    # print("next id = ", idx_word)

    print("DEBUG> @symptoms.remove_symptoms new simp = ", new_symp)
    new_symp = count_exclude(val_negation[1], new_symp)

    jml = 0
    for idx_count in new_symp:
        if idx_count[2] == 1:
            jml += 1

    print("DEBUG> @symptoms.remove_symptoms new simp2 = ", new_symp)
    print("DEBUG> @symptoms.remove_symptoms jml = ", jml)

    if jml > 1:
        if sinonim[idx_word + 1] == "sakit":
            next_id2 = idx_word + 2
        else:
            next_id2 = idx_word + 3

        val_negation = sinonim[next_id2]

        for i in new_symp:
            if i[2] == 1:
                arr_symp.append(i)

        arr_symp = count_exclude(val_negation, arr_symp)
        # print("arr_symp  = ", arr_symp)
        check_value = all(map(lambda x: x[2], arr_symp))

        if check_value == True:
            max_symp = min(arr_symp, key=lambda xs: len(xs[1]))
        else:
            max_symp = max(arr_symp, key=lambda x: x[2])
        # print("max symp = ", max_symp)
    else:
        max_symp = max(new_symp, key=lambda x: x[2])

        # print("max symp = ", max_symp)
    rmv_symp = new_symp.remove(max_symp)

    return new_symp
