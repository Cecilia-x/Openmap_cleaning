#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module is to collect tags with keys that probably contain problem chars.
It will examin each tag key in each element. If one tag key contain problem chars
or have colon but not fit the pattern, then get all the tags.
The output will like:
{ "3914359053": [{"gns:": "30"}, {"bad chars": "value"], 
  "4233934741": [{"gns:UFI": "1910877"}]
 ...} 
'''

import json
import audit
import codecs
import re


OSM_PATH = "sample.osm"
OUTPUT = "view_problem_keys.json"


LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-zA-Z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

get_element = audit.get_element

def key_filter(key):
    if re.match(PROBLEMCHARS,key) != None:
        return True
    elif key.find(':') != -1 and re.match(LOWER_COLON,key) == None:
        return True
    else:
        return False

def collect(filename, is_toget, tags=('node', 'way')):
    result = {}
    for element in get_element(OSM_PATH, tags):
        e_id = element.attrib['id']
        toget = False
        if element.findall('tag') != None:
            tags = []
            for tag_e in element.findall('tag'):
                k = tag_e.attrib['k']
                tags.append({k:tag_e.attrib['v']})
                if is_toget(k):
                    toget = True
            if toget:
                result[e_id] = tags
    return result
            

if __name__ == '__main__':
    d = collect(OSM_PATH, key_filter)
    with codecs.open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
