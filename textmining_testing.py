from processing.preprocessing import (filtering, get_stopword, stemming,
                                      tokenizing)
from processing.sinonim import get_sinonim
from processing.save_input import flat
import csv

input = []

def get_input():
    with open('file/input_user.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile)
        for r in read_data:
            input.append(r)

    text = flat(input)
    print(text)
    return text


if __name__ == "__main__":
    input = get_input()
    join_contents = []
    join_filters = []
    join_stems = []
    join_sinonim = []


    stopwords = get_stopword('file/konjungsi_info.csv')

    for text in input:
        contents = tokenizing(text)
        filters = filtering(contents, stopwords)
        stems = stemming(filters)
        sinonim = get_sinonim(stems)

        join_contents.append(', '.join(contents))
        join_filters.append(', '.join(filters))
        join_stems.append(', '.join(stems))
        join_sinonim.append(', '.join(sinonim))

        print(join_contents)

    newfilepath = 'testing_textmining.csv'
    with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
        fieldname = ['tokenizing', 'filtering', 'stemming', 'sinonim']
        writer = csv.DictWriter(f, delimiter=";", fieldnames=fieldname)

        writer.writeheader()
        for idx, inp in enumerate(input):
            print(idx)
            writer.writerow({'tokenizing': join_contents[idx], 'filtering': join_filters[idx], 'stemming': join_stems[idx], 'sinonim': join_sinonim[idx]})