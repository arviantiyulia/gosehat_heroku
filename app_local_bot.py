import datetime as dt
import sys
import time as tm

from informasi import get_info
from processing.app import get_cf
from processing.cek_input import cek_total_gejala, cek_total_penyakit
from processing.db import create_connection
from processing.greeting import check_greeting
from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.save_input import (delete_menukonsultasi, flat, hapus_kata_sakit, save_history,
                                   save_input, save_menuinformasi,
                                   save_menukonsultasi)
from processing.sinonim import get_sinonim
from processing.symptoms import get_symptoms

gejala = []

def flat(listoflist):
    for item in listoflist:
        if type(item) != list:
            gejala.append(item)
        else:
            for num in item:
                gejala.append(num)
    return gejala


def message_bot(user_id, name_user, salam, text, time, conn):
    msg_penyakit = "Kemungkinan Anda terkena penyakit "
    msg_pengobatan = "\n\n#Pengobatan \nPertolongan pertama yang bisa dilakukan adalah "
    msg_pencegahan = "\n#Pencegahan \nPencegahan yang bisa dilakukan adalah "
    msg_komplikasi = "\n#Komplikasi \nKomplikasi yang terjadi jika penyakit tidak segera ditangani yaitu "
    msg_peringatan = "Silahkan menghubungi dokter untuk mendapatkan informasi dan penanganan yang lebih baik"

    message = ""
    timestamp = tm.time()
    cursor = conn.cursor()
    penyakit_result = ""
    definisi_result = ""
    disease = ""


    if text.lower() == 'tidak':
        kondisi_gejala = 'ada'
        sinonim = []
    else:
        stopwords = get_stopword('file/konjungsi.csv')
        print(text)
        contents = tokenizing(text)
        filters = filtering(contents, stopwords)
        print("filtering = ", filters)
        stems = stemming(filters)
        sinonim = get_sinonim(stems)
        hapus_kata_sakit(sinonim)
        
        if len(sinonim) <= 2 :
            gabung_sinonim = ' '.join(sinonim)

            if gabung_sinonim == 'selamat pagi' or gabung_sinonim == 'selamat malam' or gabung_sinonim == 'pagi' or gabung_sinonim == 'malam':
                greeting = check_greeting(sinonim)
                disease_id = 0
                save_history(user_id, name_user, text, greeting, "", disease_id, time, conn)
                return greeting

        symp_db, symptoms, input = get_symptoms(conn, sinonim)
        kondisi_gejala = cek_total_gejala(symp_db)
        jml_penyakit, penyakit = cek_total_penyakit(conn, sinonim)

        cursor.execute("SELECT DISTINCT input_user, time FROM gejala_input WHERE user_id = '" + user_id + "'")
        get_time = cursor.fetchall()

        if get_time:
            timestamp_now = tm.time() - float(get_time[0][1])

            if timestamp_now >= 3600:
                cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
                conn.commit()
                print("hapus gejala expired")


    # jika gejala kosong maka tampilkan pesan
    if kondisi_gejala == "kosong":
        print("INFO> gejala kosong")
        print("DEBUG> jumlah penyakit = ", jml_penyakit)
        if jml_penyakit == 0:
            disease = check_greeting(sinonim)
        elif jml_penyakit > 0:
            for pnykt in penyakit:
                disease = disease + pnykt[0][2] + "\n\n"
        message = message + str(disease)

    # jika gejalanya kurang
    elif kondisi_gejala == "kurang":
        print("INFO> gejala kurang")

        print("timestamp = ", timestamp)
        input_to_sinonim = ",".join(input)
        print("DEBUG> Sinonim disimpan ke tabel (gejala input) = ", input_to_sinonim)
        save_input(user_id, name_user, symp_db, input_to_sinonim, timestamp, conn)

        cursor.execute("SELECT COUNT (*) FROM gejala_input WHERE user_id = '" + user_id + "'")
        count_input = cursor.fetchall()

        if count_input[0][0] <= 3:
            message = message + "Gejala yang anda masukkan kurang akurat.\nApakah ada gejala lain ?"
            disease_id = 0
            save_history(user_id, name_user, text, message, "", disease_id, time, conn)

        else:
            cursor.execute("SELECT DISTINCT input_user FROM gejala_input WHERE user_id = '" + user_id + "'")
            gejala_db = cursor.fetchall()
            print("DEBUG> Kurang | Gejala di DB = ", gejala_db)
            gejala = [i[0].split(',') for i in gejala_db]
            gejala_flat = flat(gejala)
            print("DEBUG> Kurang | Gejala yang digabung = ", gejala_flat)
            result, cf = get_cf(conn, gejala_flat)

            # jika yang terdeteksi hanya 1 penyakit
            if len(result) == 1:
                # print("hasil = ", result)
                for output in result:
                    message = message + salam + name_user + "\n" \
                              + msg_penyakit + output[0][1] + "\n" + output[0][2] \
                              + msg_pengobatan + output[0][4] + "\n" \
                              + msg_pencegahan + output[0][5] + "\n" \
                              + msg_komplikasi + str(output[0][6]) \
                              + "\n\n" + msg_peringatan

                output_sistem = msg_penyakit + result[0][0][1]
                disease_id = result[0][0][0]
                save_history(user_id, name_user, text, output_sistem, "", disease_id, time, conn)

            # jika yang terdeteksi lebih dari 1 penyakit
            else:
                for idx in result:
                    penyakit_result = penyakit_result + " , " +  idx[0][1]
                    definisi_result = definisi_result + "\n\n" + idx[0][2]

                message = message + salam + name_user + "\n" + msg_penyakit + penyakit_result + "\n" + definisi_result + "\n\n" + msg_peringatan
                output_sistem = msg_penyakit + penyakit_result

                for dis in result:
                    disease_id = dis[0][0]
                    save_history(user_id, name_user, text, output_sistem, "", disease_id, time, conn)


            cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
            conn.commit()

    # setelah sukses hapus yang ada di db
    elif kondisi_gejala == "ada":
        print("INFO> gejala cukup")
        cursor.execute("SELECT DISTINCT input_user FROM gejala_input WHERE user_id = '" + user_id + "'")
        gejala_db = cursor.fetchall()

        print("DEBUG> Cukup | Gejala di DB = ", gejala_db)

        if not gejala_db:
            print("sinonim app = ", sinonim)
            if len(sinonim) == 0:
                disease = check_greeting(sinonim)
                message = message + str(disease)
                return message

            else:
                print("gejala benar")
                result, cf = get_cf(conn, sinonim)
                # untuk mendapatkan daftar string gejala
                print("\n----------proses dibawah ini untuk daftar gejala yang disimpan ke histroy------------")
                symp_db, symptoms, input = get_symptoms(conn, sinonim)
                string_gejala = ', '.join([symp[0][1] for symp in symp_db])
                print("\n-------------------------selesai-------------------------")

        else:
            gejala = [i[0].split(',') for i in gejala_db]
            gejala_flat = flat(gejala)
            print("DEBUG> Cukup | Gejala yang digabung = ", gejala_flat)
            gejala_new2 = sinonim + gejala_flat
            print("DEBUG> Cukup | Gejala yang digabung + kalimat sebelum = ", gejala_new2)

            # untuk mendapatkan daftar string gejala
            print("\n----------proses dibawah ini untuk daftar gejala yang disimpan ke histroy------------")
            symp_db, symptoms, input = get_symptoms(conn, gejala_new2)
            string_gejala = ', '.join([symp[0][1] for symp in symp_db])
            print("-------------------------selesai-------------------------\n")

            if len(symp_db) <= 1:
                disease_id = 0
                output_sistem = "Maaf data kurang akurat. Sistem tidak bisa memberikan diagnosa.\nSilahkan masukkan keluhan Anda kembali."
                save_history(user_id, name_user, text, output_sistem, string_gejala, disease_id, time, conn)
                cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
                conn.commit()
                return salam + name_user + "\n" + output_sistem
            else:
                result, cf = get_cf(conn, gejala_new2)


            cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
            conn.commit()

        # jika yang terdeteksi hanya 1 penyakit
        if len(result) == 1:
            # print("hasil = ", result)
            for output in result:
                message = message + salam + name_user + "\n" \
                          + msg_penyakit + output[0][1] + "\n" + output[0][2] \
                          + msg_pengobatan + output[0][4] + "\n" \
                          + msg_pencegahan + output[0][5] + "\n" \
                          + (str(output[0][6]) + "\n\n" if output[0][6] is not None else '') \
                          + msg_peringatan

            output_sistem = msg_penyakit + result[0][0][1]
            disease_id = result[0][0][0]
            save_history(user_id, name_user, text, output_sistem, string_gejala, disease_id, time, conn)

        # jika yang terdeteksi lebih dari 1 penyakit
        else:
            for idx in result:
                penyakit_result = penyakit_result + " , " + idx[0][1]
                definisi_result = definisi_result + "\n\n" + idx[0][2]

            message = message + salam + name_user + "\n" + msg_penyakit + penyakit_result + "\n" + definisi_result + "\n\n" + msg_peringatan
            output_sistem = msg_penyakit + penyakit_result

            for dis in result:
                disease_id = dis[0][0]
                save_history(user_id, name_user, text, output_sistem, string_gejala, disease_id, time, conn)
    return message

