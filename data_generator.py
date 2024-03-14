import os
import re
import requests
import csv
import sys
import sqlite3
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome import service as fs
import pickle
from selenium.webdriver.chrome.options import Options # オプションを使うために必要

all_results = []

conn = sqlite3.connect('inpass.db')
c = conn.cursor()
c.execute('select app_num, reg_num, patentee_sl, patentee, patentee_address from inpass_result order by reg_num')
inpass_results = c.fetchall()

for result in inpass_results:
  reg_num = result[1]

  result_list = list(result)

  c.execute('select remark from remarks where reg_num = ?', (reg_num,))
  remarks = c.fetchall()

  for remark in remarks:
    result_list.append(remark[0])
  
  for i in range(4-len(remarks)):
    result_list.append("  ")
  
  c.execute('select * from renewal where reg_num = ?', (reg_num,))
  renewal = c.fetchall()
  if (len(renewal) > 0):
    renewal_data = renewal[0]
    result_list += [renewal_data[2], renewal_data[10], renewal_data[11]]

  all_results.append(result_list)

with open('scraping_results.tsv', 'w', newline='') as f:
  writer = csv.writer(f, delimiter='\t')
  writer.writerows(all_results)

conn.close()