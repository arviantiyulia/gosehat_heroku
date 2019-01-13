from operator import itemgetter
from collections import Counter

from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.symptoms import db_stemming


def get_info(text):
    stopwords = get_stopword('file/konjungsi_info.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    conn = create_connection()
    cursor = conn.cursor()

    penyakit = []

    for i in sinonim:
        cursor.execute("SELECT id_penyakit, nama_penyakit FROM penyakit WHERE nama_penyakit LIKE '%" + i + "%'")
        penyakit.append(cursor.fetchall())

    arr_penyakit = [e for e in penyakit if e]  # list of tuple to list and not empty

    # print("arr_penyakit = ", arr_penyakit)

    if len(arr_penyakit) != 0:
        penyakit_max = penyakit_count(arr_penyakit, sinonim)
        result = get_keywoard(sinonim, penyakit_max, conn)
    else:
        result = "Nama penyakit tidak dicantumkan. Silahkan menyertakan nama penyakit dan informasi yang ingin diketahui"

    # print(result[0][0])
    return result


def penyakit_count(arr_penyakit, sinonim):
    arr_id = []

    for row in arr_penyakit:
        if len(row) > 1:
            id_new = get_maxpenyakit(sinonim, row)
            arr_id.append(id_new)

        elif len(row) == 1:
            temp_penyakit = row[0][0]
            arr_id.append(temp_penyakit)

    count_id = Counter(arr_id)
    id_penyakit = max(count_id)
    print("arr_id = ", max(count_id))

    return id_penyakit


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
                count += 1;
        gj[1] = count

    max_ti = max(stem_penyakit, key=itemgetter(1))  # mencari id yang memiliki count tertinggi

    return max_ti[0]


def get_keywoard(input, result, conn):
    cursor = conn.cursor()

    hasil = []

    gejala = get_gejala(cursor, result)

    if "apa" in input:
        if "obat" in input or "solusi" in input:
            cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "sebab" in input:
            cursor.execute("SELECT penyebab_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "gejala" in input:
            hasil = gejala

        elif "komplikasi" in input:
            cursor.execute("SELECT komplikasi_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "cegah" in input:
            cursor.execute("SELECT pencegahan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        else:
            cursor.execute("SELECT definisi_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

    elif "mengapa" in input or "kenapa" in input:
        cursor.execute("SELECT penyebab_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
        hasil = cursor.fetchall()

    elif "bagaimana" in input:
        if "obat" in input or "solusi" in input:
            cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "cegah" in input:
            cursor.execute("SELECT pencegahan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()
        else:
            cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()
    else:
        if "obat" in input or "solusi" in input:
            cursor.execute("SELECT pengobatan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "sebab" in input:
            cursor.execute("SELECT penyebab_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "gejala" in input:
            hasil = gejala

        elif "komplikasi" in input:
            cursor.execute("SELECT komplikasi_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        elif "cegah" in input:
            cursor.execute("SELECT pencegahan_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

        else:
            cursor.execute("SELECT definisi_penyakit FROM penyakit WHERE id_penyakit = '" + str(result) + "'")
            hasil = cursor.fetchall()

    print(hasil)
    return hasil

def get_gejala(cursor, result):
    id_gejala = []
    gejala = []

    cursor.execute(
        "SELECT gejala_penyakit.id_gejala FROM penyakit JOIN gejala_penyakit ON gejala_penyakit.id_penyakit = penyakit.id_penyakit WHERE penyakit.id_penyakit = '" + str(
            result) + "'")
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
