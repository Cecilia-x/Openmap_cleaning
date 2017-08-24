#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import schema
import json


OSM_PATH = "sample.osm"
LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

KEY_TYPE_DICT = schema.schema



'''
The following functions are used to inspect validation of data.
Main function 'validate' will print out the insepct results like:
======= Example =======
checked ## spot or way nodes.
found ## validation problems:
[['unfit type (integer)', 'abc'],
 ['unfit type (float)', 'abc'],
 [...]]
 
'''

def validate(filename):
    #Check the validity of data. If data type doesn't meet the need of scheme,
    #it will be printed out. 
    
    process_nodes = 0
    problems = []
    for element in get_element(OSM_PATH):
        process_nodes += 1
        element_problem = inspect_node(element)
        if element_problem != None:
            problems.append(element_problem)
        if element.findall('tag') != None:
            for tag_e in element.findall('tag'):
                problem = inspect_tag(tag_e)
                if problem != None:
                    problems.append(problem)
        if element.tag == 'way' and element.findall('nd') != None:
            for nd_e in element.findall('nd'):
                problem = inspect_nd(nd_e)
                if problem != None:
                    problems.append(problem)
                
    print "checked " + str(process_nodes) + " spot or way nodes."
    print 'found ' + str(len(problems)) + ' validation problems: '
    pprint.pprint(problems)
    
                    
def inspect_node(element):
    schema_dict = schema.schema[element.tag]['schema']
    attr = element.attrib
    for field in schema_dict:
        type_requirment = schema_dict[field]['type']
        try:
            value = attr[field]
            if type_requirment in ['integer', 'float']:
                if type_requirment != check_int_float(value):
                    return ['unfit type ({})'.format(type_requirment), value]
        except KeyError:
            return ['field not exist: {}'.format(field), '']


    
def inspect_tag(tag_element):
    try:
        k = tag_element.attrib['k']
        v = tag_element.attrib['v']
        if re.search(PROBLEMCHARS, k) != None:
            return ['bad chars key', k]
        else:
            return None
    except KeyError:
        return ['key not found',tag_element.attrib]

def inspect_nd(nd_element):
    try:
        ref = nd_element.attrib['ref']
        if check_int_float(ref) != 'integer':
            return ['unfit (should be integer)', ref]
        else:
            return None
    except KeyError:
        return ['ref not found', nd_element.attrib]

'''
The following functions are to inspect the uniformity of tag values.
The main function 'audit_tag_value' inspect every tag element and return a
dictionary, mapping tag key and types of data of it's value, like:
======= Example =======
{
 "layer": [
  "integer", 
  "string"
 ],
 "maxspeed": [
  "integer", 
  "string"
 ]}

'''

def audit_tag_value(filename=OSM_PATH):    
    type_dict = inspect_value_types(filename)
    result = multi_types_filter(type_dict)
    return result


def inspect_value_types(filename):
    # Inspect each tag element, collect the type of data of each key.
    # Return the mapping of key of it's value types like:
    # {key_1: ([string]); key_2: ([string, integer]); ... }
    
    value_types = {}
    
    for element in get_element(filename,tags = ('tag')):
        k = element.attrib['k']
        v_type = check_int_float(element.attrib['v'])
        try:
            value_types[k].add(v_type)
        except KeyError:
            value_types[k] = set()
            value_types[k].add(v_type)
    return value_types

def multi_types_filter(value_types):
    # Filter value-type mapping, return keys with more than 1 value types.
    # Result like: {key_1: [string, integer]; key_2: [integer, float]; ... }
    
    result = {}
    for i in value_types:
        if len(value_types[i]) > 1:
            result[i] = list(value_types[i])
    return result

'''
To know if there is a real uniformity problem with those tag values have
more than 1 value types, the functions below will go through the data again
and collect sample of values sorted by types.
'''


def get_multi_type_values(d, filename=OSM_PATH):
    '''
    # The function take 1 dictionary argument, this dictionary should
    # contain keys and their coordinate keytypes, like:
    {
     "layer": ["integer", "string"],
     "maxspeed": ["integer", "string"]
     }
    '''
    result = {}
    keys_to_get = d.keys()
    for key in d:
        result[key] = {}
        for t in d[key]:
            result[key][t] = []
    for element in get_element(filename,tags = ('tag')):
        k = element.attrib['k']
        if k in keys_to_get:
            v = element.attrib['v']
            v_type = check_int_float(v)
            if len(result[k][v_type]) < 10:
                result[k][v_type].append(v)
    
    return result

def view_colon_values():
    d = {}
    for k in key_with_colon:
        klist = k.split(":",1)
        try:
            d[klist[0]].append(klist[1])
        except KeyError:
            d[klist[0]] = []
            d[klist[0]].append(klist[1])
    pprint.pprint(d)

def collect_addrss(tag_ele):
    atts = tag_ele.attrib
    k = atts['k']
    v = atts['v']
    if k[:4] == "addr":
        address.append(v)

def get_element(osm_file, tags=('node', 'way')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

'''
These are helper funcions.
'''
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def open_zip(datafile):
    with ZipFile(datafile, 'r') as myzip:
        myzip.extractall()
        
def write_list(somelist, filename):
    with open(filename, 'w') as f:
        for i in somelist:
            f.writelines((i + '\n').encode('utf-8'))

def check_int_float(value):
    try:
        int_value = float(value)
        try:
            float_value = int(value)
            return 'integer'
        except ValueError:
            return 'float'
    except ValueError:
        return 'string'
            

def get_problem_values(tagvalue_types_dict):
    values = audit_values()
    problem_keys = []
    results = {}
    
    for k in values:
        if len(values[k]) > 1:
            problem_keys.append(k)
    for i in problem_keys:
        results[i] = set()
    for element in get_element(OSM_PATH):
        if element.findall('tag') != None:
            for tag_e in element.findall('tag'):
                kvalue = tag_e.attrib['k']
                if kvalue in problem_keys:
                    results[kvalue].add(tag_e.attrib['v'])
    return results
    


if __name__ == '__main__':    
    validate(OSM_PATH)
    tag_types = audit_tag_value()
    g = get_multi_type_values(tag_types, OSM_PATH)
    
    with codecs.open('tag_types.json','w',encoding='utf-8') as f:
        json.dump(tag_types,f,indent=1, ensure_ascii=False)
    with codecs.open('multi_type_values.json','w',encoding='utf-8') as f:
        json.dump(g,f,indent=1, ensure_ascii=False)
    
    
    
            
