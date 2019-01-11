from processing.preprocessing import get_stopword, tokenizing, filtering, stemming
from processing.sinonim import get_sinonim
from processing.db import create_connection


def get_info(text):
    stopwords = get_stopword('file/konjungsi.csv')
    contents = tokenizing(text)
    filters = filtering(contents, stopwords)
    stems = stemming(filters)
    sinonim = get_sinonim(stems)

    return sinonim