def decide_process(text):
    print("\nDEBUG> ------------ DECIDE PROCESS --------------")
    # PROSES
    stopwords = get_stopword('file/konjungsi_info.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)

    stopword_info_list = ["apa", "kenapa", "mengapa", "bagaimana", "obat", "sebab", "solusi", "gejala", "komplikasi", "cegah"]
    stop_list = [word for word in stopword_info_list if word in sinonim]

    for stop in stop_list:
        sinonim.remove(stop)
    if "sakit" in sinonim:
        sinonim.remove("sakit")
    if "demam" in sinonim:
        sinonim.remove("demam")

    print("DEBUG> sinonim baru = ", sinonim)
    print("DEBUG> stop_list = ", stop_list)

    daftar_gejala, id_gejala, nama_gejala = get_symptoms(conn, sinonim)
    print("DEBUG> daftar gejala", daftar_gejala)
    print("DEBUG> panjang gejala : ", len(daftar_gejala))

    daftar_penyakit = []
    for i in sinonim:
        cursor.execute("SELECT id_penyakit, nama_penyakit FROM penyakit WHERE nama_penyakit LIKE '%" + i + "%'")
        daftar_penyakit.append(cursor.fetchall())

    daftar_penyakit = [e for e in daftar_penyakit if e]  # list of tuple to list and not empty
    print("DEBUG> daftar penyakit", daftar_penyakit)

    if len(stop_list) != 0 :

        print("DEBUG> ------------ END DECIDE PROCESS --------------\n")

        if len(stop_list) >= 1:
            if len(daftar_penyakit) == 0 and len(daftar_gejala) < 2:
                return "informasi"
            elif len(daftar_penyakit) > 0 and len(daftar_gejala) < 2:
                return "informasi"
            else:
                return "konsultasi"
        else:
            return "informasi"

    else:
        if len(sinonim) == 1 and "tidak" in sinonim:
            return "konsultasi"
        elif len(daftar_penyakit) == 0 and len(daftar_gejala) < 2:
            return "konsultasi"
        elif len(daftar_penyakit) > 0 and len(daftar_gejala) < 2:
            return "informasi"
        else:
            return "konsultasi"


""" untuk kegunaan tes line bot, contoh python app_local_bot.py <argumen input user>"""
if __name__ == "__main__":

    # dapatkan argumen cmd, contoh: python app_local_bot.py "saya merasa mual muntah"
    args = sys.argv
    if len(args) == 1:
        text = "mag"
    else:
        text = args[1]

    conn = create_connection()
    cursor = conn.cursor()

    user_id = "1"
    name_user = "admin"
    time = dt.datetime.now()
    print("time = ", time)

    # salam
    if dt.datetime.now() < dt.datetime.now().replace(hour=12, minute=0, second=0) and dt.datetime.now() > dt.datetime.now().replace(hour=0, minute=0, second=0):
            salam = "Selamat Pagi "
    elif dt.datetime.now() > dt.datetime.now().replace(hour=12, minute=0, second=0) and dt.datetime.now() < dt.datetime.now().replace(hour=18, minute=0, second=0):
        salam = "Selamat Siang "
    elif dt.datetime.now() > dt.datetime.now().replace(hour=18, minute=0, second=0):
        salam = "Selamat Malam "
    else:
        salam = "Assalamualaikum "

    # MENU
    if text == '\informasi':
        messages = "masukkan informasi"
        save_menuinformasi(user_id, name_user, text, conn)
        print(messages)
        exit(0)

    elif text == '\konsultasi':
        save_menukonsultasi(user_id, name_user, text, conn)
        messages = "masukkan konsultasi"
        print(messages)
        exit(0)
    else:
        cursor.execute("SELECT status FROM menu WHERE id_user = '" + user_id + "'")
        count_menu = cursor.fetchall()

    print("DEBUG> count menu = ", count_menu)

    if len(count_menu) != 0:
        if count_menu[0][0] == '\informasi':
            penyakit, messages_info = get_info(text)
            messages = salam + name_user + "\n" + messages_info[0][0]
            print(messages)
            delete_menukonsultasi(user_id, conn)
            exit(0)
        elif count_menu[0][0] == '\konsultasi':
            messages = message_bot(user_id, name_user, salam, text, time, conn)
            print(messages)
            delete_menukonsultasi(user_id, conn)
            exit(0)
    else:
        decision = decide_process(text)
        print("DEBUG> pilihan = ", decision)
        if decision == "informasi":
            print("INFO> masuk informasi")
            disease_id = 0
            sinonim, penyakit, messages_info = get_info(text)
            if len(penyakit) == 0 and len(sinonim) <= 2:
                messages = check_greeting(sinonim)
                save_history(user_id, name_user, text, messages, "", disease_id, time, conn)
            else:
                messages = salam + name_user
                for msg in messages_info:
                    messages = messages + "\n" + msg[0][0]
                save_history(user_id, name_user, text, messages, "", disease_id, time, conn)
            print(messages)
            exit(0)
        else:
            print("INFO> masuk konsultasi")
            messages = message_bot(user_id, name_user, salam, text, time, conn)
            print(messages)
            exit(0)
        delete_menukonsultasi(user_id, conn)
