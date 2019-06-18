import csv

def get_sinonim(inputs):
    """
    fungsi ini digunakan untuk mencari sinonim dari gejala yang didapat dari input user
    :param inputs: inputan user berupa gejala
    :return: list sin_input yang berisi daftar gejala yang baru dari hasil sinonim
    """
    sinonims = []
    sin_inputs = []

    with open('file/sinonim.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile)
        for r in read_data:
            sinonims.append(r)

    total_index = -1

    found = False
    for idx_input, input in enumerate(inputs):
        if idx_input <= total_index: #digunakan untuk mengecek jika indexnya kurang dari index yang dicari
            continue
        else:
            for index in range(len(sinonims)):
                if input in sinonims[index][1]:
                    panjang_sinonim = len(sinonims[index][1].split(" "))
                    index_input = inputs[idx_input:panjang_sinonim+idx_input]
                    join_input = ' '.join(index_input)

                    if join_input == sinonims[index][1]:
                        found = True
                        sin_inputs.append(sinonims[index][0])
                        total_index = idx_input + (panjang_sinonim - 1) #
                        break
                    else:
                        found = False

                else:
                    found = False

            if found == False:
                sin_inputs.append(input)


    print("DEBUG> sinonim = ", sin_inputs)
    return sin_inputs
