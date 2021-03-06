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

    print("id gejala = ",id_gejala)
    for i in id_gejala:
        name_gejala = [item[0].split(" ") for item in i]
        # print("old = ", name_gejala)
        gj = [element for sub in name_gejala for element in sub]
        # print("gj = ", gj)

        # print("name gejala = ", i)
        list_gj = ",".join(map("-".join, i))
        list = [list_gj]
        # print("list_gj = ", list)

        stopwords = get_stopword('file/konjungsi.csv')
        filters = filtering(gj, stopwords)
        stems = stemming(filters)
        sinonim = get_sinonim(stems)
        result, cf = get_cf(conn, sinonim)

        # print("result = ", cf)
        data = [result[0][0][1]]
        # print("data = ", data)
        nilai_cf = [cf]
        zips = zip(list, data, nilai_cf)
        newfilepath = 'testing all new.csv'

        with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
            writer = csv.writer(f, delimiter=";")
            for row in zips:
                tmp = row
                writer.writerow(tmp)

    return zips


def combination_samegejala(penyakit):
    arr_penyakit = []

    comb_penyakit = itertools.combinations(penyakit, 2)
    for cb in comb_penyakit:
        tuple_comb = [element for tupl in cb for element in tupl]  # convert tuple of tuple to list
        arr_penyakit.append(tuple_comb)
    print("kumpulan penyakit = ", arr_penyakit)

    for i in range(len(arr_penyakit)):
        list_gj = []
        arr_gejala = []
        
        

        print("penyakit = ", arr_penyakit[i])
        for j in arr_penyakit[i]:
            cursor.execute(
                "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(
                    j))
            id_gejala = cursor.fetchall()

            list_gj.append([i[0] for i in id_gejala])  # convert list of tuple to list

        print("gejala = ", list_gj)
        for x in range(len(list_gj[0])):
            for y in range(len(list_gj[1])):
                if list_gj[0][x] == list_gj[1][y]:
                    arr_gejala.append(list_gj[0][x])


        if len(arr_gejala) >= 2:
            # baru tambahkan id penyakit
            new_list_penyakit = []
            list_penyakit = []
            id_penyakit = []

            for k in arr_penyakit[i]:
                cursor.execute(
                        "SELECT penyakit.nama_penyakit FROM penyakit WHERE id_penyakit = " + str(k))
                id_penyakit.append(cursor.fetchall())

                # list_penyakit.append([i[0] for i in id_penyakit]) 
            # print("id penyakit = ", [i[0] for i in id_penyakit])
            # print("penyakit list = ", flat(list_penyakit))

            for y in id_penyakit:
                for z in y:
                    list_penyakit.append(z[0])
                    new_list_penyakit = ",".join(map("".join, list_penyakit))
            
            # print("z = ", new_list_penyakit)


            # new_list_penyakit = ",".join(map("".join, flat(list_penyakit)))
            penyakit_join_list = [new_list_penyakit]
            # print("new list penyakit = ", penyakit_join_list)

            # print(gj)
            name_gejala = [item.split(" ") for item in arr_gejala]
            # print("old = ", arr_gejala)
            gj = [element for sub in name_gejala for element in sub]
            # print("gj = ", gj)

            stopwords = get_stopword('file/konjungsi.csv')
            filters = filtering(gj, stopwords)
            stems = stemming(filters)
            sinonim = get_sinonim(stems)
            result, cf = get_cf(conn, sinonim)

            list_gj = ",".join(map("".join, arr_gejala))
            list = [list_gj]

            # print("result = ", list)
            data = [result[0][0][1]]
            # print("data = ", data)
            nilai_cf = [cf]
            # print("nilai cf = ", nilai_cf)
            # print("array penyakit ke-i = ", arr_penyakit[i])
            zips = zip(list, penyakit_join_list, data, nilai_cf)
            newfilepath = 'testing_kombinasi_same.csv'

            with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
                writer = csv.writer(f, delimiter=";")
                for row in zips:
                    tmp = row
                    writer.writerow(tmp)

    return zips

