gejala = []


def save_input(user_id, name_user, inputs, conn):
    cursor = conn.cursor()

    for i in range(len(inputs)):
        cursor.execute(
            "INSERT INTO gejala_input(user_id, nama_user, nama_gejala) VALUES('" + user_id + "', '" + name_user + "','" +
            inputs[i] + "')")
        conn.commit()

    return inputs


def flat(listoflist):
    for item in listoflist:
        if type(item) != list:
            gejala.append(item)
        else:
            for num in item:
                gejala.append(num)
    return gejala


def save_history(user_id, name_user, input, output, conn):
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO history(user_id, name_user, input_user, output_sistem) VALUES('" + user_id + "', '" + name_user + "','" + input + "','" + output + "')")
    conn.commit()

    return user_id
