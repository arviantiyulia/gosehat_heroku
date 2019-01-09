import itertools
import math

from processing.app import get_cf
from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
import csv

conn = create_connection()
cursor = conn.cursor()
gejala = []

def get_gejala():
    cursor.execute("SELECT * FROM gejala")
    gejala = cursor.fetchall()

    return gejala

def flat(listoflist):
    for item in listoflist:
        if type(item) != list:
            gejala.append(item)
        else:
            for num in item:
                gejala.append(num)
    return gejala


def get_gejalapenyakit():

    jumlah_gejala = []
    hitung_gejala = []
    sisa_gejala = []

    cursor.execute("SELECT id_penyakit FROM penyakit")
    penyakit = cursor.fetchall()

    cursor.execute("SELECT id_gejala FROM gejala")
    gejala = cursor.fetchall()
    gejala = [item[0] for item in gejala]
    gejala = tuple(gejala)



    # idx = 0
    #
    # for i in penyakit:
    #     cursor.execute("SELECT COUNT(*) FROM gejala_penyakit WHERE id_penyakit = " + str(i[0]))
    #     jumlah = cursor.fetchall()
    #     jumlah_gejala.append(jumlah[0][0])
    #
    # for x in jumlah_gejala:
    #     hitung = math.floor((x*60)/100)
    #     hitung_gejala.append(hitung)
    #
    # print("hitung gejala = ",hitung_gejala)
    #
    # for y in penyakit:
    cursor.execute("SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(1))
    id_gejala = cursor.fetchall()

    name_gejala = [item[0].split(" ") for item in id_gejala]
    gj = flat(name_gejala)

    print("name gejala = ", gj)
    stopwords = get_stopword('file/konjungsi.csv')
    filters = filtering(gj, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    result = get_cf(conn, sinonim)
    #
    #     with open('testing.csv', 'a') as csvFile:
    #         writer = csv.writer(csvFile)
    #         writer.writerow(result)
    #
    # csvFile.close()

    #
    #     comb = itertools.combinations(id_gejala, hitung_gejala[idx])
    #     comb_gejala = []
    #     all_gejala = []
    #
    #     for x in comb:
    #         comb_gejala.append(x)
    #
    #     # print(gejala)
    #
    #     # allgejala = [text for text in gejala if text not in comb_gejala[0]]
    #     for comb in comb_gejala:
    #         all_gejala.append(tuple(set(comb) ^ set(gejala)))
    #
    #     # print("comb all gejala = ", all_gejala)
    #     # print("comb gejala = ", comb_gejala)
    #
    #     sisa_gejala.append(jumlah_gejala[idx] - hitung_gejala[idx])
    #     # print("sisa gejala = ", sisa_gejala)
    #
    #     comb_all = itertools.combinations(all_gejala, sisa_gejala[idx])
    #     comb_allgejala = []
    #     for x in comb_all:
    #         comb_allgejala.append(x)
    #
    #     print("comb_allgejala = ",comb_allgejala)
    #
    #
    #     idx+=1





    return

if __name__ == "__main__":
    get_gejala()
    get_gejalapenyakit()