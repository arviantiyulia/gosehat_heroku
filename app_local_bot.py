import datetime as dt
import sys

from informasi import get_info
from processing.app import get_cf
from processing.cek_input import inputs_check
from processing.db import create_connection
from processing.greeting import check_greeting
from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.save_input import (flat, save_history, save_input,
                                   save_menuinformasi, save_menukonsultasi, delete_menukonsultasi)
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

def message_bot(user_id, name_user, salam, text, conn):
    msg_penyakit = "Kemungkinan Anda terkena penyakit "
    msg_pengobatan = "\n\n#Pengobatan \nPertolongan pertama yang bisa dilakukan adalah "
    msg_pencegahan = "\n#Pencegahan \nPencegahan yang bisa dilakukan adalah "
    msg_komplikasi = "\n#Komplikasi \nKomplikasi yang terjadi jika penyakit tidak segera ditangani yaitu "
    msg_peringatan = "Silahkan menghubungi dokter untuk mendapatkan informasi dan penanganan yang lebih baik"

    message = ""
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    kondisi_gejala = inputs_check(conn, sinonim)

    cursor = conn.cursor()

    # jika gejala kosong maka tampilkan pesan
    # TODO: mending hapus aja gejala yang sebelumnya di db biar fresh
    if kondisi_gejala == "kosong":
        disease = check_greeting(sinonim)
        message = message + str(disease)

    # jika gejalanya kurang
    elif kondisi_gejala == "kurang":

        # TODO: masukin gejala ke database, panggil fungsi bantuan
        save_input(user_id, name_user, sinonim, conn)

        cursor.execute("SELECT COUNT (*) FROM gejala_input WHERE user_id = '" + user_id + "'")
        count_input = cursor.fetchall()

        if count_input[0][0] <= 3:
            message = message + "Gejala yang anda masukkan kurang akurat.\nApakah ada gejala lain ?"
            save_history(user_id, name_user, text, message, conn)

        else:
            cursor.execute("SELECT nama_gejala FROM gejala_input WHERE user_id = '" + user_id + "'")
            gejala_db = cursor.fetchall()
            gejala = [i[0] for i in gejala_db]
            result, cf = get_cf(conn, gejala)
            # print("result = ", result)

            # jika yang terdeteksi hanya 1 penyakit
            if len(result) == 1:
                for output in result:
                    message = message + salam + name_user + "\n" \
                              + msg_penyakit + output[0][1] + "\n" + output[0][2] \
                              + msg_pengobatan + output[0][4] + "\n" \
                              + msg_pencegahan + output[0][5] + "\n" \
                              + msg_komplikasi + str(output[0][6]) \
                              + "\n\n" + msg_peringatan

                output_sistem = msg_penyakit + result[0][0][1]
                save_history(user_id, name_user, text, output_sistem, conn)

            # jika yang terdeteksi lebih dari 1 penyakit
            else:
                # print("hasil = ", result)
                message = message + salam + name_user + "\n" \
                          + msg_penyakit + result[0][0][1] + " , " + result[1][0][1] + " , " + result[2][0][1] \
                          + "\n\n" + result[0][0][2] + "\n\n" + result[1][0][2] + "\n\n" + result[2][0][2] \
                          + "\n\n" + msg_peringatan

                output_sistem = msg_penyakit + result[0][0][1] + " , " + result[1][0][1] + " , " + result[2][0][1]
                save_history(user_id, name_user, text, output_sistem, conn)

            cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
            conn.commit()

    # TODO: sebelum di lakukan hitung cf tambahkan gejala yang disimpan di db ke kata yang akan di proses
    # setelah sukses hapus yang ada di db
    elif kondisi_gejala == "ada":
        cursor.execute("SELECT nama_gejala FROM gejala_input WHERE user_id = '" + user_id + "'")
        gejala_db = cursor.fetchall()

        if gejala_db is None:
            result, cf = get_cf(conn, sinonim)

        else:
            gejala_new = [i[0] for i in gejala_db]
            sinonim.append(gejala_new)
            gejala_new2 = flat(sinonim)
            result, cf = get_cf(conn, gejala_new2)

            cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
            conn.commit()

        # jika yang terdeteksi hanya 1 penyakit
        if len(result) == 1:
            for output in result:
                message = message + salam + name_user + "\n" \
                          + msg_penyakit + output[0][1] + "\n" + output[0][2] \
                          + msg_pengobatan + output[0][4] + "\n" \
                          + msg_pencegahan + output[0][5] + "\n" \
                          + msg_komplikasi + str(output[0][6]) \
                          + "\n\n" + msg_peringatan

            output_sistem = msg_penyakit + result[0][0][1]
            save_history(user_id, name_user, text, output_sistem, conn)

        # jika yang terdeteksi lebih dari 1 penyakit
        else:
            # print("hasil = ", result)
            message = message + salam + name_user + "\n" \
                      + msg_penyakit + result[0][0][1] + " , " + result[1][0][1] + " , " + result[2][0][1] \
                      + "\n\n" + result[0][0][2] + "\n\n" + result[1][0][2] + "\n\n" + result[2][0][
                          2] + "\n\n" + msg_peringatan

            output_sistem = msg_penyakit + result[0][0][1] + " , " + result[1][0][1] + " , " + result[2][0][1]
            save_history(user_id, name_user, text, output_sistem, conn)

    return message

