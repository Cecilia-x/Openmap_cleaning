#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This script is to go through all the tag keys like 'name:languagecode', and inspect
if all language code in the name are in the ISO-639 language standard.
For each outliner founded, collect their values and write to output file.
'''

import json
import audit
import closer_inspect_values as inspect
import codecs
from bs4 import BeautifulSoup as bs

OSM_PATH = "sample.osm"

key_dict = json.load(open('inspect_keys.json','r'))
nametype = set()
for i in ['name','alt_name']:
    for key_lang in key_dict[i].keys():
        nametype.add(key_lang)

iso_1_values = []
iso_3_values = []


html = open('iso-639.html', 'r')
soup = bs(html, 'lxml')
table = soup.find(id='Table')
rows = table.find_all('tr')
for row in rows:
    cells = row.find_all('td')[1:]
    if len(cells) > 4:
        iso_1_values.append(cells[3].string)

with open("iso-639-3_Name_Index_20170217.tab",'r') as f:
    _ = f.readline()
    for line in f.readlines():
        items = line.decode('utf-8').replace('\n','').split(u'	')
        iso_3_values.append(items[0])

is_iso1 = []
is_iso3 = []
outliner = []
for name in nametype:
    if name in iso_1_values:
        is_iso1.append(name)
    elif name in iso_3_values:
        is_iso3.append(name)
    else:
        outliner.append(name)

outliner_keys = []
for i in ['official_name','name','alt_name']:
    for j in outliner:
        outliner_keys.append(':'.join([i,j]))


collect = inspect.collect(OSM_PATH,target=outliner_keys)
with codecs.open('ununiformed_nametype.json','w',encoding='utf-8') as f:
    json.dump(collect,f,ensure_ascii=False,indent=1)
