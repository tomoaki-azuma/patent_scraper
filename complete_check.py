import sqlite3

conn = sqlite3.connect('inpass.db')
c = conn.cursor()

c.execute('select * from source_applicants where is_complete = 0')
applicants = list(map(lambda m: m[0],  c.fetchall()))

for applicant in applicants:
  if applicant is None:
    continue
  c.execute('select count(*) from inpass_application where grantee = ? and is_checked = 1', (applicant,))
  result = c.fetchone()
  checked_count = result[0]

  c.execute('select count from source_applicants where company_name = ?', (applicant,))
  count = c.fetchone()
  total = count[0]

  print(applicant + " : " + str(checked_count) + "/" + str(total))

  if (checked_count == total):
    print(applicant + " is completed !")
    conn.execute('update source_applicants set is_complete = ? where company_name = ?', (checked_count, applicant,))
    conn.commit()
  



