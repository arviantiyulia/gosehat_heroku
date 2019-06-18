from processing.db import create_connection
from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.symptoms import get_symptoms, exclude_symptoms
from processing.disease_symptoms import get_id_disease
from processing.certaintyfactor import certainty_calculate
from processing.disease import get_disease
from processing.greeting import check_greeting
import time


def get_cf(conn, sinonim):
    start_time = time.time()
    symp_db, symptoms, input = get_symptoms(conn, sinonim)
    ex_symptoms = exclude_symptoms(conn, symp_db, input)
    count_disease_id, uniq_id = get_id_disease(conn, ex_symptoms)
    cf_calculate = certainty_calculate(count_disease_id)
    disease = get_disease(conn, cf_calculate, uniq_id)

    end_time = time.time() - start_time

    print("waktu = ", end_time)

    return disease
