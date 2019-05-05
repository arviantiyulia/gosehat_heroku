def save_input(user_id, name_user, inputs, input_user, timestamp, conn):
    cursor = conn.cursor()

    for i in range(len(inputs)):
        cursor.execute(
            "INSERT INTO gejala_input(user_id, nama_user, nama_gejala, input_user, time) VALUES('" + user_id + "', '" + name_user + "','" +
            inputs[i][0][1] + "', '" + input_user + "' , '" + str(timestamp) + "')")
        conn.commit()

    return inputs


def flat(listoflist):
    gejala = []
    
    for item in listoflist:
        if type(item) != list:
            gejala.append(item)
        else:
            for num in item:
                gejala.append(num)
    return gejala


def save_history(user_id, name_user, input, output, daftar_gejala, disease_id, time, conn):
    cursor = conn.cursor()

    # print("INSERT INTO history(user_id, name_user, input_user, output_sistem) VALUES('" + user_id + "', '" + name_user + "','" + input + "','" + output + "')")
    cursor.execute(
        "INSERT INTO history(user_id, name_user, input_user, output_sistem, daftar_gejala, id_penyakit, time) VALUES('" + user_id + "', '" + name_user + "','" + input + "','" + output + "','" + daftar_gejala + "','" + str(disease_id) + "','" + str(time) + "')")
    conn.commit()

    return user_id

def save_menuinformasi(user_id, name_user, text, conn):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id_user = '" + user_id + "'")
    print("INSERT INTO menu(id_user, nama_user, status) VALUES('" + user_id + "', '" + name_user + "','" + text + "')")
    cursor.execute("INSERT INTO menu(id_user, nama_user, status) VALUES('" + user_id + "', '" + name_user + "','" + text + "')")
    conn.commit()

    return user_id

def save_menukonsultasi(user_id, name_user, text, conn):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id_user = '" + user_id + "'")
    print("INSERT INTO menu(id_user, nama_user, status) VALUES('" + user_id + "', '" + name_user + "','" + text + "')")
    cursor.execute("INSERT INTO menu(id_user, nama_user, status) VALUES('" + user_id + "', '" + name_user + "','" + text + "')")
    conn.commit()

    return user_id

def delete_menukonsultasi(user_id, conn):
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id_user = '" + user_id + "'")
    conn.commit()
