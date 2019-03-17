from operator import itemgetter
from processing.preprocessing import stemming


def get_symptoms(conn, inputs):
    """
    fungsi yang digunakan untuk mendapatkan id dari database gejala sesuai input user
    :param conn: koneksi database
    :param inputs: inputan user setelah di sinonim
    :return: list result_id yang berisi kumpulan gejala yang didapat dari database sesuai dengan inputan user
    """

    cursor = conn.cursor()
    rows = []

    # looping untuk mengambil data yang sesuai di database dengan inputan
    for nama_gejala in inputs:
        cursor.execute("SELECT * FROM gejala WHERE nama_gejala LIKE '%" + nama_gejala + "%'")
        rows.append(cursor.fetchall())

    result_id = symptoms_count(rows, inputs)

    # --- HANYA UNTUK TUJUAN DEBUG ---
    rows = []
    for id_gejala in result_id:
        cursor.execute("SELECT * FROM gejala WHERE id_gejala='" + str(id_gejala) + "'")
        rows.append(cursor.fetchall())

    # print("gejala = ", rows[0][1])
    # print("\nDEBUG> Daftar gejala: ")
    # for row in rows:
    #     print("DEBUG> ID: ", row[0][0], " Nama Gejala: ", row[0][1])
    
    # --- AKHIR DARI DEBUG ---

    return rows, result_id

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

    return id_max


def db_stemming(gejala_arr):
    """digunakan untuk melakukan stemming hasil gejala yang didapat dari database"""

    for gj in gejala_arr:
        gejala_split = gj[2].split(" ")
        gejala_stemm = stemming(gejala_split)
        gejala_join = ' '.join(gejala_stemm)
        gj[2] = gejala_join

    return gejala_arr


def exclude_symptoms(symptoms, sinonim):
    
    arr_symptoms = []
    arr_count = []
    arr_count2 = []
    rmv_symp = []
    max_item = 0

    for idx in symptoms:
        arr_symptoms.append([idx[0][1], idx[0][0]])
    
    print("arr_symp = ", arr_symptoms)

    word = "tidak"
    idx_word = sinonim.index(word)
    next_id = idx_word + 1;
    word_val = sinonim[next_id]
    print("word val = ", word_val)
   
    for idx, symp in enumerate(arr_symptoms):
        count = 0
    #     print("symp = ", idx)
        if word_val in symp[0]:
            count += 1
        arr_count.append([symp[1], symp[0], count])
    
    print("count = ", arr_count)
    jml = 0
    for idx_count in arr_count:
        if idx_count[2] == 1:
            jml += 1
    
    # print ("jml = ", jml)
    if jml > 1:
        next_id2 = next_id + 1
        word_val2 = sinonim[next_id2]
        # for arr_count in arr_count:
            # arr_count2 = get_count_exclude(arr_count[1], word_val2)
        for idx, symp in enumerate(arr_count):
            # print("symp = ", symp)
            if word_val2 in symp[1]:
                symp[2] += 1
            arr_count2.append([symp[0], symp[2]])
            max_count = max(arr_count2)

        for idx, gjl in enumerate(arr_count2):
            if gjl[1] > max_item:
                max_item = gjl[1]
                index_max = idx
        rmv_symp = arr_count2.pop(index_max)

        gejala_rmv = [i[0] for i in arr_count2]

    else:
        rmv_symp = arr_count.pop(next_id)

        gejala_rmv = [i[0] for i in arr_count]
    
    print(gejala_rmv)

    return gejala_rmv