def combination_other(penyakit):
    arr_penyakit = []

    comb_penyakit = itertools.combinations(penyakit, 2)
    for cb in comb_penyakit:
        tuple_comb = [element for tupl in cb for element in tupl]  # convert tuple of tuple to list
        arr_penyakit.append(tuple_comb)

    for i in range(len(arr_penyakit)):
        list_gj = []
        arr_gejala = []

        for j in arr_penyakit[i]:
            cursor.execute(
                "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(
                    j))
            id_gejala = cursor.fetchall()

            list_gj.append([i[0] for i in id_gejala])  # convert list of tuple to list

        # print("penyakit = ", arr_penyakit[i])
        # compare list 1 dan list 2
        for x in range(len(list_gj[0])):
            for y in range(len(list_gj[1])):
                if list_gj[0][x] == list_gj[1][y]:
                    arr_gejala.append(list_gj[0][x])

        if len(arr_gejala) >= 2:
            # print("arr_gejala = ", arr_gejala)

            list_othergj = []

            # baru tambahkan id penyakit
            new_list_penyakit = []
            list_penyakit = []
            id_penyakit = []

            for k in arr_penyakit[i]:
                cursor.execute(
                        "SELECT penyakit.nama_penyakit FROM penyakit WHERE id_penyakit = " + str(k))
                id_penyakit.append(cursor.fetchall())

                # list_penyakit.append([i[0] for i in id_penyakit]) 
            # print("id penyakit = ", [i[0] for i in id_penyakit])
            # print("penyakit list = ", flat(list_penyakit))

            for l in id_penyakit:
                for j in l:
                    list_penyakit.append(j[0])
                    new_list_penyakit = ",".join(map("".join, list_penyakit))
            
            # print("z = ", new_list_penyakit)


            # new_list_penyakit = ",".join(map("".join, flat(list_penyakit)))
            penyakit_join_list = [new_list_penyakit]
            # print("new list penyakit = ", penyakit_join_list)

            gejala_same_join = ",".join(map("".join, arr_gejala))
            gejala_same_list = [gejala_same_join]

            # print("gejala same list = ", gejala_same_list)

            for y in arr_penyakit[i]:
                
                cursor.execute(
                    "SELECT gejala.nama_gejala FROM gejala_penyakit JOIN gejala ON gejala_penyakit.id_gejala = gejala.id_gejala WHERE gejala_penyakit.id_penyakit = " + str(y))
                other_gejala = cursor.fetchall()

                list_othergj.append([i[0] for i in other_gejala])
            
            # print("list_other gejala = ", list_othergj)

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
                    # print("gejala gabungan = ", list_comb)

                    stopwords = get_stopword('file/konjungsi.csv')
                    filters = filtering(arr_gj, stopwords)
                    stems = stemming(filters)
                    sinonim = get_sinonim(stems)
                    result, cf= get_cf(conn, sinonim)

                    join_gj = ",".join(map("".join, list_comb))
                    list_gj = [join_gj]

                    # print("result = ", list_gj)
                    data = [result[0][0][1]]
                    # print("data = ", data)
                    nilai_cf = [cf]
                    zips = zip(gejala_same_list, list_gj, penyakit_join_list, data, nilai_cf)
                    newfilepath = 'testing_kombinasiother2.csv'
                    with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
                        writer = csv.writer(f, delimiter=";")
                        for row in zips:
                            tmp = row
                            writer.writerow(tmp)

    return arr_gejala


def remove_duplicate():

    data = []
    with open('testing_kombinasiother2.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile, delimiter=';')
        for r in read_data:
            data.append(r)
    # print("data lama = ", data)

    for i in data:
        string_gj = i[1].split(',')
        sort_gj = sorted(string_gj)

        i[1] = sort_gj

        join_gj = ",".join(map("".join, i[1]))
        i[1] = join_gj

    data2 = set(map(tuple,data))

    newfilepath = 'duplicate_newnew.csv'
    with open(newfilepath, 'a', encoding="ISO-8859-1", newline='') as f:
        writer = csv.writer(f, delimiter=";")
        for row in data2:
            tmp = row
            writer.writerow(tmp)

    print("panjang data2 = ", data2)

    return data

if __name__ == "__main__":
    # get_gejala()
    penyakit = get_penyakit()
    # remove_duplicate()
    get_gejalapenyakit(penyakit)
    # combination_samegejala(penyakit)
    # combination_other(penyakit)
