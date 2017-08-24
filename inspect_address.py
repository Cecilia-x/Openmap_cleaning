#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This module is to inspect tags with address key.

'''

import json
import audit
import closer_inspect_values as inspect
import codecs

OSM_PATH = "sample.osm"
OUTPUT = "node_addresses.json"
KEY_FILE = 'inspect_keys.json'

def inspect_address(keyfile=KEY_FILE, filename=OSM_PATH, output=OUTPUT):
    key_dict = json.load(open(keyfile,'r'))
    addr_subkey = key_dict['addr']
    inspect_list = []
    for key in addr_subkey.keys():
        inspect_list.append('addr:' + key)

    collect = inspect.collect(filename,target=inspect_list, tags=('tag'))
    with codecs.open(output,'w',encoding='utf-8') as f:
        json.dump(collect,f,ensure_ascii=False, indent=1)

inspect_address()
