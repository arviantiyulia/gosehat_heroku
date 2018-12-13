from processing.app import get_cf
from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.cek_input import inputs_check
from processing.greeting import check_greeting

""" untuk kegunaan tes preprocessing => python app_test.py"""
if __name__ == "__main__":
    # text = "saya muntah,sakit kepala, bintik merah pada kulit"
    text = "saya muntah"
    conn = create_connection()
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    kondisi_gejala = inputs_check(conn, sinonim)

    # jika gejala kosong maka tampilkan pesan
    if kondisi_gejala == "kosong":
        disease = check_greeting(sinonim)
        print(disease)
    elif kondisi_gejala == "kurang":
        print("Gejala yang anda masukkan kurang! Woy!")
    elif kondisi_gejala == "ada":
        get_cf(conn, sinonim)

