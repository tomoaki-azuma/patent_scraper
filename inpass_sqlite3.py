#!/usr/bin/env python
# coding: utf-8

# -*- coding: utf-8 -*-
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

def get_detail_data(driver, app_num, cursor, target_id):
    detail_data = []
    try:
      app_num = driver.find_element(By.XPATH, '//*[@id="Content"]/div[2]/div/table[2]/tbody/tr[2]/td[3]').text
      print(app_num)

      cursor.execute('select count(*) from reg_info where app_num = ? and search_id = ?', (app_num, target_id))
      result = c.fetchone()

      if result[0] > 0:
        return ["do nothing"]

      reg_num = driver.find_element(By.XPATH, '//*[@id="Content"]/div[2]/div/table[2]/tbody/tr[1]/td[3]').text
      print(reg_num)
      

      data_trs = driver.find_elements(By.XPATH, '//*[@id="Content"]/div[2]/div/table[3]/tbody/tr')

      for i, tr in enumerate(data_trs):
        if i == 0:
          ths = tr.find_elements(By.XPATH, 'th')
          if ths[1].text != 'Name of Grantee':
            break
          else:
            continue

        tds = tr.find_elements(By.XPATH, 'td')
        garantee_name = tds[1].text
        garantee_address = tds[2].text

        up_data = (app_num, reg_num, garantee_name, garantee_address, target_id)
        detail_data.append(up_data)
      print(detail_data)
      return detail_data
    except Exception as e:
      print(e)
      print('cannot get detail info of :' + app_num)
      return []


if __name__ == '__main__':
  target_id = sys.argv[1]

  conn = sqlite3.connect('inpass.db')
  c = conn.cursor()
  c.execute('select * from target_companies where id = ?', (target_id,))
  result = list(map(lambda m: '"' + m[1] + '"', c.fetchall()))

  if len(result) != 1:
    sys.exit()

  target = result[0]

  print('get data: ' + target)
  
  # ドライバー指定でChromeブラウザを開く
  chrome_service = fs.Service(executable_path="./chromedriver")
  options = webdriver.ChromeOptions()
  options.add_experimental_option('excludeSwitches', ['enable-logging'])
  options.use_chromium = True
  driver = webdriver.Chrome(service=chrome_service, options=options)
  url = 'https://ipindiaservices.gov.in/PublicSearch/PublicationSearch'
  driver.get(url)
  current_html = driver.page_source
  pub_type = driver.find_element(By.ID, 'Granted')
  pub_type.click()

  item_select_element = driver.find_element(By.ID, 'ItemField1')
  item_selector = Select(item_select_element)
  item_selector.select_by_value('PA')
  item = driver.find_element(By.ID,'TextField1')
  item.send_keys(target)
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

      c.execute('select count(*) from reg_info where app_num = ? and search_id = ?', (app_num, target_id))
      result = c.fetchone()

      if result[0] > 0:
         continue
      
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

        detail_data = get_detail_data(driver, app_num, c, target_id)

        if len(detail_data) == 1 and detail_data[0] == "do nothing":
            continue
        elif len(detail_data) > 0:
          conn.executemany('insert into reg_info values(?,?,?,?,?)', detail_data)
          conn.commit()
        elif len(detail_data) == 0:
          conn.execute('insert into reg_info values(?,"NA","NA","NA",?)', (app_num, target_id))
          conn.commit()
      except Exception as e:
        print(e)
        print('error occured：' + app_num)
        conn.execute('insert into reg_info values(?,"NA","NA","NA",?)', (app_num, target_id))
        conn.commit()   
      finally:
        driver.close()
        driver.switch_to.window(handle_array[0])

    next_b = driver.find_element(By.XPATH, '//*[@id="tableData"]/tfoot/tr/td/table/tbody/tr/th[2]/button[3]')
    if next_b.is_enabled():
      next_b.click()
    else:
      conn.close()
      driver.close()
      break

