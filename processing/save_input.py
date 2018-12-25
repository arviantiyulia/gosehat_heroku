def save_input(user_id, name_user, inputs, conn):
    cursor = conn.cursor()

    for i in range(len(inputs)):
        cursor.execute("INSERT INTO gejala_input(user_id, nama_user, nama_gejala) VALUES('"+str(user_id)+"', '"+name_user+"','"+inputs[i]+"')")
        conn.commit()

    return inputs