def decide_process(text):
    print("\nDEBUG> ------------ DECIDE PROCESS --------------")
    # PROSES
    stopwords = get_stopword('file/konjungsi_info.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)

    stopword_info_list = ["apa", "mengapa", "bagaimana", "obat", "sebab", "solusi", "gejala", "komplikasi", "cegah"]
    stop_list = [word for word in stopword_info_list if word in sinonim]

    for stop in stop_list:
        sinonim.remove(stop)
    if "sakit" in sinonim:
        sinonim.remove("sakit")

    print("DEBUG> sinonim baru = ", sinonim)
    print("DEBUG> stop_list = ", stop_list)

    if len(stop_list) != 0 :
        daftar_gejala = get_symptoms(conn, sinonim)
        print("DEBUG> daftar gejala", daftar_gejala)

        daftar_penyakit = []
        for i in sinonim:
            cursor.execute("SELECT id_penyakit, nama_penyakit FROM penyakit WHERE nama_penyakit LIKE '%" + i + "%'")
            daftar_penyakit.append(cursor.fetchall())

        daftar_penyakit = [e for e in daftar_penyakit if e]  # list of tuple to list and not empty
        print("DEBUG> daftar penyakit", daftar_penyakit)
        
        print("DEBUG> ------------ END DECIDE PROCESS --------------\n")

        if len(stop_list) == 1:
            if stop_list[0] == "gejala":
                return "konsultasi"
            if stop_list[0] == "bagaimana":
                return "konsultasi"
            if stop_list[0] == "apa":
                # jika tidak ada gejala = informasi
                if not daftar_gejala:
                    return "informasi"
                # jika ada penyakit = informasi
                elif len(daftar_penyakit) != 0:
                    return "informasi"
                # selain itu
                else:
                    return "konsultasi"
            else:
                return "informasi"
                
        elif len(stop_list) > 1:
            if "apa" in stop_list:
                if "gejala" in stop_list:
                    # jika ada keyword APA dan GEJALA tapi tidak ada daftar gejala = informasi
                    if not daftar_gejala:
                        return "informasi"
                    # jika ada keyword APA dan GEJALA tapi tidak ada daftar gejala = informasi
                    if len(daftar_gejala) > 3:
                        return "konsultasi"
                    # jika ada keyword APA dan GEJALA tapi ada daftar penyakit
                    elif len(daftar_penyakit) != 0:
                        return "informasi"
                    else:
                        return "konsultasi"
                else:
                    return "informasi"    
            else:
                return "informasi"
        else:
            return "informasi"


""" untuk kegunaan tes line bot, contoh python app_local_bot.py <argumen input user>"""
if __name__ == "__main__":

    # dapatkan argumen cmd, contoh: python app_local_bot.py "saya merasa mual muntah"
    args = sys.argv
    if len(args) == 1:
        # text = "saya mual, muntah, bintik merah pada kulit, nyeri untuk melirik"
        text = "demam tinggi,kelelahan,mata berair,sensitif terhadap cahaya"
    else:
        text = args[1]

    conn = create_connection()
    cursor = conn.cursor()

    user_id = "1"
    name_user = "admin"

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
            messages_info = get_info(text)
            messages = salam + name_user + "\n" + messages_info[0][0]
            print(messages)
            delete_menukonsultasi(user_id, conn)
            exit(0)
        elif count_menu[0][0] == '\konsultasi':
            messages = message_bot(user_id, name_user, salam, text, conn)
            print(messages)
            delete_menukonsultasi(user_id, conn)
            exit(0)
    else:
        decision = decide_process(text)
        if decision == "informasi":
            messages_info = get_info(text)
            messages = salam + name_user + "\n" + messages_info[0][0]
            print(messages)
            exit(0)
        else:
            messages = message_bot(user_id, name_user, salam, text, conn)
            print(messages)
            exit(0)
        delete_menukonsultasi(user_id, conn)
