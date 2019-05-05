from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.sinonim import get_sinonim
from processing.save_input import flat
import csv

texts = []

def get_input():
    with open('file/input_user.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile, delimiter=';')
        for r in read_data:
            texts.append(r)

    # text = flat(texts)
    return texts


if __name__ == "__main__":
    texts = get_input()
    join_contents = []
    join_filters = []
    join_stems = []
    join_sinonim = []


    stopwords = get_stopword('file/konjungsi_info.csv')

    for text in texts:
        print("\nInput user:", text)

        contents = tokenizing(text[1])
        filters = filtering(contents, stopwords)
        stems = stemming(filters)
        sinonim = get_sinonim(stems)

        join_contents.append('; '.join(contents))
        join_filters.append('; '.join(filters))
        join_stems.append('; '.join(stems))
        join_sinonim.append('; '.join(sinonim))

        # print("\nHasil Contents:", join_contents)
        # print("Hasil Filter:", join_filters)
        # print("Hasil Stemming:", join_stems)
        # print("Hasil Sinonim:", join_sinonim)
        # print("--------------------------------------------------------------------------------")

    print("\nMenyimpan hasil...")
    newfilepath = 'testing_textmining.csv'
    with open(newfilepath, 'w', encoding="ISO-8859-1", newline='') as f:
        fieldname = ['user', 'text', 'tokenizing', 'filtering', 'stemming', 'sinonim']
        writer = csv.DictWriter(f, delimiter=",", fieldnames=fieldname)

        writer.writeheader()
        for index, value in enumerate(texts):
            print('*', end='')
            writer.writerow({'user': texts[index][0], 'text': texts[index][1], 'tokenizing': join_contents[index], 'filtering': join_filters[index], 'stemming': join_stems[index], 'sinonim': join_sinonim[index]})