def inputs_check(conn, inputs):
    cursor = conn.cursor()
    rows = []

    for i in inputs:
        cursor.execute("SELECT * FROM gejala WHERE nama_gejala LIKE '%" + i + "%'")
        rows.append(cursor.fetchall())

    if isListEmpty(rows) == True:
        return "kosong"
    else:
        return "ada"

def isListEmpty(inList):
    if isinstance(inList, list): # Is a list
        return all( map(isListEmpty, inList) )
    return False # Not a list