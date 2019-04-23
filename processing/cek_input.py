# Fungsi untuk cek total gejala input dari user
def cek_total_gejala(gejala):

    if len(gejala) == 0:
        return "kosong"
    # TODO: cek if jika rows (gejala) kurang dari sama dengan 3 return text kurang
    elif len(gejala) <= 3:
        return "kurang"
    else:
        return "ada"

def cek_total_penyakit(conn, sinonim):

    cursor = conn.cursor()

    rows = []

    for sinonim in sinonim:
        cursor.execute("SELECT * FROM penyakit WHERE nama_penyakit LIKE '%" + sinonim + "%'")
        rows.append(cursor.fetchall())

    print("DEBUG> penyakit = ", rows)
    print("DEBUG> penyakit 0 = ", rows[0])

    if not rows[0]:
        print("benar")
        return 0, None
    else:
        return len(rows), rows


def isListEmpty(inList):
    if isinstance(inList, list): # Is a list
        return all( map(isListEmpty, inList) )
    return False # Not a list
