from operator import itemgetter
from processing.preprocessing import stemming, filtering, get_stopword
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

    for idx, input in enumerate(inputs):
        if idx in index_word:

            # print("DEBUG> @symptoms.get_symptoms (mencari tidak) sekarang index ke = ", idx)

            if len(inputs) > 1: #untuk mengecek jika yang dimasukkan "tidak" saja
                panjang_list = len(inputs) - 1
                # jika didepan kata tidak sudah tidak ada kata lagi
                # maka skip
                if (idx + 1) > panjang_list:
                    break
                elif inputs[idx + 1] == "sakit":
                    # cek apakah setelah kata 'sakit' masih ada kata
                    # jika masih ada maka lanjutkan perasaan
                    # jika tidak skip
                    # print("DEBUG> @symptoms.get_symptoms BENAR di depan ada kata 'sakit'")
                    if (idx + 2) <= panjang_list:
                        next_id = idx + 2
                    else:
                        continue
                else:
                    next_id = idx + 1
                    # print("DEBUG> @symptoms.get_symptoms SALAH di depan bukan kata 'sakit'")

                join_negation = input + " " + inputs[next_id]
                inputs_new.append(join_negation)

                # print("input new = ", inputs_new)

            else:
                inputs_new.append(input)
        else:
            inputs_new.append(input)

    # print("DEBUG> Input baru @symptoms.get_symptoms =  ", inputs_new)


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

    # print("\nINFO> @symptoms.get_symptoms Daftar gejala: ")
    # for row in rows:
    #     print("INFO> ID: ", row[0][0], " Nama Gejala: ", row[0][1])
    
    # --- AKHIR DARI DEBUG ---
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

    # print("INFO> Max id @symptomps = ", id_max)

    return id_max


def db_stemming(gejala_arr):
    """digunakan untuk melakukan stemming hasil gejala yang didapat dari database"""

    stopwords = get_stopword('file/konjungsi.csv')
    for gj in gejala_arr:
        gejala_split = gj[2].split(" ")
        gejala_filter = filtering(gejala_split, stopwords)
        gejala_stemm = stemming(gejala_filter)
        gejala_join = ' '.join(gejala_stemm)
        gj[2] = gejala_join

    return gejala_arr


def exclude_symptoms(conn, symptoms, sinonim):
    symp_in_db = []
    arr_negation = []
    arr_symp = []
    d = defaultdict(list)
    cursor = conn.cursor()

    word = "tidak"
    index_word = [i for i,d in enumerate(sinonim) if word in d]
    # print("DEBUG> @symptoms.exclude_symptoms index word = ", index_word)
    # print("DEBUG> @symptoms.exclude_symptoms sinonim = ", sinonim)

    for symp in symptoms:
        symp_in_db.append([symp[0][0], symp[0][1], 0])

    for idx in index_word:
        arr_negation.append(sinonim[idx])

    # print("DEBUG> @symptoms.exclude_symptoms arr_negation = ", arr_negation)

    # =========================
    # dibawah adalah proses untuk me-stemming symtom di db dan mereplace
    symp_array_mau_distem = []
    for idx_symp, symp_word in enumerate(symp_in_db):
        temp = []
        for item in symp_word[1].split(' '):
            temp.append(item)

        symp_array_mau_distem.append(temp)

    stemmed_list = []
    for item in symp_array_mau_distem:
        stemmed_list.append(stemming(item))

    # print('@symptoms.exclude_symptoms symp_array_mau_distem = ', symp_array_mau_distem)
    # print('@symptoms.exclude_symptoms stemmed list = ', stemmed_list)

    # join stemming list
    stemmed_list_group = []
    for item in stemmed_list:
        stemmed_list_group.append(' '.join(item))

    # replace di list symp di db
    for idx, symp_word in enumerate(symp_in_db):
        symp_word[1] = stemmed_list_group[idx]

    # print('@symptoms.exclude_symptoms SYMP IN DB STEMMED = ', symp_in_db)

    # akhir dari me-stemming symptom
    # =========================

    for idx, negation_word in enumerate(arr_negation):
        for idx_symp, symp_word in enumerate(symp_in_db):
            if negation_word in symp_word[1]:
                arr_symp.append(symp_word)
                symp_in_db.pop(idx_symp)

    # print("DEBUG> sinonim exclude @symptoms.exclude_symptoms arr_symp = ", arr_symp)
    # print("DEBUG> sinonim exclude @symptoms.exclude_symptoms symp_in_db = ", symp_in_db)

    for idx_word in index_word:
        symp_in_db = remove_symptoms(idx_word, symp_in_db, sinonim)

    symp_in_db.extend(arr_symp)

    # print("DEBUG> sinonim exclude @symptoms.exclude_symptoms symp_in_db new = ", symp_in_db)

    gejala_rmv = [i[0] for i in symp_in_db]
    # print("DEBUG> sinonim exclude @symptoms.exclude_symptoms gejala_rmv = ", gejala_rmv)
    # --- HANYA UNTUK TUJUAN DEBUG ---
    rows = []
    for id_gejala in gejala_rmv:
        cursor.execute("SELECT * FROM gejala WHERE id_gejala='" + str(id_gejala) + "'")
        rows.append(cursor.fetchall())

    print("\nINFO> @symptoms.exclude_symptoms Daftar gejala: ")
    for row in rows:
        print("INFO> ID: ", row[0][0], " Nama Gejala: ", row[0][1])
    
    # --- AKHIR DARI DEBUG ---

    return gejala_rmv


def count_exclude(word, symp_in_db):
    for symp in symp_in_db:
        if word in symp[1]:
            symp[2] += 1

    return symp_in_db

def remove_symptoms(idx_word, symp_in_db, sinonim):

    arr_symp = []
    read_negation = sinonim[idx_word]
    val_negation = read_negation.split()

    # print("DEBUG> @symptoms.remove_symptoms val negation = ", val_negation)
    # print("DEBUG> @symptoms.remove_symptoms idx_word = ", idx_word)
    symp_in_db = count_exclude(val_negation[1], symp_in_db)
    # print("DEBUG> @symptoms.remove_symptoms new simp = ", symp_in_db)

    jml = 0
    for idx_count in symp_in_db:
        if idx_count[2] == 1:
            jml += 1

    # print("DEBUG> @symptoms.remove_symptoms new simp2 = ", symp_in_db)
    # print("DEBUG> @symptoms.remove_symptoms jml = ", jml)

    if jml > 1: #jika "tidak" terdapat pada lebih dari 1 gejala
        # jika kata setelah 'tidak ____' = sakit
        if sinonim[idx_word + 1] == "sakit":
            next_id2 = idx_word + 2
        # jika kata setelah 'tidak ____' bukan sakit
        else:
            next_id2 = idx_word + 3

        val_negation = sinonim[next_id2]

        for i in symp_in_db:
            if i[2] == 1:
                arr_symp.append(i)

        arr_symp = count_exclude(val_negation, arr_symp)

        check_value = all(map(lambda x: x[2], arr_symp))

        if check_value == True:
            max_symp = min(arr_symp, key=lambda xs: len(xs[1]))
        else:
            max_symp = max(arr_symp, key=lambda x: x[2])
    else:
        max_symp = max(symp_in_db, key=lambda x: x[2])

    rmv_symp = symp_in_db.remove(max_symp)

    return symp_in_db
