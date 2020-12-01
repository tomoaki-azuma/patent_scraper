#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-
import os
import re
import requests
import csv
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pickle

idx = int(input())

applicants = [
  'Toyota Motor*',
  'Toyota jidosha*',
  'Toyota jidousha*',
  'Nissan Motor*',
  'Mitsubishi jidosha*',
  'Mazda',
  'Subaru',
  'Daihatsu Motor*',
  'Honda Motor*',
  'Suzuki Motor*',
  'Yamaha Motor*',
  'Kawasaki Heavy Industries*'
  'Isuzu Motors*',
  'Hino Motors*',
  'Mitsubishi Fuso Truck and Bus*',
  'UD Trucks*',
  'Volvo Trucks*',
  'Hyundai Motor*',
  'Mahindra & Mahindra*',
  'Tata Motors*',
  'General Motors*',
  'Volkswagen',
  'Ford Motor*',
  'Fiat Chrysler Automobiles*',
  'Bayerische Motoren Werke*'
 ]

print('get data: ' + applicants[idx])

driver = webdriver.Chrome('./chromedriver')
url = 'https://ipindiaservices.gov.in/PublicSearch/PublicationSearch'
driver.get(url)
current_html = driver.page_source
fromdate = driver.find_element_by_id('FromDate')
fromdate.send_keys('01/01/2010')
todate = driver.find_element_by_id('ToDate')
todate.send_keys('12/31/2019')

item_select_element = driver.find_element_by_id('ItemField1')
item_selector = Select(item_select_element)
item_selector.select_by_value('PA')
item = driver.find_element_by_id('TextField1')
item.send_keys(applicants[idx])

result = []

def get_detail_data(driver):
    current_data = {}
     
    data_trs = driver.find_elements_by_xpath('//*[@id="Content"]/div[1]/table/tbody/tr')
    for tr in data_trs:
        tds = tr.find_elements_by_xpath('td')
        if tds:
          current_data[tds[0].text] = tds[1].text

    status = driver.find_elements_by_xpath('//*[@id="Content"]/div[2]/table/tbody/tr[2]/td[2]/h3/strong')
    if status:
      current_data['APPLICATION STATUS'] = status[0].text
    # ViewDocument Button
    view_b = driver.find_elements_by_xpath('//*[@id="Content"]/div[2]/form/table/tbody/tr/td[4]/input')
    
    if view_b:
      view_b[0].click()

      try:
        WebDriverWait(driver, 100).until(
          ec.presence_of_element_located((By.ID, "Content"))
        )
      except TimeoutException:
          driver.quit()
          exit('Error:ViewDocumentsに失敗しました')

      data_trs = driver.find_elements_by_xpath('//*[@id="Content"]/form/table/tbody/tr')

      document_name  = ''
      for tr in data_trs:
          tds = tr.find_elements_by_xpath('td')
          if tds:
            document_name += tds[0].text + ' ' + tds[1].text + '\n'
            #print(tds[0].text + ':' + tds[1].text)
      
      current_data['Document Name'] = document_name

    result.append(current_data)

while True:
  
  try:
    WebDriverWait(driver, 100).until(
      ec.presence_of_element_located((By.ID, "tableData"))
    )
  except TimeoutException:
      driver.quit()
      exit('Error:ログインに失敗しました')
  tabledata = driver.find_elements_by_xpath('//*[@id="tableData"]/tbody/tr')

  for t in tabledata:
      
      # リスト一覧から1文献の詳細データをクリック
      n = t.find_element_by_xpath('td[1]').text
      print(n)
      button = t.find_element_by_xpath('td[5]/button')
      button.click()

      handle_array = driver.window_handles
      # pop up windowに切り替え
      driver.switch_to.window(handle_array[1])
      try:
        WebDriverWait(driver, 100).until(
          ec.presence_of_element_located((By.ID, "Content"))
        )
        get_detail_data(driver)

        driver.close()
      except:
          #driver.quit()
          #exit('Error:詳細の取得に失敗しました')
          print('エラーが発生：' + n)
          with open('inpass.log', mode='a') as f:
            f.write(n +'\n')

      driver.switch_to.window(handle_array[0])

  
  next_b = driver.find_element_by_xpath('//*[@id="tableData"]/tfoot/tr/td/table/tbody/tr/th[2]/button[3]')
  if next_b.is_enabled():
    next_b.click()
  else:
    break

with open('inpass_'+str(idx) +'.binaryfile','wb') as pc:
  pickle.dump(result , pc)


# def get_page_links(url):
#     res = requests.get(url)
#     soup = BeautifulSoup(res.text, "html.parser")
# # 記事見出しからリンクを取得
#     elements = soup.select('#main-content .headline a')
#     for element in elements:
#         href = element.get('href')
#         print(href)
#         img_url = get_img_url(href)
#         gender = get_gender(img_url[0])
#         # print(gender)
#         dest_urls.append(['wp', href, img_url[0], img_url[1], gender])
#         sleep(3)


# # In[4]:


# def get_img_url(article_url):
#     res = requests.get(article_url)
#     soup = BeautifulSoup(res.text, "html.parser")
#     ogimg = soup.find('meta', attrs={'property': 'og:image', 'content': True})
#     pubdate = soup.find(
#         'meta', attrs={'name': 'last_updated_date', 'content': True})
#     return [ogimg['content'], pubdate['content']]


# In[5]:


# dest_urls = []
# driver.get(url)
# # 「Load More」ボタン
# element = driver.find_element_by_xpath('//*[@id="f03lcGQypZug4s"]')
# actions = ActionChains(driver)
# # 「さらに読み込む」の下
# target = driver.find_element_by_xpath(
#     '//*[@id="c08YHcSypZug4s"]/div[1]/div[2]/div')

# while True:
#     element.click()
#     # 「さらに読み込む」ボタンを画面に表示させておく
#     actions.move_to_element(target).perform()
#     sleep(2)

#     html = driver.page_source
#     if current_html != html and element.is_displayed() == True:
#         current_html = html
#     else:
#         break


# In[6]:


# get_page_links(url)
# sleep(2)
# print(get_page_links)


# # In[7]:


# with open('wp_economics.csv', 'w', newline="") as f:
#     writer = csv.writer(f)
#     writer.writerows(dest_urls)
