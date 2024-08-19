#!/usr/bin/env python
# coding: utf-8

# -*- coding: utf-8 -*-
import os
import re
import requests
import csv
import sys
import sqlite3
import threading
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


def get_detail_data(driver, app_num, cursor):
    patentee_data = []
    remark_data = []
    renewal_data = []
    try:
      reg_num = ""
      reg_num = driver.find_element(By.XPATH, '//*[@id="Content"]/div[2]/div/table[2]/tbody/tr[1]/td[3]').text
      print(reg_num)

      data_trs = driver.find_elements(By.XPATH, '//*[@id="Content"]/div[2]/div/table[4]/tbody/tr')
      for i, tr in enumerate(data_trs):
        if i == 0:
          ths = tr.find_elements(By.XPATH, 'th')
          if ths[1].text != 'Name of Patentee':
            break
          else:
            continue

        tds = tr.find_elements(By.XPATH, 'td')

        patentee_sl = tds[0].text
        patentee_name = tds[1].text
        patentee_address = tds[3].text

        up_data = (app_num, reg_num, patentee_sl, patentee_name, patentee_address)
        patentee_data.append(up_data)
    
      remark_trs = driver.find_elements(By.XPATH, '//*[@id="Content"]/div[2]/div/table[7]/tbody/tr')

      for i, tr in enumerate(remark_trs):
        if i == 0:
          ths = tr.find_elements(By.XPATH, 'th')
          if ths[0].text != 'Sl No':
            break
          else:
            continue

        tds = tr.find_elements(By.XPATH, 'td')
        serial = tds[0].text
        date_of_entry = tds[1].text
        remarks = tds[2].text

        up_data = (app_num, reg_num, serial, date_of_entry, remarks)
        remark_data.append(up_data)

      renewal_trs = driver.find_elements(By.XPATH, '//*[@id="renual"]/tbody/tr')
      for i, tr in enumerate(renewal_trs):
        tds = tr.find_elements(By.XPATH, 'td')

        if i < 2:
          continue
        if i == 2:
          renewal_data = (list(map( lambda x: x.text, tds)))
        else:
          if tds[1].text != "--":
            renewal_data = (list(map( lambda x: x.text, tds)))
      
      renewal_data = [app_num, reg_num] + renewal_data

      legal_status = ""
      status_date = ""
      print("--------show regal status -------")
      legal_status_trs = driver.find_element(By.XPATH, '//*[@id="Content"]/div[2]/div/table[1]/tbody/tr[2]/td[1]')
      legal_status = legal_status_trs.text.strip()
      print(legal_status)

      if legal_status != "":
        status_date = driver.find_element(By.XPATH, '//*[@id="Content"]/div[2]/div/table[1]/tbody/tr[2]/td[2]')
        status_date = status_date.text.strip()
        print(status_date)

      legal_status_info = (legal_status, status_date)

      return [patentee_data, remark_data, renewal_data, legal_status_info]
    except Exception as e:
      print(e)
      print('cannot get detail info of :' + app_num)
      return []

def getInpassData(applicants):
  conn = sqlite3.connect('inpass.db')
  c = conn.cursor()
