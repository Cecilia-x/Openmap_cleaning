#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import audit
import codecs

OSM_PATH = "sample.osm"
OUTPUT = "values_inspect.json"

get_element = audit.get_element
TARGET = ['start_date', 'phone', 'level', 'tunnel', 'oneway']

'''
This module is to closer inspect the values of certain tags.
For each tag with key value in 'target' list, collect and write JSON file.
'''
def collect(filename,target=TARGET,tags=('tag')):
    result = {}
    for i in target:
        result[i] = {}
    for element in get_element(OSM_PATH,tags):
        k = element.attrib['k']
        if k in target:
            v = element.attrib['v']
            if result[k].has_key(v):
                result[k][v] += 1
            else:
                result[k][v] = 1
            
    return result

if __name__ == '__main__':
    collection = collect(OSM_PATH, TARGET)
    with codecs.open(OUTPUT, 'w',encoding='utf-8') as f:
        json.dump(collection,f,indent=1, ensure_ascii=False)
    
    
