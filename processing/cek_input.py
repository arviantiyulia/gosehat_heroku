# Fungsi untuk cek total gejala input dari user
def cek_total_gejala(gejala):
    if len(gejala) == 0:
        return "kosong"
    # TODO: cek if jika rows (gejala) kurang dari sama dengan 3 return text kurang
    elif len(gejala) <= 2:
        return "kurang"
    else:
        return "ada"


def isListEmpty(inList):
    if isinstance(inList, list): # Is a list
        return all( map(isListEmpty, inList) )
    return False # Not a list
