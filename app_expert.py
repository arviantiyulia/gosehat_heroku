import datetime as dt
import sys
import time as tm
from collections import defaultdict
import operator

from informasi import get_info
from processing.app import get_cf
from processing.cek_input import cek_total_gejala, cek_total_penyakit
from processing.db import create_connection
from processing.greeting import check_greeting
from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.save_input import (delete_menukonsultasi, flat, save_history,
                                   save_input, save_menuinformasi,
                                   save_menukonsultasi)
from processing.sinonim import get_sinonim
from processing.symptoms import get_symptoms

""" untuk kegunaan tes line bot, contoh python app_local_bot.py <argumen input user>"""
if __name__ == "__main__":

    # dapatkan argumen cmd, contoh: python app_local_bot.py "saya merasa mual muntah"
    args = sys.argv
    if len(args) == 1:
        # text = "saya mual, muntah, bintik merah pada kulit, nyeri untuk melirik"
        # text = "demam tinggi,mata tidak merah, batuk darah, mata berair, tidak bisa tidur, kepala tidak sakit, sensitif terhadap cahaya"
        # text  = "Saya merasa mual dan kepala serasa berputar, saya sakit apa?"
        text = "mag"
    else:
        text = args[1]

    conn = create_connection()
    cursor = conn.cursor()

    stopwords = get_stopword('file/konjungsi_info.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    
    # dapatkan gejala
    # gejalas = []
    # for sin in sinonim:
    #     cursor.execute("SELECT * FROM gejala WHERE nama_gejala LIKE '%" + sin + "%'")
    #     gejalas = [[r[0], r[1]]  for r in cursor.fetchall()]

    # print(gejalas)

    # daftar_penyakits = []
    # for gejala in gejalas:
    #     print(gejala)

    symp_db, symptoms, symptoms_name = get_symptoms(conn, sinonim)
    print("DAFTAR ID GEJALA")
    print(symptoms)

    diseases = []
    for symptom in symptoms:
        cursor.execute("SELECT * FROM gejala_penyakit WHERE id_gejala = '" + str(symptom) + "'")
        diseases.append([[r[0], r[1], r[2], r[3]]  for r in cursor.fetchall()])

    print("DAFTAR ID PENYAKIT")
    semua_penyakit = []
    for index in range(len(symptoms)):
        print(symptoms_name[index])
        penyakit_di_gejala = [d[1] for d in diseases[index]]
        init_penyakit_di_gejala = [1 for d in diseases[index]]
        print(penyakit_di_gejala)
        semua_penyakit = semua_penyakit + penyakit_di_gejala
        # print(dict(zip(penyakit_di_gejala, init_penyakit_di_gejala)))
        # dict_penyakit.append(dict(zip(penyakit_di_gejala, init_penyakit_di_gejala)))
    
    print('\nSEMUA PENYAKIT')
    print(semua_penyakit)

    dict_penyakit = {}
    dict_penyakit_total = {}

    for penyakit in semua_penyakit:
        dict_penyakit[penyakit] = 0

    for penyakit in semua_penyakit:
        dict_penyakit_total[penyakit] = 0

    for penyakit in semua_penyakit:
        dict_penyakit[penyakit] = dict_penyakit[penyakit] + 1
    
    print("DICT PENYAKIT")
    print(dict_penyakit)
    print(dict_penyakit_total)

    for key, val in dict_penyakit.items():
        # jumlah = 0
        cursor.execute("SELECT COUNT(*) FROM gejala_penyakit WHERE id_penyakit = '" + str(key) + "'")
        jumlah = cursor.fetchall()[0][0]

        dict_penyakit_total[key] = val/jumlah

        
    
    print("DICT FROM DATABASE")
    print(sorted(dict_penyakit_total.items(), key=operator.itemgetter(1)))

    # print(dict_penyakit_total)
    # print(diseases)
    # print([d[1] for d in diseases])

    

