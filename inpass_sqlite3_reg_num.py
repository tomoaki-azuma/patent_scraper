#!/usr/bin/env python
# coding: utf-8

# -*- coding: utf-8 -*-
import os
import re
import requests
import csv
import sys
import sqlite3
from inpass_sqlite3_applicants import get_detail_data
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

if __name__ == '__main__':

  conn = sqlite3.connect('inpass.db')
  c = conn.cursor()
  c.execute('select reg_num from inpass_application where is_checked = 0')
  regnums = list(map(lambda m: m[0], c.fetchall()))

  if len(regnums) == 0:
    sys.exit()

  regnums = regnums[0:14]
  
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

  for i in range(0,len(regnums)):
    print(i)
    print(regnums[i])
    item_select_element = driver.find_element(By.ID, 'ItemField' + str(i+1))
    item_selector = Select(item_select_element)
    item_selector.select_by_value('patent-number')
    logic_select_element = driver.find_element(By.ID, 'LogicField' + str(i+1))
    logic_selector = Select(logic_select_element)
    logic_selector.select_by_value('OR')
    item = driver.find_element(By.ID,'TextField' + str(i+1))
    item.send_keys(regnums[i])

  input_captcha = input('Enter captcha code: ')
  captcha = driver.find_element(By.ID, 'CaptchaText')
  captcha.send_keys(input_captcha)
  search_btn = driver.find_element(By.XPATH, '//*[@id="home"]/div[18]/div[2]/div/div/div[1]/div[3]/input')
  search_btn.click()

  result = []
  
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
    print('------- '+ total_count + ' -------------')

    up_datas = []
    for t in tabledata:
      # 取得済みかチェック
      app_num = t.find_element(By.XPATH, 'td[1]').text
      
      try:
        print(app_num)
        # リスト一覧から1文献の詳細データをクリック
        button = t.find_element(By.XPATH,'td[5]/button')
        button.click()

        handle_array = driver.window_handles
        # pop up windowに切り替え
        driver.switch_to.window(handle_array[1])

      
        WebDriverWait(driver, 30).until(
          ec.presence_of_element_located((By.ID, "Content"))
        )

        detail_data = get_detail_data(driver, app_num, c)

        patentee_results = detail_data[0]
        conn.executemany('insert into inpass_result(app_num, reg_num, patentee_sl, patentee, patentee_address) values(?,?,?,?,?)', patentee_results)
        conn.commit()
        
        remark_results = detail_data[1]
        conn.executemany('insert into remarks(app_num, reg_num, sequence, date_of_entry, remark) values(?,?,?,?,?)',  remark_results)
        conn.commit()

        renewal_resluts = detail_data[2]
        conn.execute('insert into renewal(app_num, reg_num, year, normal_due_date, due_date_with_extension, cbr_no, cbr_date, renewal_amount, renewal_certificate_no, date_of_renewal, renewal_period_from, renewal_period_to) values(?,?,?,?,?,?,?,?,?,?,?,?)',  renewal_resluts)
        conn.commit()

        conn.execute('update inpass_application set is_checked = 1 where reg_num = ?' , (patentee_results[0][1],))
        conn.commit()
        regnums.remove(patentee_results[0][1])

      except Exception as e:
        print(e)
        print('error occured：' + app_num) 
      finally:
        driver.close()
        driver.switch_to.window(handle_array[0])

    next_b = driver.find_element(By.XPATH, '//*[@id="tableData"]/tfoot/tr/td/table/tbody/tr/th[2]/button[3]')
    if next_b.is_enabled():
      next_b.click()
    else:
      print('cannot get data of ', regnums)
      for regnum in regnums:
        conn.execute('update inpass_application set is_checked = -1 where reg_num = ?' , (regnum,))
        conn.commit()
      conn.close()
      driver.close()
      break

