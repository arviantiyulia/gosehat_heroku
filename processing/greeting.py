import csv

def open_csv():
    greeting = []

    with open('file/greeting.csv', 'r') as csvfile:
        read_data = csv.reader(csvfile)

        for r in read_data: #looping tiap baris dari file csv
            greeting.append(r)

    return greeting

def check_greeting(input):
    csv = open_csv()

    save_greeting = ""

    for i in input:
        for j in range(len(csv)):
            if i in csv[j]:
                save_greeting = csv[j][1]
                break;

    if save_greeting == "":
        return "Maaf data yang anda masukkan tidak ada, silahkan masukkan dengan data lain"
    else:
        return save_greeting
