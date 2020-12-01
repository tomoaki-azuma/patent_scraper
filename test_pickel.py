import pickle
import csv

title = [
    'APPLICATION NUMBER',
    'APPLICATION TYPE',
    'DATE OF FILING',
    'APPLICANT NAME',
    'TITLE OF INVENTION',
    'FIELD OF INVENTION',
    'PCT INTERNATIONAL APPLICATION NUMBER',
    'PCT INTERNATIONAL FILING DATE',
    'PRIORITY DATE',
    'REQUEST FOR EXAMINATION DATE',
    'PUBLICATION DATE (U/S 11A)',
    'FIRST EXAMINATION REPORT DATE',
    'Date Of Certificate Issue',
    'POST GRANT JOURNAL DATE',
    'REPLY TO FER DATE',
    'APPLICATION STATUS',
    'Document Name'
]

result = []

with open('inpass_4.binaryfile', 'rb') as pk:
    data = pickle.load(pk)
    for d in data:
        temp = []
        for t in title:
            if t in d:
                temp.append(d[t])
            else:
                temp.append('')
        result.append(temp)


with open('out.csv', 'w', encoding='shift-jis', newline='') as f:
    dataWriter = csv.writer(f)
    dataWriter.writerow(title)
    dataWriter.writerows(result)

    