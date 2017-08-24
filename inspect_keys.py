#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
this module is to inspect keys, expecially keys with colon.
'''

import audit
import re
import json
import codecs


OSM_PATH = "sample.osm"
OUTPUT = "inspect_keys.json"

get_element = audit.get_element
LOWER_COLON = audit.LOWER_COLON

'''
The function parse key values to dictionary.
If a key does not have colon, it'll be added to 'non-colon' dictionary.
If has colon, it will be splited into 2 parts as type and key.
Then it will be sorted by type.
'''
def sort_keys(filename):
    result = {'non-colon':{}}
    for element in get_element(OSM_PATH, tags=('tag')):
        k = element.attrib['k']
        if k.find(':') != -1:
            klist = k.split(':',1)
            if result.has_key(klist[0]):
                if result[klist[0]].has_key(klist[1]):
                    result[klist[0]][klist[1]] += 1
                else:
                    result[klist[0]][klist[1]] = 1
            else:
                result[klist[0]] = {klist[1] : 1}
        else:
            if result['non-colon'].has_key(k):
                result['non-colon'][k] += 1
            else:
                result['non-colon'][k] = 1
    return result


if __name__ == '__main__':
    d = sort_keys(OSM_PATH)
    with codecs.open(OUTPUT,'w',encoding='utf-8') as f:
        json.dump(d,f,indent=1,ensure_ascii=False)
