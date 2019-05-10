import copy
from collections import Counter
from operator import itemgetter

from processing.db import create_connection
from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.sinonim import get_sinonim
from processing.symptoms import db_stemming
from processing.greeting import check_greeting


def get_info(text):
    stopwords = get_stopword('file/konjungsi_info.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    conn = create_connection()
    cursor = conn.cursor()


    penyakit = []

    sinonim_untuk_gejala = copy.deepcopy(sinonim)

    # remove
    stopword_info_list = ["apa", "mengapa", "bagaimana", "obat", "sebab", "solusi", "gejala", "komplikasi", "cegah"]
    stop_list = [word for word in stopword_info_list if word in sinonim_untuk_gejala]

    for stop in stop_list:
        sinonim_untuk_gejala.remove(stop)
    if "sakit" in sinonim_untuk_gejala:
        sinonim_untuk_gejala.remove("sakit")

    

    for i in sinonim_untuk_gejala:
        cursor.execute("SELECT id_penyakit, nama_penyakit FROM penyakit WHERE nama_penyakit LIKE '%" + i + "%'")
        penyakit.append(cursor.fetchall())


    arr_penyakit = [e for e in penyakit if e]  # list of tuple to list and not empty

    # if len(arr_penyakit) == 0:
    #     messages = check_greeting(sinonim)

    #     return sinonim, arr_penyakit, messages

    print("DEBUG> arr_penyakit = ", arr_penyakit)
    if len(arr_penyakit) != 0:
        penyakit_max = penyakit_count(arr_penyakit, sinonim)
        result = get_keywoard(sinonim, penyakit_max, conn)
    else:
        result = [[("Nama penyakit tidak dicantumkan. Silahkan menyertakan nama penyakit dan informasi yang ingin diketahui",)]]

    return sinonim, arr_penyakit, result


# jelaskan fungsinya
# TODO nama fungsi gak cocok sama maksudnya
def penyakit_count(arr_penyakit, sinonim):
    arr_id = []

    for row in arr_penyakit:
        # jika memiliki 2 penyakit, cari yang paling cocok
        if len(row) > 1:
            id_new = get_maxpenyakit(sinonim, row)
            arr_id.append(id_new)

        # jika cuma 1 masukkan aja
        elif len(row) == 1:
            temp_penyakit = row[0][0]
            arr_id.append(temp_penyakit)

    count_id = Counter(arr_id)
    for key, value in count_id.items():
        if value > 1:
            id_penyakit = max(count_id)
            return [id_penyakit]

    # ketika semua counternya 1
    return arr_id

# TODO tolong dijelaskan ini maksudnya apa fungsinya
def get_maxpenyakit(sinonim, arr_penyakit):
    arr_penyakitnew = []

    # digunakan untuk inisialisasi variabel baru yang berisi id gejala, count default 0, nama gejala
    for r in arr_penyakit:
        penyakit_new = [r[0], 0, r[1]]
        arr_penyakitnew.append(penyakit_new)

    stem_penyakit = db_stemming(arr_penyakitnew)

    # digunakan untuk mencari nama gejala yang memiliki kata paling sedikit
    for gj in stem_penyakit:
        count = 0
        for nama_gejala in gj[2].split(" "):
            if nama_gejala in sinonim:
                count += 1
        gj[1] = count
    max_ti = max(stem_penyakit, key=itemgetter(1))  # mencari id yang memiliki count tertinggi

    return max_ti[0]


# maksud fungsinya apa?
def get_keywoard(input, result, conn):
    cursor = conn.cursor()

    hasil = []

    gejala = get_gejala(cursor, result)

    print("DEBUG> input Informasi = ", input)
    print("DEBUG> gejala Informasi = ", gejala)

    if "apa" in input:
        if "obat" in input or "solusi" in input:
            for res in result:
                cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "sebab" in input:
            for res in result:
                cursor.execute("SELECT penyebab_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "gejala" in input:
            hasil = gejala

        elif "komplikasi" in input:
            for res in result:
                cursor.execute("SELECT komplikasi_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "cegah" in input:
            for res in result:
                cursor.execute("SELECT pencegahan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        else:
            for res in result:
                cursor.execute("SELECT definisi_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

    elif "mengapa" in input or "kenapa" in input:
        for res in result:
            cursor.execute("SELECT penyebab_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
            hasil.append(cursor.fetchall())

    elif "bagaimana" in input:
        if "obat" in input or "solusi" in input:
            for res in result:
                cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "cegah" in input:
            for res in result:
                cursor.execute("SELECT pencegahan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())
        else:
            for res in result:
                cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())
    else:
        if "obat" in input or "solusi" in input:
            for res in result:
                cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "sebab" in input:
            for res in result:
                cursor.execute("SELECT penyebab_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "gejala" in input:
            hasil = gejala

        elif "komplikasi" in input:
            for res in result:
                cursor.execute("SELECT komplikasi_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        elif "cegah" in input:
            for res in result:
                cursor.execute("SELECT pencegahan_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

        else:
            for res in result:
                cursor.execute("SELECT definisi_penyakit FROM penyakit WHERE id_penyakit = '" + str(res) + "'")
                hasil.append(cursor.fetchall())

    print("DEBUG> hasil informasi = ", hasil)
    return hasil

def get_gejala(cursor, result):
    id_gejala = []
    gejala = []

    for res in result:
        cursor.execute("SELECT gejala_penyakit.id_gejala FROM penyakit JOIN gejala_penyakit ON gejala_penyakit.id_penyakit = penyakit.id_penyakit WHERE penyakit.id_penyakit = '" + str(res) + "'")
        id_gejala.append(cursor.fetchall())

    arr_gejala = [e for e in id_gejala if e]

    for x in arr_gejala[0]:
        id = int(''.join(map(str, x)))
        cursor.execute(
            "SELECT nama_gejala FROM gejala WHERE id_gejala = '" + str(id) + "'")
        gejala.append(cursor.fetchall())

    list_gj = [i[0] for i in gejala]

    list_gj2 = [i[0] for i in list_gj]
    list_gejala = ",".join(map("".join, list_gj2))
    gj_list = [list_gejala]

    hasil_gejala = [tuple(s for s in gj_list)]

    return hasil_gejala

if __name__ == "__main__":
    text = "infeksi saluran nafas aku penyakit apa ya ?"
    get_info(text)
