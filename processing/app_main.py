from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.symptoms import get_symptoms
from processing.disease_symptoms import get_id_disease
from processing.certaintyfactor import certainty_calculate
from processing.disease import get_disease


def get_cf(text):
    conn = create_connection()
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)
    symptoms = get_symptoms(conn, sinonim)
    count_disease_id, uniq_id = get_id_disease(conn, symptoms)
    cf_calculate = certainty_calculate(count_disease_id)
    disease = get_disease(conn, cf_calculate, uniq_id)

    return disease[0][0]


if __name__ == "__main__":
    get_cf("saya batuk darah, demam, flu dan pusing, lidah putih")
