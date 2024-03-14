import csv
import sqlite3

conn = sqlite3.connect('inpass.db')
c = conn.cursor()

data = []
with open('source_no.csv', 'r', newline='') as f:
  csvreader = csv.reader(f)
  for row in csvreader:
    data.append([row[2],row[1]])

conn.executemany('update inpass_application set app_num = ? where reg_num = ?', data)
conn.commit()
conn.close()