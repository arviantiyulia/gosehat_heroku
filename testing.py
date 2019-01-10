import csv
import itertools
from processing.app import get_cf
from processing.db import create_connection
from processing.preprocessing import get_stopword, filtering, stemming
from processing.sinonim import get_sinonim
from collections import Counter

conn = create_connection()
cursor = conn.cursor()
gejala = []


def get_gejala():
    cursor.execute("SELECT * FROM gejala")
    gejala = cursor.fetchall()

    return gejala


def flat(listoflist):
    for item in listoflist:
        if type(item) != list:
            gejala.append(item)
        else:
            for num in item:
                gejala.append(num)
    return gejala


def get_penyakit():
    cursor.execute("SELECT id_penyakit FROM penyakit")
    penyakit = cursor.fetchall()

    return penyakit


def get_gejalapenyakit(penyakit):
    id_gejala = []

    for y in penyakit:
        cursor.execute(
            "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(
                y[0]))
        id_gejala.append(cursor.fetchall())

    for i in id_gejala:
        name_gejala = [item[0].split(" ") for item in i]
        print("old = ", name_gejala)
        gj = [element for sub in name_gejala for element in sub]
        print("gj = ", gj)

        # print("name gejala = ", i)
        list_gj = ",".join(map("-".join, i))
        list = [list_gj]
        print("list_gj = ", list)

        stopwords = get_stopword('file/konjungsi.csv')
        filters = filtering(gj, stopwords)
        stems = stemming(filters)
        sinonim = get_sinonim(stems)
        result = get_cf(conn, sinonim)

        data = [result[0][0][1]]
        print("data = ", data)
        rows = [list, data]
        newfilepath = 'testing.csv'

        with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

    return rows


def combination_samegejala(penyakit):
    arr_penyakit = []

    comb_penyakit = itertools.combinations(penyakit, 2)
    for cb in comb_penyakit:
        tuple_comb = [element for tupl in cb for element in tupl]  # convert tuple of tuple to list
        arr_penyakit.append(tuple_comb)
        # print("arr = ", arr_penyakit)

    for i in range(50):
        list_gj = []
        arr_gejala = []

        for j in arr_penyakit[i]:
            cursor.execute(
                "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(
                    j))
            id_gejala = cursor.fetchall()

            list_gj.append([i[0] for i in id_gejala])  # convert list of tuple to list

        for x in range(len(list_gj[0])):
            for y in range(len(list_gj[1])):
                if list_gj[0][x] == list_gj[1][y]:
                    arr_gejala.append(list_gj[0][x])

        if len(arr_gejala) >= 3:
            # print(gj)
            name_gejala = [item.split(" ") for item in arr_gejala]
            # print("old = ", arr_gejala)
            gj = [element for sub in name_gejala for element in sub]
            # print("gj = ", gj)

            stopwords = get_stopword('file/konjungsi.csv')
            filters = filtering(gj, stopwords)
            stems = stemming(filters)
            sinonim = get_sinonim(stems)
            result = get_cf(conn, sinonim)

            list_gj = ",".join(map("".join, arr_gejala))
            list = [list_gj]

            print("result = ", list)
            data = [result[0][0][1]]
            print("data = ", data)
            rows = [list, data]
            newfilepath = 'testing.csv'

            with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
                writer = csv.writer(f)
                for row in rows:
                    writer.writerow(row)

    return rows

def combination_other(penyakit):
    arr_penyakit = []

    comb_penyakit = itertools.combinations(penyakit, 2)
    for cb in comb_penyakit:
        tuple_comb = [element for tupl in cb for element in tupl]  # convert tuple of tuple to list
        arr_penyakit.append(tuple_comb)

    for i in range(50):
        list_gj = []
        arr_gejala = []

        for j in arr_penyakit[i]:
            cursor.execute(
                "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(
                    j))
            id_gejala = cursor.fetchall()

            list_gj.append([i[0] for i in id_gejala])  # convert list of tuple to list

        # compare list 1 dan list 2
        for x in range(len(list_gj[0])):
            for y in range(len(list_gj[1])):
                if list_gj[0][x] == list_gj[1][y]:
                    arr_gejala.append(list_gj[0][x])

        if len(arr_gejala) >= 3:
            print("arr_gejala = ", arr_gejala)

            list_othergj = []

            for y in arr_penyakit[i]:
                cursor.execute(
                    "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(y))
                other_gejala = cursor.fetchall()

                list_othergj.append([i[0] for i in other_gejala])

            for gj in list_othergj:
                arr_gejalanew = []
                arr_othergejala = [text for text in gj if text not in arr_gejala]
                comb_othergejala = itertools.combinations(arr_othergejala, 2)

                for cg in comb_othergejala:
                    # arr_gejala
                    list_comb = list(cg)
                    for ag in arr_gejala:
                        list_comb.append(ag)

                    split_gj = [item.split(" ") for item in list_comb]
                    arr_gj = [element for sub in split_gj for element in sub]
                    # print(arr_gj)

                    stopwords = get_stopword('file/konjungsi.csv')
                    filters = filtering(gj, stopwords)
                    stems = stemming(filters)
                    sinonim = get_sinonim(stems)
                    result = get_cf(conn, sinonim)

                    join_gj = ",".join(map("".join, list_comb))
                    list_gj = [join_gj]

                    print("result = ", list_gj)
                    data = [result[0][0][1]]
                    print("data = ", data)
                    rows = [list_gj, data]
                    newfilepath = 'testing.csv'

                    with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
                        writer = csv.writer(f)
                        for row in rows:
                            writer.writerow(row)

    return arr_gejala


if __name__ == "__main__":
    get_gejala()
    penyakit = get_penyakit()
    # get_gejalapenyakit(penyakit)
    # combination_samegejala(penyakit)
    combination_other(penyakit)
