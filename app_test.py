from processing.app import get_cf
from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.cek_input import inputs_check
from processing.greeting import check_greeting

""" untuk kegunaan tes preprocessing => python app_test.py"""
if __name__ == "__main__":
    text = "hallo"
    conn = create_connection()
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    gejala_list = inputs_check(conn, sinonim)

    # jika gejala kosong maka tampilkan pesan
    if gejala_list == "kosong":
        disease = check_greeting(sinonim)
        # print(disease)
        return disease
    elif gejala_list == "ada":
        get_cf(text)

    # get_cf("saya rasa asam di mulut, berkeringat dingin, muntah, sakit kepala, mudah merasa kenyang")