# ドライバー指定でChromeブラウザを開く
  chrome_service = fs.Service(executable_path="./chromedriver")
  options = webdriver.ChromeOptions()
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  options.use_chromium = True
  options.add_argument('--incognito')
  driver = webdriver.Chrome(service=chrome_service, options=options)
  url = 'https://iprsearch.ipindia.gov.in/publicsearch'
  driver.get(url)

  current_html = driver.page_source
  pub_type = driver.find_element(By.ID, 'Granted')
  pub_type.click()

  for i in range(0,len(applicants)):
    item_select_element = driver.find_element(By.ID, 'ItemField' + str(i+1))
    item_selector = Select(item_select_element)
    item_selector.select_by_value('PA')
    logic_select_element = driver.find_element(By.ID, 'LogicField' + str(i+1))
    logic_selector = Select(logic_select_element)
    logic_selector.select_by_value('OR')
    item = driver.find_element(By.ID,'TextField' + str(i+1))
    item.send_keys(applicants[i])

  input_captcha = input('Enter captcha code: ')
  captcha = driver.find_element(By.ID, 'CaptchaText')
  captcha.send_keys(input_captcha)
  search_btn = driver.find_element(By.XPATH, '//*[@id="home"]/div[18]/div[2]/div/div/div[1]/div[3]/input')
  search_btn.click()

  result = []
  current = 0
  PER_PAGE = 25
  
  while True:
    try:
      WebDriverWait(driver, 100).until(
        ec.presence_of_element_located((By.ID, "tableData"))
      )
    except TimeoutException:
        driver.quit()
        exit('Error:ログインに失敗しました')
    tabledata = driver.find_elements(By.XPATH, '//*[@id="tableData"]/tbody/tr')

    total_count = driver.find_element(By.XPATH, '//*[@id="header"]/div[4]/div/div[1]/div[2]').text
    print('------- '+ str(current*PER_PAGE+1) + '-' + str(current*PER_PAGE+len(tabledata)) + '/' + total_count + ' -------------')

    up_datas = []
    for t in tabledata:
      # 取得済みかチェック
      app_num = t.find_element(By.XPATH, 'td[1]').text

      c.execute('select count(*) from inpass_application where app_num = ? and is_checked = ?', (app_num, 0))
      result = c.fetchone()
      if result[0] == 0:
        continue
      
      try:
        print(app_num)
        button = t.find_element(By.XPATH,'td[5]/button')
        button.click()
  
        handle_array = driver.window_handles
        # pop up windowに切り替え
        driver.switch_to.window(handle_array[1])

      
        WebDriverWait(driver, 30).until(
          ec.presence_of_element_located((By.ID, "Content"))
        )

        detail_data = get_detail_data(driver, app_num, c)
        if get_detail_data == []:
          continue

        patentee_results = detail_data[0]
        conn.executemany('insert into inpass_result(app_num, reg_num, patentee_sl, patentee, patentee_address) values(?,?,?,?,?)', patentee_results)
        conn.commit()
        
        remark_results = detail_data[1]
        conn.executemany('insert into remarks(app_num, reg_num, sequence, date_of_entry, remark) values(?,?,?,?,?)',  remark_results)
        conn.commit()

        renewal_resluts = detail_data[2]
        conn.execute('insert into renewal(app_num, reg_num, year, normal_due_date, due_date_with_extension, cbr_no, cbr_date, renewal_amount, renewal_certificate_no, date_of_renewal, renewal_period_from, renewal_period_to) values(?,?,?,?,?,?,?,?,?,?,?,?)',  renewal_resluts)
        conn.commit()

        conn.execute('update inpass_application set is_checked = 1 where app_num = ?' , (app_num,))
        conn.commit()

        legal_status_info = detail_data[3]
        conn.execute('update inpass_result set legal_status = ?, date_of_status = ? where app_num = ?' , (legal_status_info[0],legal_status_info[1], app_num))
        conn.commit()

      except Exception as e:
        print(e)
        print('error occured：' + app_num) 
      finally:
        driver.close()
        driver.switch_to.window(handle_array[0])

    current += 1
    next_b = driver.find_element(By.XPATH, '//*[@id="tableData"]/tfoot/tr/td/table/tbody/tr/th[2]/button[3]')
    if next_b.is_enabled():
      next_b.click()
    else:

      for applicant in applicants:
        conn.execute('update source_applicants set is_checked = 1 where company_name = ' + applicant)
        conn.commit()

    break
  driver.close()
  conn.close()


if __name__ == '__main__':

  conn = sqlite3.connect('inpass.db')
  c = conn.cursor()
  c.execute('select company_name from source_applicants where is_checked = 0 order by count desc limit 84')
  applicants = list(map(lambda m: '"' + m[0] + '"', c.fetchall()))
  print(applicants)
  conn.close()
  if len(applicants) == 0:
    sys.exit()
  
  thread_array = []
  for i in range(0,4):
    print(applicants[(i*14):(i+1)*14])
    t = threading.Thread(target=getInpassData, args=(applicants[(i*14):(i+1)*14],))
    thread_array.append(t)
  
  for thread in thread_array:
    thread.start()
  
  for thread in thread_array:
    thread.join()