from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.db import create_connection
from processing.symptoms import db_stemming


def get_info(text):
    stopwords = get_stopword('../file/konjungsi.csv')
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

    arr_penyakit = [e[0] for e in penyakit if e]
    # print(arr_penyakit)
    # digunakan untuk inisialisasi variabel baru yang berisi id gejala, count default 0, nama gejala
    for r in arr_penyakit:
        penyakit_new = [r[0], 0, r[1]]
        arr_penyakit.append(penyakit_new)

    arr_penyakit = db_stemming(arr_penyakit)

    print(arr_penyakit)
    # digunakan untuk mencari nama gejala yang memiliki kata paling sedikit
    # for gj in gejala_arr:
    #     count = 0
    #     for nama_gejala in gj[2].split(" "):
    #         if nama_gejala in input:
    #             count += 1;
    #     gj[1] = count
    #
    # print("gj = ", gj)
    # max_ti = max(gejala_arr, key=itemgetter(1))  # mencari id yang memiliki count tertinggi
    # max_count = max_ti[1]

    return sinonim

if __name__ == "__main__":
    text = "apa obat yang cocok untuk demam berdarah dengue ?"
    get_info(text)