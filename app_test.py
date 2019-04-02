from processing.app import get_cf
from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.cek_input import inputs_check
from processing.greeting import check_greeting
from processing.save_input import save_input
from processing.negation import remove_negation

gejala = []

def flat(listoflist):
    for item in listoflist:
        if type(item) != list:
            gejala.append(item)
        else:
            for num in item:
                gejala.append(num)
    return gejala

""" untuk kegunaan tes preprocessing => python app_test.py"""
if __name__ == "__main__":
    # text = "saya mual, muntah, bintik merah pada kulit, nyeri untuk melirik"
    text = "mual, muntah, nyeri otot, bintik merah di kulit, demam tinggi, tidak pusing"

    user_id = "1"
    name_user = "admin"

    conn = create_connection()
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    # negation = remove_negation(stems)
    sinonim = get_sinonim(stems)
    print(sinonim)
    kondisi_gejala = inputs_check(conn, sinonim)

    gejala_db = []
    cursor = conn.cursor()

    # jika gejala kosong maka tampilkan pesan
    if kondisi_gejala == "kosong":
        disease = check_greeting(sinonim)
        print(disease)
    elif kondisi_gejala == "kurang":
        input_db = save_input(user_id, name_user, sinonim, conn)

        cursor.execute("SELECT COUNT (*) FROM gejala_input WHERE user_id = '" + user_id + "'")
        count_input = cursor.fetchall()

        if count_input[0][0] <= 3:
            print("Gejala yang anda masukkan kurang, silahkan tambahkan lagi")
        else:
            cursor.execute("SELECT nama_gejala FROM gejala_input WHERE user_id = '" + user_id + "'")
            gejala_db = cursor.fetchall()
            gejala_new = [i[0] for i in gejala_db]
            get_cf(conn, gejala_new)

    elif kondisi_gejala == "ada":
        cursor.execute("SELECT nama_gejala FROM gejala_input WHERE user_id = '" + user_id + "'")
        gejala_db = cursor.fetchall()

        if gejala_db is None:
            get_cf(conn, sinonim)
        else:
            gejala_new = [i[0] for i in gejala_db]
            sinonim.append(gejala_new)
            gejala_new2 = flat(sinonim)
            get_cf(conn, gejala_new2)

    cursor.execute("DELETE FROM gejala_input WHERE user_id = '" + user_id + "'")
    conn.commit()






